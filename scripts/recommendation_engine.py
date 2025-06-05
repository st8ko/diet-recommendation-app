import pandas as pd
import numpy as np
import random

df = pd.read_csv('data/mvp_recipes_clean.csv')
print(df.head())

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
        ("Do you want your meals vegan? (y/n): ", ['y', 'n'], 'vegan'),
        ("Do you want your meals easy? (y/n): ", ['y', 'n'], 'easy'),
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
        df_filtered = df_filtered[df_filtered['Quick']==1].reset_index(drop=True)
    if preferences.get('preptime') == 's':
        df_filtered = df_filtered[df_filtered['StandardPrepTime']==1].reset_index(drop=True)
    if preferences.get('preptime') == 'l':
        df_filtered = df_filtered[df_filtered['LongPrepTime']==1].reset_index(drop=True)
    return(df_filtered)

list(df.columns.values) #command to list all the names of the columns

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

def generate_meal_names(count):
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
            
def number_of_meals(df_filtered = df, target_calories = 2500, target_protein = 120, max_meals = 6):
    '''Function to estimate the number of meals that would be optimal for given caloric/protein goals'''
    
    avg_calories = df_filtered["Calories"].mean()
    avg_protein = df_filtered["ProteinContent"].mean()
    
    



def generate_daily_meal_plan(df_filtered = df): #make this more flexible -> hit protein and caloric goals & dynamically select number of meals during the day
    '''Generates a daily plan of meals from the filtered recipes dataframe'''
    
    if df_filtered.empty: #czy to jest dobry sposob na wpisanie pustego df'a?
        print('There are no recipes to choose! Check your filters and try again')
        return None
    
    meal_slots = ['Breakfast', 'Lunch', 'Dinner'] #Consider more flex here
    meal_plan = {meal: None for meal in meal_slots}
    meal_plan = meal_plan.fromkeys(meal_slots)
    
    calories = 0
    protein = 0
    
    print("\n" + "="*60)
    print("🍽️  YOUR DAILY MEAL PLAN")
    print("="*60)
    
    for meal in meal_plan.keys():
        #For now I will implement randomly choosing meals from the filtered df
        r = random.randint(1, len(df_filtered))

        selected_meal = df_filtered.iloc[r]["Name"]
        meal_calories = int(df_filtered.iloc[r]["Calories"])
        meal_protein = int(df_filtered.iloc[r]["ProteinContent"])
        
        meal_plan.update({meal: selected_meal})
        
        print(f"\n🌅 {meal.upper()}")
        print(f"   📝 {selected_meal}")
        print(f"   🔥 {meal_calories} calories")
        print(f"   💪 {meal_protein}g protein")
        
        calories += meal_calories
        protein += meal_protein
    print("Our total calorie count for the day is ", calories)
    print("Our total protien count for the day is ", protein)
    return(meal_plan)


### Do something about the fact that the meals have so little protein (?)
