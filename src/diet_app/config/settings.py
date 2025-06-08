"""
Application configuration and settings for the Diet Recommendation App.
"""
from pathlib import Path
from typing import List, Dict, Any
import os

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
MVP_DATASET_PATH = DATA_DIR / "mvp_recipes_clean.pkl"
MVP_METADATA_PATH = DATA_DIR / "mvp_metadata.json"
RAW_DATASET_PATH = DATA_DIR / "recipes.csv"

# Model settings
RECOMMENDATION_SETTINGS = {
    "max_recommendations": 20,
    "min_recommendations": 5,
    "similarity_threshold": 0.1,
    "performance_target_seconds": 2.0,
}

# Feature configuration (matching MVP dataset)
MVP_FEATURES = [
    "Easy", "Vegan", "Vegetarian", "GlutenFree", "DairyFree",
    "Quick", "StandardPrepTime", "LongPrepTime", 
    "LowCal", "ModCal", "HighCal", "HighProtein"
]

# Nutritional columns
NUTRITIONAL_COLUMNS = [
    "Calories", "ProteinContent", "FatContent", "SaturatedFatContent",
    "CarbohydrateContent", "SodiumContent", "FiberContent", 
    "SugarContent", "CholesterolContent"
]

# Recipe display columns
RECIPE_DISPLAY_COLUMNS = [
    "RecipeId", "Name", "Calories", "ProteinContent", 
    "AggregatedRating", "ReviewCount", "PrepTime", "CookTime"
]

# Default user preferences
DEFAULT_USER_PREFERENCES = {
    "dietary_restrictions": [],
    "time_preference": "StandardPrepTime",
    "calorie_preference": "ModCal",
    "protein_priority": False,
    "max_results": 10
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "data_loading_max_seconds": 5.0,
    "recommendation_max_seconds": 2.0,
    "search_max_seconds": 1.0,
    "memory_usage_max_mb": 1000
}

def get_data_path(filename: str) -> Path:
    """Get full path to data file."""
    return DATA_DIR / filename

def validate_settings() -> bool:
    """Validate that all required paths exist."""
    required_paths = [DATA_DIR, MVP_DATASET_PATH, MVP_METADATA_PATH]
    
    for path in required_paths:
        if not path.exists():
            print(f"Warning: Required path does not exist: {path}")
            return False
    
    return True

# Environment-specific settings
ENVIRONMENT = os.getenv("DIET_APP_ENV", "development")

if ENVIRONMENT == "production":
    RECOMMENDATION_SETTINGS["max_recommendations"] = 50
    PERFORMANCE_THRESHOLDS["recommendation_max_seconds"] = 1.0
elif ENVIRONMENT == "testing":
    RECOMMENDATION_SETTINGS["max_recommendations"] = 5
    PERFORMANCE_THRESHOLDS["recommendation_max_seconds"] = 5.0