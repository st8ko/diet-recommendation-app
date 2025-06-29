#!/usr/bin/env python3
"""
Export MVP dataset from EDA notebook for application development
"""

import pandas as pd
import json
import os
from datetime import datetime

def export_mvp_dataset():
    """Export the clean MVP dataset and metadata"""
    
    print("Loading original dataset...")
    # Load the original dataset
    df = pd.read_csv('data/recipes.csv')
    print(f"Original dataset shape: {df.shape}")
    
    # Apply the same cleaning and feature engineering as in notebook
    print("Applying data cleaning...")
    
    # Remove outliers (99th percentile threshold)
    numerical_cols = ['Calories', 'FatContent', 'SaturatedFatContent', 
                     'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 
                     'FiberContent', 'SugarContent', 'ProteinContent']
    
    for col in numerical_cols:
        if col in df.columns:
            p99 = df[col].quantile(0.99)
            outliers = df[col] > p99
            df = df[~outliers]
    
    print(f"After outlier removal: {df.shape}")
    
    # Feature engineering - Clean keywords
    print("Engineering features...")
    df['Keywords'] = df['Keywords'].str.strip('c()').str.replace('"', '', regex=False)
    df['Keywords'] = df['Keywords'].apply(
        lambda keyword_string: [kw.strip().lower() for kw in str(keyword_string).split(',')]
                                if pd.notna(keyword_string) else []
    )
    
    # Encode Easy feature
    df['Easy'] = df['Keywords'].apply(lambda x: 1 if 'easy' in x else 0)
    
    # Encode Vegan feature
    meat_list = ['beef', 'pork', 'chicken', 'turkey', 'fish', 'lamb', 'meat', 'bacon', 'ham']
    animal_products = ['cheese', 'milk', 'butter', 'cream', 'egg', 'honey', 'yogurt']
    df['Vegan'] = df['Keywords'].apply(
        lambda x: 1 if not any(item in x for item in meat_list + animal_products) else 0
    )
    
    # Encode Vegetarian feature  
    df['Vegetarian'] = df['Keywords'].apply(
        lambda x: 1 if not any(meat_item in x for meat_item in meat_list) else 0
    )
    
    # Encode Pescatarian feature (allows fish but no other meat)
    non_fish_meat = ['beef', 'pork', 'chicken', 'turkey', 'lamb', 'meat', 'bacon', 'ham']
    df['Pescatarian'] = df['Keywords'].apply(
        lambda x: 1 if not any(meat_item in x for meat_item in non_fish_meat) else 0
    )
    
    # Encode time-based features
    quick_keywords = ['< 15 mins', '< 30 mins', 'quick', 'fast']
    df['Quick'] = df['Keywords'].apply(
        lambda x: 1 if any(kw in x for kw in quick_keywords) else 0
    )
    
    standard_keywords = ['< 4 hours', 'weeknight', 'easy', 'one dish meal']
    df['StandardPrepTime'] = df['Keywords'].apply(
        lambda x: 1 if any(kw in x for kw in standard_keywords) else 0
    )
    
    long_prep_keywords = ['crock pot slow cooker', 'beef crock pot', 'time to make', 
                         'slow cooked', 'long cooking time']
    df['LongPrepTime'] = df['Keywords'].apply(
        lambda x: 1 if any(kw in x for kw in long_prep_keywords) else 0
    )
    
    # Encode dietary restriction features
    gluten_free_keywords = ['gluten-free', 'gluten free', 'celiac', 'wheat-free', 'wheat free']
    df['GlutenFree'] = df['Keywords'].apply(
        lambda x: 1 if any(kw in x for kw in gluten_free_keywords) else 0
    )
    
    dairy_free_keywords = ['dairy-free', 'dairy free', 'lactose-free', 'lactose free', 'vegan']
    dairy_products = ['milk', 'cheese', 'butter', 'cream', 'yogurt']
    df['DairyFree'] = df['Keywords'].apply(
        lambda x: 1 if (any(kw in x for kw in dairy_free_keywords) or 
                       not any(dairy in x for dairy in dairy_products)) else 0
    )
    
    # Encode nutritional categories
    df['LowCalorie'] = (df['Calories'] < 300).astype(int)
    df['ModerateCalorie'] = ((df['Calories'] >= 300) & (df['Calories'] <= 600)).astype(int)
    df['HighCalorie'] = (df['Calories'] > 600).astype(int)
    
    df['LowProtein'] = (df['ProteinContent'] < 10).astype(int)
    df['ModerateProtein'] = ((df['ProteinContent'] >= 10) & (df['ProteinContent'] <= 20)).astype(int)
    df['HighProtein'] = (df['ProteinContent'] > 20).astype(int)
    
    # Create MealCat column based on recipe category
    meal_category_mapping = {
        'appetizers': 'Snacks',
        'beverages': 'Snacks', 
        'breakfast': 'Breakfast',
        'brunch': 'Breakfast',
        'desserts': 'Snacks',
        'lunch/snacks': 'Lunch/Dinner',
        'main dish': 'Lunch/Dinner',
        'side dish': 'Lunch/Dinner',
        'soups': 'Lunch/Dinner',
        'salads': 'Lunch/Dinner'
    }
    
    df['MealCat'] = df['RecipeCategory'].str.lower().map(meal_category_mapping).fillna('Lunch/Dinner')
    
    # Define MVP features and columns
    mvp_features = [
        'Easy', 'Vegan', 'Vegetarian', 'Pescatarian',
        'Quick', 'StandardPrepTime', 'LongPrepTime',
        'LowCalorie', 'ModerateCalorie', 'HighCalorie',
        'LowProtein', 'ModerateProtein', 'HighProtein',
        'GlutenFree', 'DairyFree'
    ]
    
    mvp_columns = [
        # Basic recipe information
        'RecipeId', 'Name', 'Description', 'RecipeCategory', 'MealCat', 'AggregatedRating', 'ReviewCount',
        'CookTime', 'PrepTime', 'TotalTime', 'RecipeYield', 'RecipeInstructions', 'RecipeIngredientQuantities',
        
        # Nutritional information
        'Calories', 'ProteinContent', 'FatContent', 'SaturatedFatContent', 
        'CarbohydrateContent', 'SodiumContent', 'FiberContent', 'SugarContent',
        
        # Keywords and ingredients
        'Keywords', 'RecipeIngredientParts',
        
        # MVP encoded features
        'Easy', 'Vegan', 'Vegetarian', 'Pescatarian',
        'Quick', 'StandardPrepTime', 'LongPrepTime',
        'LowCalorie', 'ModerateCalorie', 'HighCalorie',
        'LowProtein', 'ModerateProtein', 'HighProtein',
        'GlutenFree', 'DairyFree'
    ]
    
    # Create MVP dataset
    mvp_df = df[mvp_columns].copy()
    
    print(f"MVP dataset shape: {mvp_df.shape}")
    print(f"Memory usage: {mvp_df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    # Export dataset
    print("Exporting MVP dataset...")
    
    mvp_df.to_csv('data/mvp_recipes_clean.csv', index=False)
    print(f"✅ Exported CSV: {len(mvp_df):,} recipes to mvp_recipes_clean.csv")
    
    mvp_df.to_pickle('data/mvp_recipes_clean.pkl')
    print(f"✅ Exported Pickle: {len(mvp_df):,} recipes to mvp_recipes_clean.pkl")
    
    # Export feature metadata
    feature_metadata = {
        'total_recipes': len(mvp_df),
        'total_features': len(mvp_features),
        'features': mvp_features,
        'feature_counts': {feature: int(mvp_df[feature].sum()) for feature in mvp_features},
        'nutritional_columns': ['Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'FiberContent', 'SugarContent'],
        'dataset_info': {
            'shape': mvp_df.shape,
            'memory_mb': round(mvp_df.memory_usage(deep=True).sum() / 1024**2, 1),
            'columns': list(mvp_df.columns)
        },
        'created_date': datetime.now().isoformat(),
        'source': 'Food.com recipes dataset - MVP processing pipeline'
    }
    
    with open('data/mvp_metadata.json', 'w') as f:
        json.dump(feature_metadata, f, indent=2)
    
    print(f"✅ Exported metadata: mvp_metadata.json")
    print(f"\n=== EXPORT COMPLETE ===")
    print(f"Dataset ready for application development!")
    print(f"Files created:")
    print(f"  - mvp_recipes_clean.csv ({mvp_df.shape[0]:,} recipes)")
    print(f"  - mvp_recipes_clean.pkl (faster loading)")
    print(f"  - mvp_metadata.json (feature definitions)")
    
    # Show feature summary
    print(f"\n=== FEATURE SUMMARY ===")
    for feature in mvp_features:
        count = mvp_df[feature].sum()
        percentage = count / len(mvp_df) * 100
        print(f"{feature:<20}: {count:>6,} recipes ({percentage:>5.1f}%)")

if __name__ == "__main__":
    export_mvp_dataset()
