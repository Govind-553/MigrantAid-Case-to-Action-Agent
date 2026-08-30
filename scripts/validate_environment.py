import os
import sys
import json
from pathlib import Path

# Resolve the project root (one directory above this script)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def print_status(check_name: str, passed: bool, message: str = ""):
    status_str = "SUCCESS" if passed else "FAILED"
    print(f"[{status_str}] {check_name}: {message}")


def check_python_version() -> bool:
    major, minor = sys.version_info.major, sys.version_info.minor
    passed = (major == 3 and minor >= 9)
    print_status(
        "Python Version",
        passed,
        f"Detected {sys.version.split()[0]} (Required >= 3.9.0)"
    )
    return passed


def check_env_file() -> bool:
    env_path = PROJECT_ROOT / ".env"
    passed = env_path.exists()
    print_status(
        ".env File Presence",
        passed,
        "Found .env file" if passed else f"No .env file found at {env_path}. Please create one from .env.example"
    )
    return passed


def check_env_variables() -> bool:
    # Load .env from the project root
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)

    required_vars = [
        "LLM_MODEL",
        "DATABASE_URL",
        "APP_ENV"
    ]

    api_key = os.getenv("LLM_API_KEY", "")
    has_api_key = bool(api_key and not api_key.startswith("placeholder"))

    all_passed = True
    for var in required_vars:
        val = os.getenv(var)
        var_passed = bool(val)
        if not var_passed:
            all_passed = False
        print_status(f"Env Variable: {var}", var_passed, f"Value: '{val}'" if var_passed else "Missing")

    print_status(
        "LLM API Key Check",
        has_api_key,
        "API Key is configured" if has_api_key else "API Key is missing or placeholder (set LLM_API_KEY in .env)"
    )

    return all_passed


def check_data_files() -> bool:
    data_dir = PROJECT_ROOT / "data"
    required_files = [
        "evaluation_cases.json",
        "resources.json",
        "sources.json"
    ]

    all_passed = True
    for filename in required_files:
        file_path = data_dir / filename
        exists = file_path.exists()
        if not exists:
            all_passed = False
            print_status(f"Data File Presence: {filename}", False, f"File not found at {file_path}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            print_status(f"Data File & JSON Check: {filename}", True, "Found and valid JSON")
        except json.JSONDecodeError as e:
            all_passed = False
            print_status(f"Data File & JSON Check: {filename}", False, f"JSON parse error: {str(e)}")

    return all_passed


def main():
    print("==================================================")
    print("       MIGRANTAID ENVIRONMENT VALIDATION          ")
    print("==================================================")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    python_ok = check_python_version()
    env_file_ok = check_env_file()
    env_vars_ok = check_env_variables()
    data_ok = check_data_files()

    print()
    print("==================================================")
    if python_ok and env_file_ok and data_ok:
        print("Result: ENVIRONMENT IS VALID")
        print("Note: LLM API key is required for model calls but not for schema/data validation.")
        sys.exit(0)
    else:
        print("Result: ENVIRONMENT VALIDATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
