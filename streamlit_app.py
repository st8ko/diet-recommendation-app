import streamlit as st
import pandas as pd
import numpy as np
import random
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Set page config
st.set_page_config(
    page_title="Daily Meal Planner",
    page_icon="🍽️",
    layout="wide"
)

@st.cache_data
def _load_csv_data():
    return pd.read_csv('data/mvp_recipes_clean.csv')

def load_data():
    """Load data with adaptive progress indication"""
    try:
        if 'data_loaded' not in st.session_state:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Container for the loaded data
            data_container = {'df': None, 'loading': True, 'error': None}
            start_time = time.time()
            
            def load_in_background():
                try:
                    data_container['df'] = _load_csv_data()
                except Exception as e:
                    data_container['error'] = e
                finally:
                    data_container['loading'] = False
            
            # Start loading in background
            thread = threading.Thread(target=load_in_background)
            thread.start()
            
            # Adaptive progress - speeds up if loading takes longer
            progress = 0
            messages = [
                '🔍 Locating recipe database...',
                '📊 Loading recipe data...',
                '📊 Reading CSV file...',
                '🧹 Processing data...',
                '🧹 Cleaning data...',
                '✅ Validating recipe information...',
                '✨ Almost ready...'
            ]
            
            message_index = 0
            cycle_count = 0
            
            while data_container['loading']:
                elapsed_time = time.time() - start_time
                
                # Adaptive progress calculation
                if elapsed_time < 3:
                    # Fast progress for first 3 seconds
                    progress = min(60, int(elapsed_time * 20))
                elif elapsed_time < 8:
                    # Slower progress for 3-8 seconds
                    progress = 60 + min(25, int((elapsed_time - 3) * 5))
                else:
                    # Very slow progress after 8 seconds
                    progress = 85 + min(10, int((elapsed_time - 8) * 2))
                
                # Update message periodically
                if int(elapsed_time) > message_index and message_index < len(messages):
                    status_text.text(messages[message_index])
                    message_index += 1
                elif message_index >= len(messages):
                    # Cycle through waiting messages if taking very long
                    waiting_messages = [
                        '⏳ Still loading, please wait...',
                        '🔄 Processing large dataset...',
                        '⌛ Almost there...'
                    ]
                    status_text.text(waiting_messages[cycle_count % len(waiting_messages)])
                    cycle_count += 1
                
                progress_bar.progress(progress)
                time.sleep(0.3)
            
            # Wait for loading to complete
            thread.join()
            
            if data_container['error']:
                raise data_container['error']
            
            # Final progress
            status_text.text('✨ Ready to create your meal plan!')
            progress_bar.progress(100)
            time.sleep(0.3)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.data_loaded = True
            return data_container['df']
        else:
            return _load_csv_data()
            
    except FileNotFoundError:
        st.error("Recipe dataset not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()
    
def format_time(time_str):
    """Convert PT time format to readable format"""
    if pd.isna(time_str) or time_str == "":
        return "Not specified"
    
    # Handle PT format (e.g., PT30M, PT1H30M, PT24H45M)
    if isinstance(time_str, str) and time_str.startswith('PT'):
        time_str = time_str[2:]  # Remove 'PT'
        
        hours = 0
        minutes = 0
        
        # Extract hours
        if 'H' in time_str:
            h_match = re.search(r'(\d+)H', time_str)
            if h_match:
                hours = int(h_match.group(1))
        
        # Extract minutes
        if 'M' in time_str:
            m_match = re.search(r'(\d+)M', time_str)
            if m_match:
                minutes = int(m_match.group(1))
        
        # Format output
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "Not specified"
    
    return str(time_str)

def format_instructions(instructions_str):
    """Format recipe instructions for better display"""
    if pd.isna(instructions_str) or instructions_str == "":
        return ["Instructions not available"]
    
    # Handle c("step1", "step2", ...) format
    if isinstance(instructions_str, str):
        # Remove c( and trailing )
        cleaned = instructions_str.strip()
        if cleaned.startswith('c(') and cleaned.endswith(')'):
            cleaned = cleaned[2:-1]
        
        # Split by quotes and commas, clean up
        steps = []
        # Simple regex to extract quoted strings
        matches = re.findall(r'"([^"]*)"', cleaned)
        if matches:
            steps = [step.strip() for step in matches if step.strip()]
        else:
            # Fallback: split by common delimiters
            steps = [cleaned]
        
        return steps[:8]  # Limit to 8 steps for display
    
    return ["Instructions not available"]

def format_ingredients(ingredients_str):
    """Format recipe ingredients for better display"""
    if pd.isna(ingredients_str) or ingredients_str == "":
        return ["Ingredients not available"]
    
    # Handle c("ingredient1", "ingredient2", ...) format
    if isinstance(ingredients_str, str):
        # Remove c( and trailing )
        cleaned = ingredients_str.strip()
        if cleaned.startswith('c(') and cleaned.endswith(')'):
            cleaned = cleaned[2:-1]
        
        # Split by quotes and commas, clean up
        ingredients = []
        # Simple regex to extract quoted strings
        matches = re.findall(r'"([^"]*)"', cleaned)
        if matches:
            ingredients = [ing.strip() for ing in matches if ing.strip()]
        else:
            # Fallback: split by common delimiters
            ingredients = [cleaned]
        
        return ingredients[:15]  # Limit to 15 ingredients for display
    
    return ["Ingredients not available"]

def display_detailed_recipe(recipe_data, meal_name):
    """Display detailed recipe information in a beautiful card format"""
    
    # Main recipe card
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; margin: 10px 0; color: white;">
            <h2 style="margin: 0; color: white;">🍽️ {meal_name}</h2>
            <h3 style="margin: 5px 0; color: #f0f0f0;">{recipe_data['Name']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        if not pd.isna(recipe_data.get('Description', '')):
            st.markdown(f"**📝 Description:** {recipe_data['Description']}")
        
        # Main metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔥 Calories", f"{int(recipe_data.get('Calories', 0))}")
            st.metric("🧈 Fat", f"{recipe_data.get('FatContent', 0):.1f}g")
            
        with col2:
            st.metric("💪 Protein", f"{int(recipe_data.get('ProteinContent', 0))}g")
            st.metric("🍞 Carbs", f"{recipe_data.get('CarbohydrateContent', 0):.1f}g")
            
        with col3:
            rating = recipe_data.get('AggregatedRating', 0)
            if rating and not pd.isna(rating):
                st.metric("⭐ Rating", f"{float(rating):.1f}")
            else:
                st.metric("⭐ Rating", "N/A")
            
            reviews = recipe_data.get('ReviewCount', 0)
            if reviews and not pd.isna(reviews):
                st.metric("👥 Reviews", f"{int(reviews)}")
            else:
                st.metric("👥 Reviews", "N/A")
                
        with col4:
            st.metric("⏱️ Cook Time", format_time(recipe_data.get('CookTime', '')))
            st.metric("🔪 Prep Time", format_time(recipe_data.get('PrepTime', '')))
        
        # Additional nutritional information
        st.markdown("---")
        st.markdown("**🥗 Detailed Nutrition Information**")
        
        nutr_col1, nutr_col2, nutr_col3 = st.columns(3)
        
        with nutr_col1:
            st.markdown(f"**Saturated Fat:** {recipe_data.get('SaturatedFatContent', 0):.1f}g")
            st.markdown(f"**Fiber:** {recipe_data.get('FiberContent', 0):.1f}g")
            
        with nutr_col2:
            st.markdown(f"**Sodium:** {recipe_data.get('SodiumContent', 0):.0f}mg")
            st.markdown(f"**Sugar:** {recipe_data.get('SugarContent', 0):.1f}g")
            
        with nutr_col3:
            yield_info = recipe_data.get('RecipeYield', 'Not specified')
            st.markdown(f"**Servings:** {yield_info}")
            total_time = format_time(recipe_data.get('TotalTime', ''))
            st.markdown(f"**Total Time:** {total_time}")
        
        # Ingredients section
        st.markdown("---")
        st.markdown("**🛒 Ingredients**")
        ingredients = format_ingredients(recipe_data.get('RecipeIngredientParts', ''))
        
        # Display ingredients in a nice format
        if len(ingredients) > 1:
            for i, ingredient in enumerate(ingredients, 1):
                st.markdown(f"{i}. {ingredient}")
        else:
            st.markdown(ingredients[0])
        
        # Instructions section
        st.markdown("---")
        st.markdown("**👩‍🍳 Cooking Instructions**")
        instructions = format_instructions(recipe_data.get('RecipeInstructions', ''))
        
        # Display instructions in a nice format
        if len(instructions) > 1:
            for i, instruction in enumerate(instructions, 1):
                st.markdown(f"**Step {i}:** {instruction}")
        else:
            st.markdown(instructions[0])

def collect_preferences():
    """Collect user dietary preferences using Streamlit widgets"""
    st.subheader("🥗 Dietary Preferences")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Dietary Restrictions:**")
        vegetarian = st.checkbox("Vegetarian meals only")
        vegan = st.checkbox("Vegan meals only")
        pescatarian = st.checkbox("Pescatarian meals only")
        
    with col2:
        st.markdown("**Dietary Requirements:**")
        easy = st.checkbox("Easy recipes only")
        glutenfree = st.checkbox("Gluten free meals only")
        dairyfree = st.checkbox("Dairy free meals only")
    
    with col3:
        st.markdown("**Meal Characteristics:**")
        calories = st.selectbox(
            "Caloric content per meal:",
            options=['low', 'moderate', 'high'],
            index=2  # default to moderate
        )
        protein = st.selectbox(
            "Protein content per meal:",
            options=['low', 'moderate', 'high'],
            index=2  # default to moderate
        )
        preptime = st.selectbox(
            "Preparation time:",
            options=['quick', 'standard', 'long'],
            index=0  # default to quick
        )
    
    return {
        'vegetarian': 'y' if vegetarian else 'n',
        'vegan': 'y' if vegan else 'n',
        'pescatarian': 'y' if pescatarian else 'n',
        'easy': 'y' if easy else 'n',
        'glutenfree': 'y' if glutenfree else 'n',
        'dairyfree': 'y' if dairyfree else 'n',
        'calories': calories[0],  # first letter
        'protein': protein[0],
        'preptime': preptime[0]
    }

def filter_by_preferences(dataframe, preferences):
    """Filter dataframe based on user preferences - enhanced version from first script"""
    df_filtered = dataframe.copy()
    
    if preferences.get('vegetarian') == 'y':
        df_filtered = df_filtered[df_filtered['Vegetarian']==1]
        
    if preferences.get('vegan') == 'y':
        df_filtered = df_filtered[df_filtered['Vegan']==1]
        
    if preferences.get('pescatarian') == 'y':
        df_filtered = df_filtered[df_filtered['Pescatarian'] ==1]
        
    if preferences.get('easy') == 'y':
        df_filtered = df_filtered[df_filtered['Easy']==1]
        
    if preferences.get('glutenfree') == 'y':
        df_filtered = df_filtered[df_filtered['GlutenFree'] ==1]
        
    if preferences.get('dairyfree') == 'y':
        df_filtered = df_filtered[df_filtered['DairyFree'] ==1]
        
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
    """Give appropriate weight to each meal during the day, to assign appropriate amount of calories/protein to each of them"""
    # Defining weights for every possible named meal (see function above)
    meal_weights = {
        "Breakfast": 3, "Lunch": 4, "Dinner": 4, 
        "Mid-Morning": 2, "Afternoon Snack": 2, 
        "Evening Snack": 2, "Snack": 2, "Default": 3
    } 
    
    meal_slots = generate_meal_names(count)
    meal_plan_weights = {meal: None for meal in meal_slots}
    
    for meal in meal_plan_weights:
        if meal in meal_weights:  # this should somehow get the key and not the value
            meal_plan_weights[meal] = meal_weights[meal] 
        else:
            meal_plan_weights[meal] = meal_weights["Default"]
    
    # calculate the total sum of points
    total_weight = sum(meal_plan_weights.values())
    for meal in meal_plan_weights:
        meal_plan_weights[meal] = round(meal_plan_weights[meal] / total_weight, 2)  # possibly remove the rounding if I feel like it will make it simpler
    
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
    """Generate a daily meal plan from filtered recipes - enhanced version with adaptive targeting and meal categorization"""
    
    if df_filtered.empty:
        return None, "No recipes available with your current filters!", 0, 0
    
    # Get meal slots and initialize plan
    meal_slots = number_of_meals(df_filtered, target_calories, target_protein, max_meals)
    meal_plan = {}
    
    # Calculate targets per meal using optimal weights
    weights = optimal_weights_per_meal(len(meal_slots))
    calories_per_meal = {meal: weights[meal] * target_calories for meal in meal_slots}
    protein_per_meal = {meal: weights[meal] * target_protein for meal in meal_slots}
    
    # Initialize totals
    total_calories = 0
    total_protein = 0
    
    # Meal category mapping for better recipe selection
    meal_category_map = {
        "Lunch": "Lunch/Dinner",
        "Dinner": "Lunch/Dinner", 
        "Snack": "Snacks",
        "Mid-Morning": "Snacks",
        "Afternoon Snack": "Snacks",
        "Evening Snack": "Snacks",
        "Breakfast": "Breakfast"
    }
    
    for meal in meal_slots:
        #Filtering the dataframe for a list of meals that fulfill our criteria, +- standard deviation
        # Calculate remaining targets
        remaining_meals = len([m for m in meal_slots if m not in meal_plan])
        remaining_calories = target_calories - total_calories
        remaining_protein = target_protein - total_protein
        
        # Flexible targets for this meal
        target_cal = calories_per_meal[meal]
        target_prot = protein_per_meal[meal]
        
        # Find suitable recipes with wider tolerance
        df_suitable = df_filtered.loc[
            (df_filtered['Calories'] >= target_cal * (1 - tolerance)) &
            (df_filtered['Calories'] <= target_cal * (1 + tolerance)) &
            (df_filtered['ProteinContent'] >= target_prot * (1 - tolerance)) & 
            (df_filtered['ProteinContent'] <= target_prot * (1 + tolerance))
        ]
        
        meal_category_map = {
            "Lunch": "Lunch/Dinner",
            "Dinner": "Lunch/Dinner", 
            "Snack": "Snacks",
            "Breakfast": "Breakfast"
        }
        
        if meal in meal_category_map:
            df_suitable = df_suitable.loc[df_suitable["MealCat"] == meal_category_map[meal]]
        
        if len(df_suitable) == 0:
            # Fallback: try without meal category restriction
            df_suitable = df_filtered.loc[
                (df_filtered['Calories'] >= target_cal * (1 - tolerance)) &
                (df_filtered['Calories'] <= target_cal * (1 + tolerance)) &
                (df_filtered['ProteinContent'] >= target_prot * (1 - tolerance)) & 
                (df_filtered['ProteinContent'] <= target_prot * (1 + tolerance))
            ]
            
            if len(df_suitable) == 0:
                # Last resort: pick any recipe from filtered set
                if len(df_filtered) > 0:
                    selected_recipe = df_filtered.sample(n=1).iloc[0]
                else:
                    continue
            else:
                # Select highest rated recipe from suitable options
                if 'AggregatedRating' in df_suitable.columns:
                    max_rating = df_suitable['AggregatedRating'].max()
                    top_rated = df_suitable[df_suitable['AggregatedRating'] == max_rating]
                    selected_recipe = top_rated.sample(n=1).iloc[0]
                else:
                    selected_recipe = df_suitable.sample(n=1).iloc[0]
        else:
            # Select highest rated recipe from suitable options
            if 'AggregatedRating' in df_suitable.columns:
                max_rating = df_suitable['AggregatedRating'].max()
                top_rated = df_suitable[df_suitable['AggregatedRating'] == max_rating]
                selected_recipe = top_rated.sample(n=1).iloc[0]
            else:
                selected_recipe = df_suitable.sample(n=1).iloc[0]
        
        # Add to meal plan with full recipe data
        meal_plan[meal] = selected_recipe
        
        # Update totals
        total_calories += int(selected_recipe["Calories"])
        total_protein += int(selected_recipe["ProteinContent"])
    
    summary = f"Total: {total_calories} calories, {total_protein}g protein"
    return meal_plan, summary, total_calories, total_protein

# Main Streamlit App
def main():
    st.title("🍽️ Daily Meal Planner")
    st.markdown("Create your personalized daily meal plan based on your dietary preferences and goals!")
    
    # Show loading message
    st.markdown("### 🚀 Initializing Meal Planner...")
    
    # Load data with progress bar
    df = load_data()
    if df.empty:
        st.stop()
    
    # Display dataset info
    with st.expander("📊 Dataset Information"):
        st.write(f"**Total recipes available:** {len(df)}")
        if not df.empty:
            st.write(f"**Average calories per recipe:** {df['Calories'].mean():.0f}")
            st.write(f"**Average protein per recipe:** {df['ProteinContent'].mean():.1f}g")
            st.write(f"**Recipe columns:** {', '.join(df.columns.tolist())}")
    
    # Sidebar for inputs
    st.sidebar.header("📊 Daily Goals")
    target_calories = st.sidebar.number_input(
        "Target Calories:", 
        min_value=1000, 
        max_value=5000, 
        value=2500, 
        step=50,
        help="Your daily caloric goal"
    )
    target_protein = st.sidebar.number_input(
        "Target Protein (g):", 
        min_value=50, 
        max_value=300, 
        value=120, 
        step=5,
        help="Your daily protein goal in grams"
    )
    max_meals = st.sidebar.slider(
        "Maximum number of meals:", 
        min_value=3, 
        max_value=7, 
        value=4,
        help="Maximum number of meals per day"
    )
    
    tolerance = st.sidebar.slider(
        "Tolerance for calorie/protein matching:",
        min_value=0.1,
        max_value=0.5,
        value=0.2,
        step=0.05,
        help="How flexible should the matching be? Higher = more flexible"
    )
    
    # Display options
    st.sidebar.header("📋 Display Options")
    show_compact = st.sidebar.checkbox("Show compact meal overview", value=True)
    show_detailed = st.sidebar.checkbox("Show detailed recipe information", value=True)  # Changed to True by default
    
    # Main content area
    preferences = collect_preferences()
    
    # Show current filter summary
    active_filters = []
    for key, value in preferences.items():
        if value == 'y':
            active_filters.append(key.capitalize())
        elif key in ['calories', 'protein', 'preptime'] and value != 'm':
            filter_map = {'l': 'Low', 'h': 'High', 'q': 'Quick', 's': 'Standard'}
            active_filters.append(f"{key.capitalize()}: {filter_map.get(value, value)}")
    
    if active_filters:
        st.info(f"**Active filters:** {', '.join(active_filters)}")
    
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
                meal_plan, summary, total_cal, total_prot = generate_daily_meal_plan(
                    df_filtered, target_calories, target_protein, tolerance=tolerance, max_meals=max_meals
                )
                
                if meal_plan:
                    # Compact overview
                    if show_compact:
                        st.subheader("📋 Meal Plan Overview")
                        
                        # Display meal plan in enhanced cards
                        for meal_name, recipe_data in meal_plan.items():
                            with st.container():
                                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                                with col1:
                                    st.markdown(f"**{meal_name}:** {recipe_data['Name']}")
                                with col2:
                                    st.markdown(f"🔥 {int(recipe_data['Calories'])} cal")
                                with col3:
                                    st.markdown(f"💪 {int(recipe_data['ProteinContent'])}g protein")
                                with col4:
                                    rating = recipe_data.get('AggregatedRating', 0)
                                    if rating and not pd.isna(rating):
                                        st.markdown(f"⭐ {float(rating):.1f}")
                                    else:
                                        st.markdown("⭐ N/A")
                        
                        st.markdown("---")
                        
                        # Enhanced summary with goal tracking
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**📊 Daily Totals:**")
                            st.markdown(f"🔥 **Calories:** {total_cal} / {target_calories} ({total_cal/target_calories*100:.1f}%)")
                            st.markdown(f"💪 **Protein:** {total_prot}g / {target_protein}g ({total_prot/target_protein*100:.1f}%)")
                        
                        with col2:
                            st.markdown("**🎯 Goal Achievement:**")
                            cal_status = "✅" if abs(total_cal - target_calories) <= target_calories * 0.1 else "⚠️"
                            prot_status = "✅" if abs(total_prot - target_protein) <= target_protein * 0.1 else "⚠️"
                            st.markdown(f"{cal_status} Calorie target")
                            st.markdown(f"{prot_status} Protein target")
                    
                    # Detailed recipe information (now shown by default)
                    if show_detailed:
                        st.markdown("---")
                        st.subheader("🍽️ Detailed Recipe Information")
                        
                        for meal_name, recipe_data in meal_plan.items():
                            display_detailed_recipe(recipe_data, meal_name)
                            st.markdown("---")
                    
                    # Action buttons
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Generate New Plan"):
                            st.rerun()
                    with col2:
                        if st.button("📊 Show Meal Analytics"):
                            st.session_state.show_analytics = True
                    
                    # Show meal analytics if requested
                    if st.session_state.get('show_analytics', False):
                        st.subheader("📊 Meal Plan Analytics")
                        
                        # Create analytics dataframe
                        analytics_data = []
                        for meal_name, recipe_data in meal_plan.items():
                            analytics_data.append({
                                'Meal': meal_name,
                                'Calories': int(recipe_data['Calories']),
                                'Protein': int(recipe_data['ProteinContent']),
                                'Fat': float(recipe_data.get('FatContent', 0)),
                                'Carbs': float(recipe_data.get('CarbohydrateContent', 0)),
                                'Prep Time': format_time(recipe_data.get('PrepTime', '')),
                                'Cook Time': format_time(recipe_data.get('CookTime', '')),
                                'Rating': float(recipe_data.get('AggregatedRating', 0)) if recipe_data.get('AggregatedRating') and not pd.isna(recipe_data.get('AggregatedRating')) else 0
                            })
                        
                        analytics_df = pd.DataFrame(analytics_data)
                        st.dataframe(analytics_df, use_container_width=True)
                        
                        # Nutrition breakdown
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**🥗 Nutrition Breakdown**")
                            total_fat = analytics_df['Fat'].sum()
                            total_carbs = analytics_df['Carbs'].sum()
                            st.markdown(f"**Total Fat:** {total_fat:.1f}g")
                            st.markdown(f"**Total Carbs:** {total_carbs:.1f}g")
                            st.markdown(f"**Total Protein:** {total_prot}g")
                        
                        with col2:
                            st.markdown("**⏱️ Time Summary**")
                            total_prep_mins = 0
                            total_cook_mins = 0
                            for _, recipe in meal_plan.items():
                                # Rough time calculation for display
                                prep_time = recipe.get('PrepTime', '')
                                cook_time = recipe.get('CookTime', '')
                                # You could implement proper time parsing here
                            st.markdown("**Estimated prep time varies by recipe**")
                            st.markdown("**Check individual recipes for exact times**")
                
                else:
                    st.error("❌ Could not generate meal plan. Try adjusting your preferences!")

if __name__ == "__main__":
    main()