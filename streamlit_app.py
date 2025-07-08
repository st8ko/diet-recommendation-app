import streamlit as st
import pandas as pd
import numpy as np
import random
import re
import time

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
    """Load data with simple progress indication"""
    try:
        if 'data_loaded' not in st.session_state:
            # Simple progress indication without threading
            with st.spinner('🔍 Loading recipe database...'):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Show loading messages
                messages = [
                    '📊 Reading recipe data...',
                    '🧹 Processing nutritional information...',
                    '✅ Validating recipe database...',
                    '✨ Almost ready...'
                ]
                
                for i, message in enumerate(messages):
                    status_text.text(message)
                    progress_bar.progress((i + 1) * 25)
                    time.sleep(0.2)  # Brief pause for user feedback
                
                # Load the data (this is cached by @st.cache_data)
                df = _load_csv_data()
                
                # Final progress
                status_text.text('✨ Ready to create your meal plan!')
                progress_bar.progress(100)
                time.sleep(0.3)
                
                # Clean up progress elements
                progress_bar.empty()
                status_text.empty()
                
                st.session_state.data_loaded = True
                return df
        else:
            # Data already loaded, return from cache
            return _load_csv_data()
            
    except FileNotFoundError:
        st.error("📁 Recipe dataset not found. Please ensure 'data/mvp_recipes_clean.csv' exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
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

def format_ingredients(ingredients_str, quantities_str=None):
    """Format recipe ingredients with quantities for better display"""
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
            # Fallback: try to split by commas and clean up
            # This handles cases where quotes might be malformed
            parts = cleaned.split(',')
            ingredients = []
            for part in parts:
                # Remove quotes, brackets, whitespace, and other formatting
                clean_part = part.strip().strip('"').strip("'").strip("['").strip("']").strip()
                if clean_part and clean_part != "":
                    ingredients.append(clean_part)
            
            # If we still don't have good ingredients, return a fallback message
            if not ingredients:
                ingredients = ["Ingredients not available"]
        
        # Process quantities if provided
        quantities = []
        if quantities_str and not pd.isna(quantities_str) and quantities_str != "":
            if isinstance(quantities_str, str):
                # Remove c( and trailing )
                cleaned_qty = quantities_str.strip()
                if cleaned_qty.startswith('c(') and cleaned_qty.endswith(')'):
                    cleaned_qty = cleaned_qty[2:-1]
                
                # Extract quantities using regex
                qty_matches = re.findall(r'"([^"]*)"', cleaned_qty)
                if qty_matches:
                    quantities = [qty.strip() for qty in qty_matches if qty.strip()]
                else:
                    # Fallback for quantities
                    qty_parts = cleaned_qty.split(',')
                    for part in qty_parts:
                        clean_qty_part = part.strip().strip('"').strip("'").strip('[').strip(']').strip()
                        if clean_qty_part and clean_qty_part != "":
                            quantities.append(clean_qty_part)
        
        # Combine ingredients with quantities if available
        combined_ingredients = []
        for i, ingredient in enumerate(ingredients[:15]):  # Limit to 15 ingredients
            if quantities and i < len(quantities) and quantities[i]:
                # Format as "quantity ingredient"
                combined_ingredients.append(f"{quantities[i]} {ingredient}")
            else:
                # Just the ingredient if no quantity available
                combined_ingredients.append(ingredient)
        
        return combined_ingredients
    
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
        
        # Check if quantities column exists
        if 'RecipeIngredientQuantities' in recipe_data:
            ingredients = format_ingredients(
                recipe_data.get('RecipeIngredientParts', ''),
                recipe_data.get('RecipeIngredientQuantities', '')
            )
        else:
            # Fallback to ingredients only with a note
            ingredients = format_ingredients(recipe_data.get('RecipeIngredientParts', ''))
            st.markdown("*Note: Ingredient quantities not available in this dataset version*")
        
        # Display ingredients as clean bullet points
        for ingredient in ingredients:
            st.markdown(f"• {ingredient}")
        
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
        df_filtered = df_filtered[df_filtered['Pescatarian']==1]
        
    if preferences.get('easy') == 'y':
        df_filtered = df_filtered[df_filtered['Easy']==1]
        
    if preferences.get('glutenfree') == 'y':
        df_filtered = df_filtered[df_filtered['GlutenFree']==1]
        
    if preferences.get('dairyfree') == 'y':
        df_filtered = df_filtered[df_filtered['DairyFree']==1]
        
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
                if 'AggregatedRating' in df_suitable.columns and not df_suitable['AggregatedRating'].isna().all():
                    max_rating = df_suitable['AggregatedRating'].max()
                    top_rated = df_suitable[df_suitable['AggregatedRating'] == max_rating]
                    if len(top_rated) > 0:
                        selected_recipe = top_rated.sample(n=1).iloc[0]
                    elif len(df_suitable) > 0:
                        selected_recipe = df_suitable.sample(n=1).iloc[0]
                    else:
                        continue
                else:
                    if len(df_suitable) > 0:
                        selected_recipe = df_suitable.sample(n=1).iloc[0]
                    else:
                        continue
        else:
            # Select highest rated recipe from suitable options
            if 'AggregatedRating' in df_suitable.columns and not df_suitable['AggregatedRating'].isna().all():
                max_rating = df_suitable['AggregatedRating'].max()
                top_rated = df_suitable[df_suitable['AggregatedRating'] == max_rating]
                if len(top_rated) > 0:
                    selected_recipe = top_rated.sample(n=1).iloc[0]
                elif len(df_suitable) > 0:
                    selected_recipe = df_suitable.sample(n=1).iloc[0]
                else:
                    continue
            else:
                if len(df_suitable) > 0:
                    selected_recipe = df_suitable.sample(n=1).iloc[0]
                else:
                    continue
        
        # Add to meal plan with full recipe data
        meal_plan[meal] = selected_recipe
        
        # Update totals
        total_calories += int(selected_recipe["Calories"])
        total_protein += int(selected_recipe["ProteinContent"])
    
    summary = f"Total: {total_calories} calories, {total_protein}g protein"
    return meal_plan, summary, total_calories, total_protein

# Main Streamlit App
def about_page():
    """Display the About page with project information"""
    # Add top navigation hint
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
        💡 <strong>Tip:</strong> Use the sidebar navigation buttons to switch between <strong>About Project</strong> and <strong>Meal Planner</strong> pages!
    </div>
    """, unsafe_allow_html=True)
    
    st.title("📖 About This Project")
    st.markdown("---")
    
    # Project overview
    st.markdown("""
    ## 🍽️ Diet Recommendation App
    
    > **A sophisticated nutrition platform that leverages data science to provide personalized meal recommendations from 960,000+ recipes**
    
    This comprehensive diet recommendation system demonstrates advanced **data science**, **software engineering**, 
    and **product development** skills through the creation of a data-driven nutrition platform.
    """)
    
    # Key features
    st.markdown("""
    ## 🚀 Key Features
    
    ### 📊 **Data Science Excellence**
    - **Large-Scale Processing**: 960K+ recipes cleaned and processed
    - **Multi-Source Integration**: Merged multiple Kaggle datasets
    - **Statistical Analysis**: 99th percentile outlier detection
    - **Feature Engineering**: 12 dietary classification features
    - **Data Pipeline**: Automated preprocessing and export
    
    ### 🤖 **Intelligent Recommendations**
    - **Multi-Factor Filtering**: Nutritional targets, dietary restrictions, time preferences
    - **Meal Planning**: Automated daily plans with optimal distribution
    - **Adaptive Targeting**: Dynamic meal calculation based on goals
    - **Rating-Based Selection**: Prioritizes highly-rated recipes
    - **Nutri-Score Development**: Healthiness scoring system (in progress)
    
    ### 💻 **Modern Web Development**
    - **Interactive UI**: Beautiful Streamlit interface
    - **Real-time Filtering**: Dynamic preference collection
    - **Performance Optimization**: Efficient data loading with caching
    - **User Experience**: Intuitive design and detailed displays
    """)
    
    # Technical stack
    st.markdown("""
    ## 🛠️ Technical Stack
    
    - **Python 3.11**: Core programming language
    - **Streamlit**: Interactive web application framework
    - **Pandas & NumPy**: Data manipulation and analysis
    - **Scikit-learn**: Machine learning foundations
    - **Jupyter**: Data analysis and exploration
    """)
    
    # Data sources
    st.markdown("""
    ## 📊 Data Sources
    
    **Inspiration**: [zakaria-narjis/Diet-Recommendation-System](https://github.com/zakaria-narjis/Diet-Recommendation-System)
    
    **Datasets**:
    - [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews?select=recipes.csv) (960K+ recipes)
    - [Food.com Recipes with Search Terms and Tags](https://www.kaggle.com/datasets/shuyangli94/foodcom-recipes-with-search-terms-and-tags) (Enhanced categorization)
    """)
    
    # Project metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Total Recipes", "960K+")
        st.metric("🧹 Clean Dataset", "477K")
    with col2:
        st.metric("🏷️ Features", "12")
        st.metric("📊 Data Quality", "98.8%")
    with col3:
        st.metric("🔥 Avg Calories", "367")
        st.metric("💪 Avg Protein", "16.4g")
    
    st.markdown("---")
    
    # GitHub link
    st.markdown("""
    ## 🔗 Project Repository
    
    **Explore the complete project on GitHub:**
    """)
    
    # Create a prominent button for GitHub
    st.link_button(
        "🐙 View on GitHub",
        "https://github.com/st8ko/diet-recommendation-app",
        help="Access the complete source code, documentation, and project files",
        use_container_width=True
    )
    
    # Alternative link
    st.markdown("""
    **Direct link**: [https://github.com/st8ko/diet-recommendation-app](https://github.com/st8ko/diet-recommendation-app)
    
    """)
    
    # Skills demonstrated
    st.markdown("""
    ## 🎯 Skills Demonstrated
    
    **Data Science**: Big data processing, statistical analysis, feature engineering, EDA
    
    **Software Engineering**: Clean architecture, performance optimization, error handling
    
    **Web Development**: Interactive applications, UI/UX design, user experience
    
    **Product Development**: Requirements analysis, technical documentation, project management
    """)
    
    st.markdown("---")
    st.markdown("*Built with ❤️ using Python and Streamlit*")

def meal_planner_page():
    """Display the main meal planner functionality"""
    # Add top navigation hint
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
        💡 <strong>Tip:</strong> Use the sidebar navigation buttons to switch between <strong>Meal Planner</strong> and <strong>About Project</strong> pages!
    </div>
    """, unsafe_allow_html=True)
    
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
            # Get sidebar values
            target_calories = st.session_state.get('target_calories', 2500)
            target_protein = st.session_state.get('target_protein', 120)
            tolerance = st.session_state.get('tolerance', 0.2)
            max_meals = st.session_state.get('max_meals', 4)
            show_compact = st.session_state.get('show_compact', True)
            show_detailed = st.session_state.get('show_detailed', True)
            
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

def main():
    """Main application with page navigation"""
    # Page selection in sidebar with prominent buttons
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px; margin-bottom: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white;">
        <h2 style="margin: 0; color: white;">🧭 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize page state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🍽️ Meal Planner"
    
    # Create navigation buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🍽️\nMeal\nPlanner", 
                    key="nav_meal_planner",
                    help="Create personalized meal plans",
                    use_container_width=True):
            st.session_state.current_page = "🍽️ Meal Planner"
    
    with col2:
        if st.button("📖\nAbout\nProject", 
                    key="nav_about",
                    help="Learn about this project",
                    use_container_width=True):
            st.session_state.current_page = "📖 About"
    
    # Add visual indicator for current page
    if st.session_state.current_page == "🍽️ Meal Planner":
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 5px; margin: 10px 0; 
                    background-color: #e8f5e8; border-radius: 5px; 
                    border-left: 4px solid #4CAF50;">
            <small><strong>📍 Currently on: Meal Planner</strong></small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 5px; margin: 10px 0; 
                    background-color: #e8f0ff; border-radius: 5px; 
                    border-left: 4px solid #2196F3;">
            <small><strong>📍 Currently on: About Project</strong></small>
        </div>
        """, unsafe_allow_html=True)
    
    page = st.session_state.current_page
    
    # Sidebar for inputs (only show on meal planner page)
    if page == "🍽️ Meal Planner":
        st.sidebar.markdown("---")
        st.sidebar.header("📊 Daily Goals")
        target_calories = st.sidebar.number_input(
            "Target Calories:", 
            min_value=1000, 
            max_value=5000, 
            value=2500, 
            step=50,
            help="Your daily caloric goal",
            key="target_calories"
        )
        target_protein = st.sidebar.number_input(
            "Target Protein (g):", 
            min_value=50, 
            max_value=300, 
            value=120, 
            step=5,
            help="Your daily protein goal in grams",
            key="target_protein"
        )
        max_meals = st.sidebar.slider(
            "Maximum number of meals:", 
            min_value=3, 
            max_value=7, 
            value=4,
            help="Maximum number of meals per day",
            key="max_meals"
        )
        
        tolerance = st.sidebar.slider(
            "Tolerance for calorie/protein matching:",
            min_value=0.1,
            max_value=0.5,
            value=0.2,
            step=0.05,
            help="How flexible should the matching be? Higher = more flexible",
            key="tolerance"
        )
        
        # Display options
        st.sidebar.header("📋 Display Options")
        show_compact = st.sidebar.checkbox("Show compact meal overview", value=True, key="show_compact")
        show_detailed = st.sidebar.checkbox("Show detailed recipe information", value=True, key="show_detailed")
    
    # Display selected page
    if page == "🍽️ Meal Planner":
        meal_planner_page()
    elif page == "📖 About":
        about_page()

if __name__ == "__main__":
    main()