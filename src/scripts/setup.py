#!/usr/bin/env python
"""Setup script - installs dependencies and runs migrations"""
import os
import subprocess
import sys


def run_command(cmd, description):
    print(f"\n=== {description} ===")
    # Add Poetry to PATH
    poetry_path = ""
    env = os.environ.copy()
    env["PATH"] = f"{poetry_path}:{env.get('PATH', '')}"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    if result.stdout:
        print(result.stdout)


def poetry_exists():
    result = subprocess.run("poetry --version", shell=True, capture_output=True)
    return result.returncode == 0

def create_env_file():
    """Create .env with database credentials from host environment"""
    env_content = """
DATABASE_URL=
DATABASE_HOST=
DATABASE_PORT=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_POOL_SIZE=
DATABASE_MAX_OVERFLOW=
DATABASE_POOL_RECYCLE=
DATABASE_POOL_PRE_PING=
DATABASE_ECHO=
"""
    with open(".env", "w") as f:
        f.write(env_content.strip())
    print("Created .env file")

def main():
    # Install Poetry if not present
    if not poetry_exists():
        if sys.platform == "win32":
            run_command(
                '(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -',
                "Installing Poetry"
            )
        else:
            run_command(
                "curl -sSL https://install.python-poetry.org | python3 -",
                "Installing Poetry"
            )
    
    # Create .env file
    create_env_file()

    # Generate poetry lock
    run_command(f"poetry lock", "Updating lock file")
    
    # Install dependencies
    run_command("poetry install --only main", "Installing dependencies")

    # Run migrations
    run_command("poetry run alembic upgrade head", "Running database migrations")

    # Delete .env for security
    if os.path.exists(".env"):
        os.remove(".env")
        print("Removed .env file for security")
    
    print("\n=== Setup complete ===")
    print("Run 'poetry run uvicorn main:app --host 0.0.0.0 --port 8000' to start the app")


if __name__ == "__main__":
    main()