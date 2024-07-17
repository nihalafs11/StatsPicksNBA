import os
from django.conf import settings

from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
import numpy as np

pypath =  os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'mlmodels')

class NNMLPRegressor:
    def __init__(self, hidden_layer_sizes=(50,50), alpha=0.0001):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.alpha = alpha
        
        self.X = None
        self.y = None
        self.model = None
    
    def fit(self, X, y):
        self.model = MLPRegressor(hidden_layer_sizes=self.hidden_layer_sizes, alpha=self.alpha)
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
                    'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 100)],
                    'alpha': [0.0001, 0.001, 0.01]
        } 
        model = MLPRegressor(max_iter=10000)
        grid = GridSearchCV(model, parameters, cv=10)
        grid.fit(self.X, self.y)

        with open(os.path.join(pypath, "mlpregressor_optimize.txt"), "w+") as file:
            parameter_string = ",".join(f"{key}={value}" for key, value in grid.best_params_.items())
            file.write(parameter_string)
