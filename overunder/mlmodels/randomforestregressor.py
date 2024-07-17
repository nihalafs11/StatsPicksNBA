import os
from django.conf import settings

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score

pypath =  os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'mlmodels')

class RandForestRegressor:
    def __init__(self, max_depth=10, min_samples_leaf=4, min_samples_split=10, n_estimators=100):
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.min_samples_split = min_samples_split
        self.n_estimators = n_estimators
        self.X = None
        self.y = None
        self.model = None
    
    def fit(self, X, y):
        self.model = RandomForestRegressor(max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf, min_samples_split=self.min_samples_split, n_estimators=self.n_estimators)
        self.model.fit(X, y)
        self.X = X
        self.y = y
        
    def predict(self, X_pred):
        y_pred = self.model.predict(X_pred)
        return y_pred
    
    def get_score(self):
        score = cross_val_score(self.model, self.X, self.y, scoring="neg_mean_squared_error")
        return abs(score.mean())
    
    def output_optimized_parameters(self):
        parameters = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
        }
        model = RandomForestRegressor()
        grid = GridSearchCV(model, parameters, cv=10)
        grid.fit(self.X, self.y)

        with open(os.path.join(pypath, "randomforest_optimize.txt"), "w+") as file:
            parameter_string = ",".join(f"{key}={value}" for key, value in grid.best_params_.items())
            file.write(parameter_string)