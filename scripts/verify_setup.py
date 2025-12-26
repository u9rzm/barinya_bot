"""Verify project setup and configuration."""
import sys
import os
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} missing: {filepath}")
        return False


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description} missing: {dirpath}")
        return False


def main():
    """Main verification function."""
    print("=" * 60)
    print("Telegram Bar Bot - Setup Verification")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check project structure
    print("Checking project structure...")
    print("-" * 60)
    
    directories = [
        ("bot/", "Bot directory"),
        ("webapp/", "Web app directory"),
        ("webapp/static/", "Static files directory"),
        ("webapp/templates/", "Templates directory"),
        ("shared/", "Shared code directory"),
        ("alembic/", "Alembic directory"),
        ("alembic/versions/", "Alembic versions directory"),
        ("scripts/", "Scripts directory"),
        ("tests/", "Tests directory"),
    ]
    
    for dirpath, description in directories:
        if not check_directory_exists(dirpath, description):
            all_checks_passed = False
    
    print()
    
    # Check configuration files
    print("Checking configuration files...")
    print("-" * 60)
    
    config_files = [
        ("pyproject.toml", "Project configuration"),
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment variables example"),
        ("alembic.ini", "Alembic configuration"),
        ("README.md", "README file"),
    ]
    
    for filepath, description in config_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    print()
    
    # Check core Python files
    print("Checking core Python files...")
    print("-" * 60)
    
    python_files = [
        ("bot/__init__.py", "Bot package init"),
        ("bot/main.py", "Bot main entry point"),
        ("webapp/__init__.py", "Webapp package init"),
        ("webapp/main.py", "Webapp main entry point"),
        ("shared/__init__.py", "Shared package init"),
        ("shared/config.py", "Configuration module"),
        ("shared/database.py", "Database module"),
        ("shared/models.py", "Database models"),
        ("alembic/env.py", "Alembic environment"),
        ("scripts/init_db.py", "Database initialization script"),
        ("tests/__init__.py", "Tests package init"),
        ("tests/conftest.py", "Pytest configuration"),
    ]
    
    for filepath, description in python_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    print()
    
    # Check for migrations
    print("Checking database migrations...")
    print("-" * 60)
    
    versions_dir = Path("alembic/versions")
    migration_files = list(versions_dir.glob("*.py"))
    migration_files = [f for f in migration_files if f.name != "__pycache__"]
    
    if migration_files:
        print(f"✓ Found {len(migration_files)} migration file(s)")
        for migration in migration_files:
            print(f"  - {migration.name}")
    else:
        print("✗ No migration files found")
        all_checks_passed = False
    
    print()
    
    # Check .env file
    print("Checking environment configuration...")
    print("-" * 60)
    
    if Path(".env").exists():
        print("✓ .env file exists")
        print("  Note: Make sure to configure all required variables")
    else:
        print("⚠ .env file not found")
        print("  Run: cp .env.example .env")
        print("  Then edit .env with your configuration")
    
    print()
    print("=" * 60)
    
    if all_checks_passed:
        print("✓ All checks passed! Project setup is complete.")
        print()
        print("Next steps:")
        print("1. Create .env file: cp .env.example .env")
        print("2. Configure .env with your settings")
        print("3. Run migrations: alembic upgrade head")
        print("4. Initialize database: python scripts/init_db.py")
        print("5. Start webapp: python webapp/main.py")
        print("6. Start bot: python bot/main.py")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
