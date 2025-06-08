import streamlit as st
import pandas as pd
import numpy as np
import random

# Set page config
st.set_page_config(
    page_title="Daily Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

# Cache the data loading
@st.cache_data
def load_data():
    """Load the recipe dataset"""
    try:
        df = pd.read_csv('data/mvp_recipes_clean.csv')
        return df
    except FileNotFoundError:
        st.error("Recipe dataset not found. Please ensure 'data/mvp_recipes_clean.csv' exists.")
        return pd.DataFrame()

def collect_preferences():
    """Collect user dietary preferences using Streamlit widgets"""
    st.subheader("🥗 Dietary Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vegetarian = st.checkbox("Vegetarian meals only")
        vegan = st.checkbox("Vegan meals only")
        easy = st.checkbox("Easy recipes only")
    
    with col2:
        calories = st.selectbox(
            "Caloric content per meal:",
            options=['low', 'moderate', 'high'],
            index=1  # default to moderate
        )
        protein = st.selectbox(
            "Protein content per meal:",
            options=['low', 'moderate', 'high'],
            index=1  # default to moderate
        )
        preptime = st.selectbox(
            "Preparation time:",
            options=['quick', 'standard', 'long'],
            index=0  # default to quick
        )
    
    return {
        'vegetarian': 'y' if vegetarian else 'n',
        'vegan': 'y' if vegan else 'n',
        'easy': 'y' if easy else 'n',
        'calories': calories[0],  # first letter
        'protein': protein[0],
        'preptime': preptime[0]
    }

def filter_by_preferences(dataframe, preferences):
    """Filter dataframe based on user preferences"""
    df_filtered = dataframe.copy()
    
    if preferences.get('vegetarian') == 'y':
        df_filtered = df_filtered[df_filtered['Vegetarian']==1]
        
    if preferences.get('vegan') == 'y':
        df_filtered = df_filtered[df_filtered['Vegan']==1]
        
    if preferences.get('easy') == 'y':
        df_filtered = df_filtered[df_filtered['Easy']==1]
        
    if preferences.get('calories') == 'l':
        df_filtered = df_filtered[df_filtered['LowCalorie']==1]
    elif preferences.get('calories') == 'm':
        df_filtered = df_filtered[df_filtered['ModerateCalorie']==1]
    elif preferences.get('calories') == 'h':
        df_filtered = df_filtered[df_filtered['HighCalorie']==1]
        
    if preferences.get('protein') == 'l':
        df_filtered = df_filtered[df_filtered['LowProtein']==1]
    elif preferences.get('protein') == 'm':
        df_filtered = df_filtered[df_filtered['ModerateProtein']==1]    
    elif preferences.get('protein') == 'h':
        df_filtered = df_filtered[df_filtered['HighProtein']==1]
        
    if preferences.get('preptime') == 'q':
        df_filtered = df_filtered[df_filtered['Quick']==1]
    elif preferences.get('preptime') == 's':
        df_filtered = df_filtered[df_filtered['StandardPrepTime']==1]
    elif preferences.get('preptime') == 'l':
        df_filtered = df_filtered[df_filtered['LongPrepTime']==1]
        
    return df_filtered.reset_index(drop=True)

def generate_meal_names(count=3):
    """Generate appropriate meal names based on count"""
    base_names = ["Breakfast", "Lunch", "Dinner"]
    
    if count <= 3:
        return base_names[:count]
    elif count == 4:
        return ["Breakfast", "Lunch", "Snack", "Dinner"]
    elif count == 5:
        return ["Breakfast", "Mid-Morning", "Lunch", "Afternoon Snack", "Dinner"]
    elif count == 6:
        return ["Breakfast", "Mid-Morning", "Lunch", "Afternoon Snack", "Dinner", "Evening Snack"]
    else:
        return [f"Meal {i+1}" for i in range(count)]

def optimal_weights_per_meal(count=3):
    """Give appropriate weight to each meal during the day"""
    meal_weights = {
        "Breakfast": 3, "Lunch": 4, "Dinner": 4, 
        "Mid-Morning": 2, "Afternoon Snack": 2, 
        "Evening Snack": 2, "Default": 3
    } 
    
    meal_slots = generate_meal_names(count)
    meal_plan_weights = {}
    
    for meal in meal_slots:
        meal_plan_weights[meal] = meal_weights.get(meal, meal_weights["Default"])
    
    total_weight = sum(meal_plan_weights.values())
    for meal in meal_plan_weights:
        meal_plan_weights[meal] = round(meal_plan_weights[meal] / total_weight, 2)
    
    return meal_plan_weights

def number_of_meals(df_filtered, target_calories=2500, target_protein=120, max_meals=6):
    """Estimate optimal number of meals for given goals"""
    if df_filtered.empty:
        return ["Breakfast", "Lunch", "Dinner"]
    
    avg_calories = df_filtered["Calories"].mean()
    avg_protein = df_filtered["ProteinContent"].mean()
    
    estimated_meals_by_cal = min(max_meals, max(2, int(target_calories // (avg_calories * 0.8))))
    estimated_meals_by_protein = min(max_meals, max(2, int(target_protein // (avg_protein * 0.8))))
    
    optimal_meals = max(estimated_meals_by_cal, estimated_meals_by_protein)
    
    return generate_meal_names(optimal_meals)

def generate_daily_meal_plan(df_filtered, target_calories=2500, target_protein=120, tolerance=0.2, max_meals=6):
    """Generate a daily meal plan from filtered recipes"""
    
    if df_filtered.empty:
        return None, "No recipes available with your current filters!"
    
    meal_slots = number_of_meals(df_filtered, target_calories, target_protein, max_meals)
    meal_plan = {}
    
    # Calculate targets per meal
    weights = optimal_weights_per_meal(len(meal_slots))
    calories_per_meal = {meal: weights[meal] * target_calories for meal in meal_slots}
    protein_per_meal = {meal: weights[meal] * target_protein for meal in meal_slots}
    
    # Calculate allowable deviations
    deviation_calories = {meal: tolerance * calories_per_meal[meal] for meal in meal_slots}
    deviation_protein = {meal: tolerance * protein_per_meal[meal] for meal in meal_slots}
    
    total_calories = 0
    total_protein = 0
    
    for meal in meal_slots:
        # Filter suitable recipes
        df_suitable = df_filtered.loc[
            (df_filtered['Calories'] >= calories_per_meal[meal] - deviation_calories[meal]) &
            (df_filtered['Calories'] <= calories_per_meal[meal] + deviation_calories[meal]) &
            (df_filtered['ProteinContent'] >= protein_per_meal[meal] - deviation_protein[meal]) & 
            (df_filtered['ProteinContent'] <= protein_per_meal[meal] + deviation_protein[meal])
        ]
        
        if len(df_suitable) == 0:
            # Fallback to any recipe from filtered set
            if len(df_filtered) > 0:
                selected_recipe = df_filtered.sample(n=1).iloc[0]
            else:
                continue
        else:
            selected_recipe = df_suitable.sample(n=1).iloc[0]
        
        meal_plan[meal] = {
            'name': selected_recipe["Name"],
            'calories': int(selected_recipe["Calories"]),
            'protein': int(selected_recipe["ProteinContent"])
        }
        
        total_calories += meal_plan[meal]['calories']
        total_protein += meal_plan[meal]['protein']
    
    return meal_plan, f"Total: {total_calories} calories, {total_protein}g protein"

# Main Streamlit App
def main():
    st.title("🍽️ Daily Meal Planner")
    st.markdown("Create your personalized daily meal plan based on your dietary preferences and goals!")
    
    # Load data
    df = load_data()
    if df.empty:
        st.stop()
    
    # Sidebar for inputs
    st.sidebar.header("📊 Daily Goals")
    target_calories = st.sidebar.number_input(
        "Target Calories:", 
        min_value=1000, 
        max_value=5000, 
        value=2500, 
        step=50
    )
    target_protein = st.sidebar.number_input(
        "Target Protein (g):", 
        min_value=50, 
        max_value=300, 
        value=120, 
        step=5
    )
    max_meals = st.sidebar.slider(
        "Maximum number of meals:", 
        min_value=3, 
        max_value=6, 
        value=4
    )
    
    # Main content area
    preferences = collect_preferences()
    
    # Generate meal plan button
    if st.button("🎯 Generate My Meal Plan", type="primary"):
        with st.spinner("Creating your personalized meal plan..."):
            # Filter recipes
            df_filtered = filter_by_preferences(df, preferences)
            
            if df_filtered.empty:
                st.error("❌ No recipes match your criteria. Try adjusting your preferences!")
            else:
                st.success(f"✅ Found {len(df_filtered)} recipes matching your preferences!")
                
                # Generate meal plan
                meal_plan, summary = generate_daily_meal_plan(
                    df_filtered, target_calories, target_protein, max_meals=max_meals
                )
                
                if meal_plan:
                    st.subheader("🍽️ Your Daily Meal Plan")
                    
                    # Display meal plan in cards
                    for meal_name, details in meal_plan.items():
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(f"**{meal_name}:** {details['name']}")
                            with col2:
                                st.markdown(f"🔥 {details['calories']} cal")
                            with col3:
                                st.markdown(f"💪 {details['protein']}g protein")
                    
                    st.markdown("---")
                    st.markdown(f"**{summary}**")
                    
                    # Option to regenerate
                    if st.button("🔄 Generate New Plan"):
                        st.experimental_rerun()
                else:
                    st.error("❌ Could not generate meal plan. Try adjusting your preferences!")

if __name__ == "__main__":
    main()