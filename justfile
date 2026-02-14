# -------------------------------------------------------------------
# DSPy vs LangGraph vs CrewAI — Comparison Project
# -------------------------------------------------------------------

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
set dotenv-load := true

PYTHON_VERSION := "3.11"
export UV_PROJECT_ENVIRONMENT := ".venv"
VENV_PYTHON := "${UV_PROJECT_ENVIRONMENT}/bin/python"

default: help

# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------

help:
	@just --list

# -------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------

# Create venv and install dependencies
install:
	@echo "🔧 Creating virtual environment..."
	uv venv --python {{PYTHON_VERSION}} --clear
	@echo "📦 Installing dependencies..."
	uv sync
	@echo "✅ Setup complete!"

# -------------------------------------------------------------------
# Run pipelines
# -------------------------------------------------------------------

# Run DSPy pipeline (default: Apple)
dspy company="Apple":
	@echo "🧠 Running DSPy pipeline for {{company}}..."
	{{VENV_PYTHON}} -m dspy_impl.run "{{company}}"

# Run LangGraph pipeline (default: Apple)
langgraph company="Apple":
	@echo "🔀 Running LangGraph pipeline for {{company}}..."
	{{VENV_PYTHON}} -m langgraph_impl.run "{{company}}"

# Run CrewAI pipeline (default: Apple)
crewai company="Apple":
	@echo "👥 Running CrewAI pipeline for {{company}}..."
	{{VENV_PYTHON}} -m crewai_impl.run "{{company}}"

# Run all three pipelines on the same company
all company="Apple":
	@echo "🏁 Running all pipelines for {{company}}..."
	just dspy "{{company}}"
	just langgraph "{{company}}"
	just crewai "{{company}}"

# -------------------------------------------------------------------
# Code quality
# -------------------------------------------------------------------

# Auto-fix lint issues
format:
	@echo "🔧 Auto-fixing lint issues..."
	{{VENV_PYTHON}} -m ruff check --fix src
	{{VENV_PYTHON}} -m ruff format src
	@echo "✅ Done!"

# Run tests
test:
	@echo "🧪 Running tests..."
	{{VENV_PYTHON}} -m pytest -vvs tests/

# -------------------------------------------------------------------
# Cleanup
# -------------------------------------------------------------------

# Remove cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned!"