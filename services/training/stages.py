"""Leakage-safe ingestion, fitting, validation selection and test evaluation."""

import importlib.metadata
import subprocess
import time
from dataclasses import asdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as TrainingPipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from common.features import (
    NUMERIC_FEATURES,
    RAW_FEATURES,
    SCHEMA_VERSION,
    FeatureEngineer,
)
from common.io import sha256_file, source_hash
from common.versions import package_version
from services.training.contracts import ModelArtifact, SplitArtifact

TARGET = "Machine failure"


def ingest(config):
    data = pd.read_csv(config.data_path)
    required = RAW_FEATURES + [TARGET]
    if not set(required).issubset(data.columns) or data[required].isna().any().any():
        raise ValueError("Dataset has missing required columns or values")
    if set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("Training requires both binary target classes")
    if not data.Type.isin(["L", "M", "H"]).all():
        raise ValueError("Invalid product Type")
    train_val, test = train_test_split(
        data[required],
        test_size=config.test_size,
        random_state=config.seed,
        stratify=data[TARGET],
    )
    train, validation = train_test_split(
        train_val,
        test_size=config.validation_size / (1 - config.test_size),
        random_state=config.seed,
        stratify=train_val[TARGET],
    )
    return SplitArtifact(train, validation, test, sha256_file(config.data_path))


def build_pipeline(name, seed):
    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000, random_state=seed),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, random_state=seed, n_jobs=2
        ),
        "GradientBoosting": GradientBoostingClassifier(random_state=seed),
    }
    if name == "XGBoost":
        from xgboost import XGBClassifier

        model = XGBClassifier(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=4,
            min_child_weight=3,
            subsample=0.85,
            colsample_bytree=0.85,
            scale_pos_weight=28,
            reg_alpha=0.1,
            reg_lambda=1.5,
            gamma=0.1,
            eval_metric="aucpr",
            random_state=seed,
            n_jobs=2,
        )
    else:
        model = models[name]
    prep = ColumnTransformer(
        [
            ("num", RobustScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="error", sparse_output=False),
                ["Type"],
            ),
        ]
    )
    return TrainingPipeline(
        [
            ("eng", FeatureEngineer()),
            ("prep", prep),
            ("sampler", SMOTE(random_state=seed)),
            ("model", model),
        ]
    )


def evaluate(y, scores, threshold):
    labels = scores >= threshold
    return {
        "recall": float(recall_score(y, labels, zero_division=0)),
        "precision": float(precision_score(y, labels, zero_division=0)),
        "f1": float(f1_score(y, labels, zero_division=0)),
        "f2": float(fbeta_score(y, labels, beta=2, zero_division=0)),
        "pr_auc": float(average_precision_score(y, scores)),
        "roc_auc": float(roc_auc_score(y, scores)),
        "accuracy": float(accuracy_score(y, labels)),
        "confusion_matrix": confusion_matrix(y, labels, labels=[0, 1]).tolist(),
        "threshold": float(threshold),
    }


def select_threshold(y, scores, min_precision):
    choices = [evaluate(y, scores, t) for t in np.linspace(0.01, 0.99, 99)]
    eligible = [m for m in choices if m["precision"] >= min_precision]
    if not eligible:
        raise ValueError("No validation threshold satisfies minimum precision")
    return max(
        eligible, key=lambda m: (m["f2"], m["recall"], m["precision"], m["threshold"])
    )


def fit_candidate(name, config, split):
    start = time.perf_counter()
    pipeline = build_pipeline(name, config.seed)
    pipeline.fit(split.train[RAW_FEATURES], split.train[TARGET])
    scores = pipeline.predict_proba(split.validation[RAW_FEATURES])[:, 1]
    metrics = select_threshold(split.validation[TARGET], scores, config.min_precision)
    # Sampler is training-only. Serving needs sklearn plus the winning estimator.
    serving = Pipeline([(n, s) for n, s in pipeline.steps if n != "sampler"])
    return name, serving, metrics, time.perf_counter() - start


def train(config, fit_results=None, split=None, progress=None):
    started = time.perf_counter()
    emit = progress or (lambda stage, **values: None)
    emit(
        "splitting",
        estimator_progress="Stratified split; no estimator fit progress yet",
    )
    split = split if split is not None else ingest(config)
    emit(
        "split_complete",
        split_rows={
            key: len(getattr(split, key)) for key in ("train", "validation", "test")
        },
        completed_candidates=0,
        total_candidates=len(config.candidates),
    )
    if fit_results:
        results = (
            fit_results(config, split, progress=progress)
            if progress
            else fit_results(config, split)
        )
    else:
        results = []
        for name in config.candidates:
            emit(
                "fitting",
                candidate=name,
                estimator_progress="Estimator fit is running; finer progress unavailable",
                workers=[
                    {
                        "id": "local-training-process",
                        "state": "fitting",
                        "processing": None,
                    }
                ],
                active_workers=1,
            )
            result = fit_candidate(name, config, split)
            results.append(result)
            emit(
                "candidate_complete",
                completed_candidates=len(results),
                candidate=name,
                candidate_result={
                    "name": name,
                    "validation": result[2],
                    "fit_seconds": result[3],
                },
                workers=[],
                active_workers=0,
                estimator_progress="Candidate fit and validation threshold selection completed",
            )
    emit(
        "test_evaluation",
        workers=[],
        active_workers=0,
        estimator_progress="Evaluating selected model on untouched challenger test split",
    )
    name, pipeline, validation, _ = max(
        results, key=lambda r: (r[2]["f2"], r[2]["pr_auc"])
    )
    threshold = validation["threshold"]
    test_metrics = evaluate(
        split.test[TARGET],
        pipeline.predict_proba(split.test[RAW_FEATURES])[:, 1],
        threshold,
    )
    git = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=False
    )
    timestamp = datetime.now(timezone.utc)
    metadata = {
        "model_version": timestamp.strftime("%Y%m%dT%H%M%S%fZ")
        + "-"
        + split.data_hash[:8],
        "schema_version": SCHEMA_VERSION,
        "created_at": timestamp.isoformat(),
        "selected_model": name,
        "threshold": threshold,
        "warning_threshold": threshold / 2,
        "score_kind": "uncalibrated_classifier_score",
        "config": asdict(config),
        "data_sha256": split.data_hash,
        "git_commit": git.stdout.strip() or "unavailable",
        "source_sha256": source_hash(),
        "git_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
        "split_seed": config.seed,
        "split_rows": {
            key: len(getattr(split, key)) for key in ["train", "validation", "test"]
        },
        "split_indices": {
            key: getattr(split, key).index.tolist()
            for key in ["train", "validation", "test"]
        },
        "explanation_background": split.train[RAW_FEATURES]
        .sample(min(32, len(split.train)), random_state=config.seed)
        .to_dict(orient="records"),
        "validation": validation,
        "test": test_metrics,
        "candidates": {
            n: {"validation": m, "fit_seconds": seconds} for n, _, m, seconds in results
        },
        "training_seconds": time.perf_counter() - started,
        "versions": {
            n: package_version(n)
            for n in ["numpy", "pandas", "scikit-learn", "joblib", "xgboost"]
        },
    }
    return ModelArtifact(pipeline, metadata)
