# Poetry Dependency Management Commands

## Initial Setup
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies from pyproject.toml
cd backend
poetry install

# Activate the virtual environment
poetry shell
```

## Development Commands
```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Remove a dependency
poetry remove package-name

# Update all dependencies
poetry update

# Update specific dependency
poetry update package-name

# Show current dependencies
poetry show

# Show dependency tree
poetry show --tree

# Check for outdated packages
poetry show --outdated
```

## Running the Application
```bash
# Start the FastAPI server using Poetry
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or activate the shell first, then run
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Useful Commands
```bash
# Export requirements.txt (if needed for deployment)
poetry export -f requirements.txt --output requirements.txt

# Export without dev dependencies
poetry export -f requirements.txt --output requirements.txt --without dev

# Check virtual environment info
poetry env info

# List virtual environments
poetry env list

# Remove virtual environment
poetry env remove python
```

## Lock File Management
```bash
# Generate/update poetry.lock
poetry lock

# Install from lock file only
poetry install --only-root

# Sync dependencies with lock file
poetry install --sync
```
