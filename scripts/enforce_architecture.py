# scripts/enforce_architecture.py
import ast
import sys

# 1. Define what is forbidden
FORBIDDEN_FUNCTIONS = {
    "print": 'Production code must use "src.logger" instead of print().'
}

# 2. Define what MUST be imported if you are in 'src/' or 'api/'
# We check if the file imports your custom logger
REQUIRED_MODULES = ["src.logger", "src.exception"]


def check_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filename)
        except SyntaxError:
            return []

    errors = []
    has_logger_import = False

    # Scan the AST
    for node in ast.walk(tree):
        # 1. Check imports
        if isinstance(node, ast.ImportFrom) and node.module:
            if any(req in node.module for req in REQUIRED_MODULES):
                has_logger_import = True

        # 2. Check forbidden functions
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_FUNCTIONS:
                # build the message on multiple lines to satisfy line-length limits
                msg = (
                    f"{filename}:{node.lineno} ❌ Forbidden: "
                    f"{FORBIDDEN_FUNCTIONS[node.func.id]}"
                )
                errors.append(msg)

        # 3. Enforce DetailedException Usage in 'raise'
        # If we see a 'raise' statement, check what is being raised.
        if isinstance(node, ast.Raise):
            if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                # If they raise generic 'Exception' or 'ValueError', warn them
                if node.exc.func.id in [
                    "Exception",
                    "ValueError",
                    "TypeError",
                    "KeyError",
                ]:
                    msg = (
                        f"{filename}:{node.lineno} ⚠️  Anti-Pattern: Raising generic "
                        f"'{node.exc.func.id}'. Wrap it in 'DetailedException(e)' \n"
                        f"or use a custom exception."
                    )
                    errors.append(msg)
    # Logic: If it's a python file in src/ or api/, it SHOULD import the logger
    # (Skipping __init__.py files as they might just expose exports)
    if ("src/" in filename or "api/" in filename) and not filename.endswith(
        "__init__.py"
    ):
        if not has_logger_import:
            # Warning only, effectively (or make it an error if you want to be strict)
            # errors.append(f"{filename} ⚠️  Warning: Does not import 'src.logger'")
            pass

    return errors


def main():
    files = sys.argv[1:]
    all_errors = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        for e in all_errors:
            print(e)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
