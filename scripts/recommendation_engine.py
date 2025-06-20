import pandas as pd
import numpy as np
import random

df = pd.read_csv('data/mvp_recipes_clean.csv')
print(df.tail())

def choose_preferences():
    """Collect user dietary preferences."""
    
    def get_input(prompt, valid_options):
        while True:
            user_input = input(prompt).lower().strip()
            if user_input in valid_options:
                return user_input
            print(f"Invalid input! Please enter: {'/'.join(valid_options)}\n")
    
    questions = [
        ("Do you want meals that are vegetarian? (y/n): ", ['y', 'n'], 'vegetarian'),
        ("Do you want your meals pescatarian? (y/n): ", ['y', 'n'], 'pescatarian'),
        ("Do you want your meals vegan? (y/n): ", ['y', 'n'], 'vegan'),
        ("Do you want your meals easy? (y/n): ", ['y', 'n'], 'easy'),
        ("Do you want your meals diary free? (y/n): ", ['y', 'n'], 'diaryfree'),
        ('Do you want your meals gluten free? (y/n): ', ['y', 'n',], 'glutenfree'),
        ("Caloric content - low/moderate/high? (l/m/h): ", ['l', 'm', 'h'], 'calories'),
        ("Protein content - low/moderate/high? (l/m/h): ", ['l', 'm', 'h'], 'protein'),
        ("Prep time - quick/standard/long? (q/s/l): ", ['q', 's', 'l'], 'preptime')
    ]
    
    preferences = {}
    for prompt, options, key in questions:
        preferences[key] = get_input(prompt, options)
    
    return preferences
    

def filter_by_preferences(dataframe = df, preferences = 0): #in future iterations this function could use less hardcoding of the categories, similar to choose_preferences()
    '''For the time being this function will make you choose at least one option from each filter category, later on you will be able to choose only the ones you actually want to specify and the rest will not be modified'''
    
    df_filtered = dataframe.copy()
    preferences = choose_preferences() # in the future this should be outside of the function
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
        
    if preferences.get('diaryfree') == 'y':
        df_filtered = df_filtered[df_filtered['DiaryFree'] ==1]
        
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
        df_filtered = df_filtered[df_filtered['Quick']==1].reset_index(drop=True)
    if preferences.get('preptime') == 's':
        df_filtered = df_filtered[df_filtered['StandardPrepTime']==1].reset_index(drop=True)
    if preferences.get('preptime') == 'l':
        df_filtered = df_filtered[df_filtered['LongPrepTime']==1].reset_index(drop=True)
    return(df_filtered)

list(df.columns.values) #command to list all the names of the columns

print(df.head(1))
#Now let's get to the daily meal planner

def calories_protein_goals():
    '''Function to specify your daily goal of calories and of protein'''
    calories_protein = [None, None]
    while True:
        try:
            calories = int(input("What is your desired caloric goal for the day? Please enter a number "))
            if calories > 0 and calories < 10000:
                calories_protein[1] = calories
                break
        except ValueError:
            print("Please enter a valid number")
    while True:
        try:
            protein = int(input("What is your desired protein goal for the day? Please enter a number "))
            if protein > 0 and protein < 1000:
                calories_protein[2] = protein
                break
            else:
                print("Please enter a number in the range 0 to 1000 for protein")
        except ValueError:
            print("Please enter a valid number")
    return(calories_protein)

def generate_meal_names(count = 3):
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
        # For 7+ meals, use numbered approach
        return [f"Meal {i+1}" for i in range(count)]
 
def optimal_weights_per_meal(count = 3):
    '''Give appropriate weight to each meal during the day, to assign appropriate amount of calories/protein to each of them'''
    #Defining weights for every possible named meal (see function above)
    meal_weights = {"Breakfast": 3, "Lunch": 4, "Dinner": 4, "Mid-Morning": 2, "Afternoon Snack": 2, "Evening Snack": 2, "Default": 3} 
    meal_slots = generate_meal_names(count)
    meal_plan_weights = {meal: None for meal in meal_slots}
    for meal in meal_plan_weights:
        if meal in meal_weights: #this should somehow get the key and not the value
            meal_plan_weights[meal] = meal_weights[meal] 
        else:
            meal_plan_weights[meal] = meal_weights["Default"]
            
    #calculate the total sum of points
    # total_points = sum(meal_plan_weights.values())
    total_weight = sum(meal_plan_weights.values())
    for meal in meal_plan_weights:
        meal_plan_weights[meal] = round(meal_plan_weights[meal] / total_weight,2) #possibly remove the rounding if I feel like it will make it simpler
    
    return(meal_plan_weights) 
            
def number_of_meals(df_filtered = df, target_calories = 2500, target_protein = 120, max_meals = 6):
    '''Function to estimate the number of meals that would be optimal for given caloric/protein goals
        The function automatically returns the names of the meals, therefore their count is included but not indicated with an integer'''
    
    avg_calories = df_filtered["Calories"].mean()
    avg_protein = df_filtered["ProteinContent"].mean()
    
    estimated_meals_by_cal = min(max_meals, max(2, target_calories // (avg_calories * 0.8)))
    estimated_meals_by_protein = min(max_meals, max(2, target_protein // (avg_protein * 0.8)))
    
    optimal_meals = max(estimated_meals_by_cal, estimated_meals_by_protein)
    
    meal_names = generate_meal_names(optimal_meals)
    
    return(meal_names)

def generate_daily_meal_plan(df_filtered=df, target_calories=2500, target_protein=120, tolerance = 0.2, max_meals = 6): #doesn't the max meal count contradict the use of the number of meals generator?
    '''Generates a daily plan of meals from the filtered recipes dataframe'''
    
    if df_filtered.empty:
        print('There are no recipes to choose! Check your filters and try again')
        return None
    
    # Get meal slots and initialize plan
    meal_slots = number_of_meals(df_filtered, target_calories, target_protein, max_meals)
    meal_plan = {meal: None for meal in meal_slots}
    
    # Calculate targets per meal, the weights could be adjusted
    calories_per_meal = {meal: optimal_weights_per_meal(len(meal_plan))[meal] * target_calories for meal in optimal_weights_per_meal(len(meal_plan))}
    protein_per_meal = {meal: optimal_weights_per_meal(len(meal_plan))[meal] * target_protein for meal in optimal_weights_per_meal(len(meal_plan))}
    
    # Calculate allowable deviations based on tolerance
    deviation_calories = {meal: tolerance * calories_per_meal[meal] for meal in meal_slots}
    deviation_protein = {meal: tolerance * protein_per_meal[meal] for meal in meal_slots}
    
    # Initialize totals
    total_calories = 0
    total_protein = 0
        
    print("🍽️  YOUR DAILY MEAL PLAN")
    print("\n" + "="*60)
    print("="*60)
    
    for meal in meal_slots:
        #Filtering the dataframe for a list of meals that fulfill our criteria, +- standard deviation
        # Calculate remaining targets
        remaining_meals = len([m for m in meal_slots if meal_plan[m] is None])
        remaining_calories = target_calories - total_calories
        remaining_protein = target_protein - total_protein
        
        # Flexible targets for this meal
        target_cal = remaining_calories / remaining_meals if remaining_meals > 0 else calories_per_meal[meal]
        target_prot = remaining_protein / remaining_meals if remaining_meals > 0 else protein_per_meal[meal]
        
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
            print(f"No suitable recipes found for {meal}")
            continue
        
        # Select and assign recipe
        # Get the highest rating
        max_rating = df_suitable['AggregatedRating'].max()

        # Filter for recipes with the highest rating
        top_rated = df_suitable[df_suitable['AggregatedRating'] == max_rating]

        # Randomly select from the top-rated recipes
        selected_recipe = top_rated.sample(n=1).iloc[0]
        meal_plan[meal] = selected_recipe["Name"]
        
        # Update totals
        total_calories += int(selected_recipe["Calories"])
        total_protein += int(selected_recipe["ProteinContent"])
        
        # Optional: Print each meal as it's selected
        print(f"{meal}: {selected_recipe['Name']} ({int(selected_recipe['Calories'])} cal, {int(selected_recipe['ProteinContent'])}g protein)")
            
    print(f"\nTotal calories: {total_calories}")
    print(f"Total protein: {total_protein}")
    return meal_plan