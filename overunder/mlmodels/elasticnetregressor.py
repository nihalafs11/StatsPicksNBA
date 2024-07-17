import os
from django.conf import settings
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, cross_val_score
import numpy as np

pypath =  os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'mlmodels')

class ENet:
    def __init__(self, alpha=1, l1_ratio=0.90, tol=0.001):
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.tol = tol
        
        self.X = None
        self.y = None
        self.model = None
    
    def fit(self, X, y):
        self.model = ElasticNet(alpha=self.alpha, l1_ratio=self.l1_ratio, tol=self.tol)
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
                    'alpha': [1.0, 0.1, 0.01],
                    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
            }
        model = ElasticNet(max_iter=10000)
        grid = GridSearchCV(model, parameters, cv=10)
        grid.fit(self.X, self.y)

        with open(os.path.join(pypath, "elasticnet_regressor.txt"), "w+") as file:
            parameter_string = ",".join(f"{key}={value}" for key, value in grid.best_params_.items())
            file.write(parameter_string)
