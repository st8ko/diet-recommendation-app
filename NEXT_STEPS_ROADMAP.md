# Diet Recommendation App - Next Steps Roadmap

## 🎯 Current Status Assessment

**EXCELLENT PROGRESS!** Your MVP dataset preparation is now complete. You have successfully:

✅ **Comprehensive EDA**: 960K+ recipes analyzed with statistical rigor
✅ **Data Cleaning**: Outlier removal and quality validation completed  
✅ **Feature Engineering**: 14 MVP categories encoded and validated
✅ **Dataset Ready**: Clean 516K recipe dataset prepared for application development

**MVP Features Successfully Encoded:**
- **Dietary**: Easy, Vegan, Vegetarian, GlutenFree, DairyFree (5 features)
- **Time-based**: Quick, StandardPrepTime, LongPrepTime (3 features)  
- **Nutritional**: Low/Moderate/High for Calories, Protein, Fat (6 features)

## 🚀 Immediate Next Steps (Week 1-2)

### Priority 1: Project Structure & Environment Setup

#### 1.1 Create Professional Project Structure
```bash
# Create modular Python package structure
mkdir -p src/diet_app/{config,data,models,api,web,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p scripts
mkdir -p requirements
touch src/diet_app/__init__.py
touch src/diet_app/{config,data,models,api,web,utils}/__init__.py
```

#### 1.2 Set Up Development Environment  
```bash
# Create proper requirements files
pip freeze > requirements/base.txt

# Add essential dependencies
echo "fastapi>=0.104.0" >> requirements/base.txt
echo "streamlit>=1.28.0" >> requirements/base.txt
echo "scikit-learn>=1.3.0" >> requirements/base.txt
echo "pydantic>=2.5.0" >> requirements/base.txt

# Development dependencies
echo "black>=23.9.1" >> requirements/dev.txt
echo "pytest>=7.4.0" >> requirements/dev.txt
echo "flake8>=6.1.0" >> requirements/dev.txt
```

#### 1.3 Export Clean MVP Dataset
Add this to your notebook to save the clean dataset:
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
}

import json
with open('../data/mvp_metadata.json', 'w') as f:
    json.dump(feature_metadata, f, indent=2)
```

### Priority 2: Data Processing Pipeline (Modular)

#### 2.1 Create Data Loading Module
**File: `src/diet_app/data/loaders.py`**
```python
import pandas as pd
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import json

class RecipeDataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def load_mvp_dataset(self) -> pd.DataFrame:
        """Load the clean MVP dataset"""
        pkl_path = self.data_dir / "mvp_recipes_clean.pkl"
        if pkl_path.exists():
            return pd.read_pickle(pkl_path)
        
        csv_path = self.data_dir / "mvp_recipes_clean.csv"
        return pd.read_csv(csv_path)
    
    def load_metadata(self) -> Dict:
        """Load feature metadata"""
        with open(self.data_dir / "mvp_metadata.json") as f:
            return json.load(f)
    
    def get_feature_names(self) -> List[str]:
        """Get list of MVP feature names"""
        metadata = self.load_metadata()
        return metadata['features']
```

#### 2.2 Create Recipe Filtering Module  
**File: `src/diet_app/data/filters.py`**
```python
import pandas as pd
from typing import Dict, List, Optional

class RecipeFilter:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def filter_by_dietary_preferences(self, 
                                    dietary_prefs: List[str]) -> pd.DataFrame:
        """Filter recipes by dietary preferences"""
        if not dietary_prefs:
            return self.df
            
        dietary_features = ['Vegan', 'Vegetarian', 'GlutenFree', 'DairyFree']
        active_features = [pref for pref in dietary_prefs if pref in dietary_features]
        
        mask = True
        for feature in active_features:
            mask = mask & (self.df[feature] == 1)
        
        return self.df[mask]
    
    def filter_by_time_constraint(self, time_pref: str) -> pd.DataFrame:
        """Filter by cooking time preference"""
        time_mapping = {
            'quick': 'Quick',
            'standard': 'StandardPrepTime', 
            'long': 'LongPrepTime'
        }
        
        if time_pref in time_mapping:
            feature = time_mapping[time_pref]
            return self.df[self.df[feature] == 1]
        
        return self.df
    
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

### Week 1: Foundation Setup
- [ ] ✅ Export clean MVP dataset from notebook
- [ ] 📁 Create modular project structure
- [ ] 🐍 Set up proper Python package with requirements
- [ ] 🧪 Create basic data loading and filtering modules
- [ ] ✅ Write unit tests for data modules

### Week 2: Basic Recommendation Engine  
- [ ] 🤖 Implement content-based recommendation algorithm
- [ ] 🔍 Create recipe search functionality
- [ ] 📊 Build basic evaluation metrics
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

After completing the foundation, you'll move to:

### Phase 2A: Web Interface (Streamlit MVP)
- **User Interface**: Basic Streamlit app for recipe browsing
- **Preference Collection**: UI for dietary/time preferences  
- **Recommendation Display**: Interactive recipe cards
- **Search Interface**: Text and filter-based recipe search

### Phase 2B: API Development (FastAPI)
- **REST Endpoints**: Recipe search, recommendations, preferences
- **Data Validation**: Pydantic models for API contracts
- **Performance**: Caching layer for frequent queries
- **Documentation**: Auto-generated API docs

## 💡 Pro Tips for Success

### Technical Best Practices
1. **Start Simple**: Get basic functionality working before optimization
2. **Test Early**: Write tests as you develop, not after
3. **Version Control**: Commit frequently with descriptive messages
4. **Performance First**: Profile code early to identify bottlenecks
5. **User-Centric**: Always think about the end-user experience

### Project Management Approach
- **Time-box tasks**: Set 2-hour maximum per feature implementation
- **Daily standup**: Review progress against roadmap daily
- **Weekly demo**: Show working features weekly (even to yourself)
- **Iterate quickly**: Get feedback early and often
- **Document decisions**: Keep a development journal

## 📈 Success Metrics

### Technical Milestones
- [ ] Clean dataset exported and validated
- [ ] Modular codebase with 90%+ test coverage
- [ ] Basic recommendation engine producing results  
- [ ] API endpoints responding < 500ms
- [ ] Streamlit interface functional end-to-end

### Business Validation
- [ ] Recommendation quality validated with sample users
- [ ] Recipe diversity maintained across different preferences
- [ ] System handles edge cases gracefully
- [ ] Performance acceptable for expected user load
- [ ] Documentation sufficient for future development

---

## 🎯 **IMMEDIATE ACTION ITEMS** (Today)

1. **Export your clean dataset** from the notebook
2. **Create the modular project structure** 
3. **Set up proper requirements.txt** with essential dependencies
4. **Implement the data loading module**
5. **Write your first unit tests**

**Your data foundation is solid. Now it's time to build the application!** 🚀

---

*Last Updated: June 4, 2025*
*Status: Ready for Phase 1 Implementation*
