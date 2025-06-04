import pandas as pd
import numpy as np
import math
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

def generate_daily_meal_plan(df_filtered = df): #fix this function next
    '''Generates a daily plan of meals from the filtered recipes dataframe'''
    
    if df_filtered.empty: #czy to jest dobry sposob na wpisanie pustego df'a?
        print('There are no recipes to choose! Check your filters and try again')
        return None
    
    meal_slots = ['Breakfast', 'Lunch', 'Dinner'] #Consider more flex here
    meal_plan = {}
    meal_plan = meal_plan.fromkeys(meal_slots)
    
    for meal in meal_plan.keys():
        #For now I will implement randomly choosing meals from the filtered df
        r = random.randint(1, len(df_filtered))
        print(r)
        meal_plan.update({"meal": df_filtered.loc[r, "Name"]})
    return(meal_plan)
    
    
df.loc[1030, "Name"]