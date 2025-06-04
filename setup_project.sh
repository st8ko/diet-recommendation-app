#!/bin/bash

# Diet Recommendation App - Quick Setup Script
# Run this script to set up your development environment

echo "🚀 Setting up Diet Recommendation App development environment..."

# Create project structure
echo "📁 Creating modular project structure..."
mkdir -p src/diet_app/{config,data,models,api,web,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p scripts
mkdir -p requirements

# Create __init__.py files
touch src/__init__.py
touch src/diet_app/__init__.py
touch src/diet_app/config/__init__.py
touch src/diet_app/data/__init__.py
touch src/diet_app/models/__init__.py
touch src/diet_app/api/__init__.py
touch src/diet_app/web/__init__.py
touch src/diet_app/utils/__init__.py
touch tests/__init__.py

# Create requirements files
echo "📦 Setting up requirements..."

# Base requirements
cat > requirements/base.txt << EOF
# Core dependencies
pandas>=2.1.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Web frameworks
fastapi>=0.104.0
streamlit>=1.28.0
uvicorn[standard]>=0.24.0

# Data validation
pydantic>=2.5.0

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0.1
EOF

# Development requirements
cat > requirements/dev.txt << EOF
-r base.txt

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1

# Code quality
black>=23.9.1
flake8>=6.1.0
isort>=5.12.0
mypy>=1.6.1

# Development tools
jupyter>=1.0.0
ipywidgets>=8.1.0
pre-commit>=3.5.0
EOF

# Production requirements  
cat > requirements/prod.txt << EOF
-r base.txt

# Production server
gunicorn>=21.2.0

# Monitoring
prometheus-client>=0.19.0

# Caching
redis>=5.0.0
EOF

# Main requirements.txt
cp requirements/base.txt requirements.txt

# Create basic config
echo "⚙️ Creating configuration files..."

cat > src/diet_app/config/settings.py << 'EOF'
"""Application configuration settings."""

from pathlib import Path
from typing import List
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Project paths
    PROJECT_NAME: str = "Diet Recommendation App"
    VERSION: str = "0.1.0"
    
    # Data paths
    DATA_DIR: Path = Path("data")
    MODELS_DIR: Path = Path("models")
    
    # Dataset settings
    MVP_DATASET_FILE: str = "mvp_recipes_clean.pkl"
    METADATA_FILE: str = "mvp_metadata.json"
    
    # ML settings
    DEFAULT_RECOMMENDATIONS: int = 10
    SIMILARITY_THRESHOLD: float = 0.1
    
    # API settings
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    
    # Streamlit settings
    STREAMLIT_PORT: int = 8501
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
EOF

# Create basic data loader
echo "📊 Creating data modules..."

cat > src/diet_app/data/loaders.py << 'EOF'
"""Data loading utilities for the diet recommendation app."""

import pandas as pd
import pickle
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)

class RecipeDataLoader:
    """Load and manage recipe datasets."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.DATA_DIR
        
    def load_mvp_dataset(self) -> pd.DataFrame:
        """Load the clean MVP dataset."""
        pkl_path = self.data_dir / settings.MVP_DATASET_FILE
        
        if pkl_path.exists():
            logger.info(f"Loading dataset from {pkl_path}")
            return pd.read_pickle(pkl_path)
        
        # Fallback to CSV
        csv_path = self.data_dir / "mvp_recipes_clean.csv"
        if csv_path.exists():
            logger.info(f"Loading dataset from {csv_path}")
            return pd.read_csv(csv_path)
        
        raise FileNotFoundError(
            f"No dataset found. Please export from notebook first."
        )
    
    def load_metadata(self) -> Dict:
        """Load feature metadata."""
        metadata_path = self.data_dir / settings.METADATA_FILE
        
        if not metadata_path.exists():
            logger.warning("Metadata file not found, returning defaults")
            return self._get_default_metadata()
            
        with open(metadata_path) as f:
            return json.load(f)
    
    def get_feature_names(self) -> List[str]:
        """Get list of MVP feature names."""
        metadata = self.load_metadata()
        return metadata.get('features', self._get_default_features())
    
    def _get_default_features(self) -> List[str]:
        """Default MVP features if metadata is missing."""
        return [
            'Easy', 'Vegan', 'Vegetarian', 'GlutenFree', 'DairyFree',
            'Quick', 'StandardPrepTime', 'LongPrepTime',
            'LowCalorie', 'ModerateCalorie', 'HighCalorie',
            'LowProtein', 'ModerateProtein', 'HighProtein'
        ]
    
    def _get_default_metadata(self) -> Dict:
        """Default metadata structure."""
        return {
            'features': self._get_default_features(),
            'nutritional_columns': [
                'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent'
            ]
        }
EOF

# Create basic test
echo "🧪 Creating test framework..."

cat > tests/unit/test_data_loaders.py << 'EOF'
"""Tests for data loading functionality."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pathlib import Path

from src.diet_app.data.loaders import RecipeDataLoader

class TestRecipeDataLoader:
    """Test cases for RecipeDataLoader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = RecipeDataLoader()
    
    def test_init_with_default_path(self):
        """Test initialization with default data directory."""
        loader = RecipeDataLoader()
        assert loader.data_dir is not None
    
    def test_init_with_custom_path(self):
        """Test initialization with custom data directory."""
        custom_path = Path("/custom/path")
        loader = RecipeDataLoader(custom_path)
        assert loader.data_dir == custom_path
    
    def test_get_default_features(self):
        """Test default feature list."""
        features = self.loader._get_default_features()
        
        assert len(features) == 14
        assert 'Easy' in features
        assert 'Vegan' in features
        assert 'LowCalorie' in features
    
    @patch('pathlib.Path.exists')
    def test_load_mvp_dataset_file_not_found(self, mock_exists):
        """Test error handling when dataset file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            self.loader.load_mvp_dataset()
EOF

# Create pytest configuration
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=src
    --cov-report=term-missing
    --cov-report=html
EOF

# Create .env template
cat > .env.template << 'EOF'
# Environment configuration template
# Copy this to .env and customize for your environment

# Data paths
DATA_DIR=data
MODELS_DIR=models

# API settings
API_HOST=localhost
API_PORT=8000

# Streamlit settings  
STREAMLIT_PORT=8501

# Development settings
DEBUG=true
LOG_LEVEL=INFO
EOF

# Create Makefile for common tasks
cat > Makefile << 'EOF'
.PHONY: install test lint format clean setup

# Install dependencies
install:
	pip install -r requirements/dev.txt

# Run tests
test:
	pytest

# Run linting
lint:
	flake8 src tests
	mypy src

# Format code
format:
	black src tests
	isort src tests

# Clean up cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Export dataset (run this after notebook work)
export-data:
	@echo "Run the data export cells in your notebook first!"
	@echo "Then verify files exist:"
	@ls -la data/mvp_*.* 2>/dev/null || echo "No MVP data files found"

# Setup development environment
setup: install
	pre-commit install
	@echo "✅ Development environment ready!"
	@echo "Next steps:"
	@echo "1. Export your clean dataset from the notebook"
	@echo "2. Run 'make test' to verify setup"
	@echo "3. Start developing!"

# Quick development server
dev-api:
	uvicorn src.diet_app.api.main:app --reload --host 0.0.0.0 --port 8000

# Quick streamlit app
dev-web:
	streamlit run src/diet_app/web/streamlit_app.py --server.port 8501
EOF

# Update .gitignore
cat >> .gitignore << 'EOF'

# Project specific
data/mvp_*.csv
data/mvp_*.pkl
models/
.env

# Test coverage
htmlcov/
.coverage
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ Project structure created successfully!"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Run: pip install -r requirements/dev.txt"
echo "2. Export your clean dataset from the notebook"
echo "3. Run: make test (to verify setup)"
echo "4. Start developing with the modular structure!"
echo ""
echo "📁 Project structure:"
tree -I '__pycache__|*.pyc|venv' . 2>/dev/null || find . -type d -not -path './venv*' -not -path './.git*' | head -20
echo ""
echo "🚀 You're ready to build the recommendation engine!"
