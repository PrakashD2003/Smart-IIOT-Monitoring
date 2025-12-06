import datetime
import random  # nosec B311
from typing import Any

MACHINE_IDS = ["M1", "M2", "M3", "M4"]


def random_sensor_reading() -> dict[str, float]:
    return {
        "temp": round(random.uniform(50, 85), 2),  # nosec B311
        "speed": round(random.uniform(1000, 2000), 2),  # nosec B311
        "pressure": round(random.uniform(1.0, 6.0), 2),  # nosec B311
        "vibration": round(random.uniform(0.01, 0.25), 4),  # nosec B311
        "torque": round(random.uniform(10, 50), 2),  # nosec B311
        "tool_wear": round(random.uniform(0, 100), 2),  # nosec B311
    }


def simulate_failure_probability(sensor: dict[str, float]) -> float:
    score = 0.0
    score += max(0, (sensor["temp"] - 60) / 40) * 0.4
    score += max(0, (sensor["vibration"] - 0.02) / 0.2) * 0.3
    score += max(0, (sensor["tool_wear"] / 100)) * 0.2
    score += random.uniform(-0.05, 0.05)  # nosec B311
    return max(0, min(1, score))


def get_mock_machines() -> list[dict[str, Any]]:
    machines = []
    for m in MACHINE_IDS:
        sensors = random_sensor_reading()
        fp = simulate_failure_probability(sensors)
        machines.append(
            {
                "id": m,
                "name": f"Machine {m}",
                "status": "OK" if fp < 0.5 else "NEEDS_MAINTENANCE",
                "failure_probability": fp,
                "last_updated": datetime.datetime.utcnow().isoformat(),
            }
        )
    return machines


def get_mock_machine_live(machine_id: str) -> dict[str, Any]:
    sensors = random_sensor_reading()
    fp = simulate_failure_probability(sensors)
    return {
        "machine_id": machine_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "sensor_data": sensors,
        "failure_probability": fp,
    }
