# Diet Recommendation App - Next Steps Roadmap

## 🎯 Current Status Assessment

**SOLID FOUNDATION IN PROGRESS!** You have made excellent progress on data preparation and project structure:

✅ **Comprehensive EDA**: 960K+ recipes analyzed with statistical rigor
✅ **Data Cleaning**: Outlier removal completed (477K clean recipes retained)
✅ **Feature Engineering**: 12 MVP categories encoded and exported
✅ **Modular Structure**: Professional Python package structure implemented
✅ **Data Export**: Automated MVP dataset export pipeline created
✅ **Development Environment**: Requirements files and virtual environment configured

**MVP Features Successfully Encoded (12 total):**
- **Dietary**: Easy, Vegan, Vegetarian, GlutenFree, DairyFree (5 features)
- **Time-based**: Quick, StandardPrepTime, LongPrepTime (3 features)  
- **Nutritional**: LowCal, ModCal, HighCal, HighProtein (4 features)

**Current Blockers Before Streamlit Development:**
⚠️ **Empty Core Modules**: `settings.py`, `loaders.py`, `recommender.py` scaffolded but empty
⚠️ **Non-Production Code**: Logic exists only in prototype scripts
⚠️ **No Test Coverage**: Testing framework set up but no tests implemented

## 🚀 Immediate Next Steps (Week 1-2)

### Priority 1: Core Module Implementation (CRITICAL BLOCKER)

#### 1.1 Implement Data Loader Module
Create production-ready data loading in `src/diet_app/data/loaders.py`:
```python
# Essential: Load and validate MVP dataset
# Features: Recipe search, filtering, nutritional lookup
# Convert from prototype script to modular functions
```

#### 1.2 Implement Configuration Module  
Set up `src/diet_app/config/settings.py`:
```python
# Application settings and constants
# Feature weights and recommendation parameters
# Database/file paths configuration
```

#### 1.3 Implement Basic Recommender
Convert `scripts/recommendation_engine.py` to `src/diet_app/models/recommender.py`:
```python
# Move content-based filtering logic
# Make recommendation functions modular and testable
# Add input validation and error handling
```

#### 1.4 Create Basic Tests
Implement `tests/test_basic_functionality.py`:
```python
# Test data loading from MVP dataset
# Test recommendation generation
# Validate filter functionality
```
```python
# Export MVP dataset for application development
mvp_df.to_csv('../data/mvp_recipes_clean.csv', index=False)
mvp_df.to_pickle('../data/mvp_recipes_clean.pkl')  # Faster loading

# Export feature metadata
feature_metadata = {
    'total_recipes': len(mvp_df),
    'features': mvp_features,
    'feature_counts': {feature: int(mvp_df[feature].sum()) for feature in mvp_features},
    'nutritional_columns': ['Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent'],
    'created_date': datetime.now().isoformat()
### Priority 2: Streamlit Readiness Validation (Week 2)

#### 2.1 Test Core Functionality
Validate that modules work before Streamlit development:
```bash
# Test data loading
python -c "from src.diet_app.data.loaders import RecipeDataLoader; loader = RecipeDataLoader(); df = loader.load_mvp_dataset(); print(f'Loaded {len(df)} recipes')"

# Test recommendation generation  
python -c "from src.diet_app.models.recommender import ContentBasedRecommender; rec = ContentBasedRecommender(); recs = rec.get_recommendations({'Easy': True}, limit=5); print(f'Generated {len(recs)} recommendations')"
```

#### 2.2 Performance Validation
Ensure sub-2-second recommendation generation:
```python
import time
start = time.time()
recommendations = recommender.get_recommendations(user_prefs, limit=10)
duration = time.time() - start
assert duration < 2.0, f"Too slow: {duration:.2f}s"
```

#### 2.3 Create Integration Tests
**File: `tests/test_integration.py`**
```python
def test_full_recommendation_pipeline():
    # Load data -> Apply filters -> Generate recommendations
    # Verify end-to-end functionality works
    pass

def test_data_consistency():
    # Verify MVP dataset loads correctly
    # Check feature counts and data types
    pass
```
    
    def filter_by_nutrition(self, 
                          max_calories: Optional[int] = None,
                          min_protein: Optional[int] = None) -> pd.DataFrame:
        """Filter by nutritional constraints"""
        filtered_df = self.df.copy()
        
        if max_calories:
            filtered_df = filtered_df[filtered_df['Calories'] <= max_calories]
        
        if min_protein:
            filtered_df = filtered_df[filtered_df['ProteinContent'] >= min_protein]
            
        return filtered_df
```

### Priority 3: Basic Recommendation Engine

#### 3.1 Create Content-Based Recommender
**File: `src/diet_app/models/content_based.py`**
```python
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple

class ContentBasedRecommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.feature_columns = [
            'Easy', 'Vegan', 'Vegetarian', 'GlutenFree', 'DairyFree',
            'Quick', 'StandardPrepTime', 'LongPrepTime',
            'LowCalorie', 'ModerateCalorie', 'HighCalorie',
            'LowProtein', 'ModerateProtein', 'HighProtein'
        ]
        self.nutritional_columns = ['Calories', 'ProteinContent', 'FatContent']
        self.scaler = StandardScaler()
        self._prepare_features()
    
    def _prepare_features(self):
        """Prepare feature matrix for similarity calculation"""
        # Combine categorical and numerical features
        categorical_features = self.df[self.feature_columns]
        
        # Normalize nutritional features
        nutritional_features = self.scaler.fit_transform(
            self.df[self.nutritional_columns]
        )
        nutritional_df = pd.DataFrame(
            nutritional_features, 
            columns=self.nutritional_columns,
            index=self.df.index
        )
        
        # Combine all features
        self.feature_matrix = pd.concat([
            categorical_features, nutritional_df
        ], axis=1)
    
    def get_similar_recipes(self, 
                          recipe_id: str, 
                          n_recommendations: int = 10) -> List[Dict]:
        """Get similar recipes based on content features"""
        if recipe_id not in self.df['RecipeId'].values:
            return []
        
        # Get recipe index
        recipe_idx = self.df[self.df['RecipeId'] == recipe_id].index[0]
        
        # Calculate similarity
        similarities = cosine_similarity(
            [self.feature_matrix.iloc[recipe_idx]], 
            self.feature_matrix
        )[0]
        
        # Get top similar recipes (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            recipe = self.df.iloc[idx]
            recommendations.append({
                'recipe_id': recipe['RecipeId'],
                'name': recipe['Name'],
                'calories': recipe['Calories'],
                'protein': recipe['ProteinContent'],
                'similarity_score': similarities[idx],
                'rating': recipe.get('AggregatedRating', 0)
            })
        
        return recommendations
    
    def recommend_by_preferences(self, 
                                user_preferences: Dict,
                                n_recommendations: int = 10) -> List[Dict]:
        """Recommend recipes based on user preferences"""
        # Create user preference vector
        user_vector = np.zeros(len(self.feature_matrix.columns))
        
        # Set dietary preferences
        for pref in user_preferences.get('dietary', []):
            if pref in self.feature_columns:
                col_idx = self.feature_matrix.columns.get_loc(pref)
                user_vector[col_idx] = 1
        
        # Set time preference
        time_pref = user_preferences.get('time_preference')
        if time_pref in self.feature_columns:
            col_idx = self.feature_matrix.columns.get_loc(time_pref)
            user_vector[col_idx] = 1
        
        # Calculate similarities
        similarities = cosine_similarity([user_vector], self.feature_matrix)[0]
        
        # Get top recommendations
        top_indices = np.argsort(similarities)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            recipe = self.df.iloc[idx]
            recommendations.append({
                'recipe_id': recipe['RecipeId'],
                'name': recipe['Name'],
                'calories': recipe['Calories'],
                'protein': recipe['ProteinContent'],
                'similarity_score': similarities[idx],
                'rating': recipe.get('AggregatedRating', 0)
            })
        
        return recommendations
```

## 🎯 Phase 1 Goals (Next 2 Weeks)

**FOUNDATION COMPLETION BEFORE STREAMLIT**

### Week 1: Core Module Implementation (CRITICAL)
- [x] ✅ Export clean MVP dataset from notebook (COMPLETED)
- [x] ✅ Create modular project structure (COMPLETED)
- [x] ✅ Set up proper Python package with requirements (COMPLETED)
- [ ] 🧪 **Implement empty core modules** (loaders.py, recommender.py, settings.py)
- [ ] 📊 **Convert prototype logic to production modules**
- [ ] ✅ **Write and pass basic unit tests**

### Week 2: Streamlit Readiness Validation
- [ ] 🤖 **Test recommendation generation** (sub-2-second performance)
- [ ] 🔍 **Validate data loading pipeline** (477K recipes load correctly)
- [ ] 📊 **Integration testing** (end-to-end recommendation flow)
- [ ] 🚀 **Streamlit development can begin** (all blockers resolved)

### Success Criteria (Must Pass Before Streamlit):
```bash
# These commands must work without errors:
python -c "from src.diet_app.data.loaders import load_mvp_dataset; print('✅ Data loading works')"
python -c "from src.diet_app.models.recommender import get_recommendations; print('✅ Recommendations work')" 
pytest tests/ -v  # All tests pass
```
- [ ] 🧪 Test recommendation quality with sample data
- [ ] 📝 Document API design for recommendation service

## 🔄 Development Workflow

### Daily Development Process
1. **Start with tests**: Write tests before implementing features
2. **Small iterations**: Focus on one module at a time  
3. **Data validation**: Always validate data pipeline outputs
4. **Performance monitoring**: Track recommendation latency
5. **Documentation**: Update README with setup instructions

### Key Performance Targets
- **Data Loading**: < 2 seconds for MVP dataset
- **Recommendation Generation**: < 500ms for 10 recommendations
- **Feature Coverage**: Support all 14 MVP encoded features
- **Code Quality**: 90%+ test coverage, linting compliance

## 🚀 Next Phase Preview (Weeks 3-4) 

**ONLY AFTER FOUNDATION IS COMPLETE**

### Phase 2A: Streamlit Development (Week 3)
- **User Interface**: Recipe browsing and recommendation display
- **Preference Collection**: Dietary/time/nutritional preference forms
- **Real-time Recommendations**: Interactive filtering and suggestions
- **Performance Optimization**: Caching and response time optimization

### Phase 2B: Advanced Features (Week 4)
- **Search Interface**: Text and filter-based recipe search
- **Nutritional Analysis**: Detailed macro/micronutrient breakdowns
- **User Feedback**: Recipe rating and favorite functionality
- **Meal Planning**: Weekly meal plan generation

## 💡 Pro Tips for Foundation Phase

### Critical Development Priorities
1. **Module Implementation First**: Focus on core functionality before UI
2. **Test-Driven Development**: Write tests that prove modules work
3. **Performance Validation**: Ensure sub-2-second recommendation times
4. **Data Integrity**: Validate that all 477K recipes load correctly
5. **Clean Interfaces**: Design functions for easy Streamlit integration

### Avoiding Common Pitfalls
- **Don't skip module implementation** - Streamlit will fail without working core
- **Don't optimize prematurely** - Get basic functionality working first
- **Don't ignore testing** - Bugs compound quickly in recommendation systems
- **Don't rush to UI** - Strong foundation enables rapid UI development

## 📈 Foundation Completion Checklist

### Technical Validation (Must Complete)
- [ ] **Data Loading**: `load_mvp_dataset()` function returns 477,443 recipes
- [ ] **Recommendation Generation**: Content-based filtering produces ranked results
- [ ] **Filter Application**: Dietary/time preferences correctly filter recipes  
- [ ] **Performance**: Recommendation generation completes in <2 seconds
- [ ] **Testing**: Core functionality covered by unit and integration tests

### Code Quality Standards
- [ ] **Modular Design**: Functions can be imported and used independently
- [ ] **Error Handling**: Graceful handling of missing data and edge cases
- [ ] **Documentation**: Clear docstrings and usage examples
- [ ] **Type Hints**: Functions properly typed for IDE support
- [ ] **Consistent Style**: Code formatted with black/isort

---

## 🎯 **IMMEDIATE ACTION ITEMS** (This Week)

### Day 1-2: Module Implementation
1. **Implement `src/diet_app/data/loaders.py`** - Convert data loading to production code
2. **Implement `src/diet_app/models/recommender.py`** - Convert recommendation logic to modular functions
3. **Implement `src/diet_app/config/settings.py`** - Application configuration and constants 
3. **Set up proper requirements.txt** with essential dependencies
4. **Implement the data loading module**
5. **Write your first unit tests**

### Day 3-4: Testing and Validation
4. **Implement `tests/test_basic_functionality.py`** - Core functionality tests
5. **Performance Testing** - Validate <2-second recommendation generation
6. **Integration Testing** - End-to-end pipeline validation

### Day 5: Streamlit Readiness Check
7. **Run Foundation Tests** - All tests must pass before proceeding
8. **Performance Benchmarking** - Document actual recommendation times
9. **Ready for Streamlit Development** - Green light to begin UI work

**Your foundation work is nearly complete. Focus on module implementation first!** 🚀

---

*Last Updated: December 19, 2024*
*Status: Foundation In Progress - Core Modules Need Implementation*
