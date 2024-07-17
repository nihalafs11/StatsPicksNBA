from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn import metrics 


class LinearRegressor:
    def __init__(self):
        self.X = None
        self.y = None
        self.model = LinearRegression()

    def fit(self, X, y):
        self.X = X
        self.y = y
        self.model.fit(X, y) 

    def predict(self, X_pred):
        y_pred = self.model.predict(X_pred)
        return y_pred
    
    def get_score(self):
        score = cross_val_score(self.model, self.X, self.y, scoring="neg_mean_squared_error")
        return abs(score.mean())
