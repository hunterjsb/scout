import os
import sys
from pathlib import Path


def load_dotenv(env_file: str = ".env", override: bool = True) -> None:
    """Load variables from .env file into os.environ."""
    # Handle different execution contexts
    env_path = _find_env_file(env_file)

    if not env_path or not env_path.exists():
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse key=value pairs
            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes from value
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

            # Set in environment if override or not already set
            if override or key not in os.environ:
                os.environ[key] = value


def _find_env_file(env_file: str) -> Path:
    """Find .env file in different execution contexts."""
    env_path = Path(env_file)

    # If absolute path or exists in current dir, use it
    if env_path.is_absolute() or env_path.exists():
        return env_path

    # Try current working directory
    cwd_path = Path.cwd() / env_file
    if cwd_path.exists():
        return cwd_path

    # Try parent directories (useful when running modules)
    current_file = Path(__file__)
    for parent in [current_file.parent, current_file.parent.parent]:
        parent_env = parent / env_file
        if parent_env.exists():
            return parent_env

    # Try from sys.path[0] (script directory)
    if sys.path and sys.path[0]:
        script_dir_env = Path(sys.path[0]) / env_file
        if script_dir_env.exists():
            return script_dir_env

    # Default to original path
    return env_path


# Example usage
if __name__ == "__main__":
    # Load .env file
    load_dotenv()

    # Use standard os.environ
    api_key = os.environ.get("API_KEY", "default_key")
    print(f"API_KEY: {api_key}")

    # Check if required var exists
    if "REQUIRED_VAR" not in os.environ:
        print("REQUIRED_VAR not found in environment")
