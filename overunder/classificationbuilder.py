import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'statspicksnba.settings')
django.setup()

from .mlmodels.elasticnetregressor import ENet
from .objects.datahandler import DataHandler
from sklearn.linear_model import LogisticRegression
from .misc.helperfunctions import get_seasons
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from .objects.team import Team
import pandas as pd
import pickle
import numpy as np


csv_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'csvs')
picklepath = os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'modelspickle')

print("Test 1:", csv_path)
print("Test 2:", picklepath)


def build_csv():
    df = pd.read_csv(os.path.join(csv_path, "predicted_points_empty.csv"), index_col=False)

    dh = DataHandler()
    dh.load_data(update_team=False)
    dh.set_X_y()

    X = dh.X
    y = dh.y

    model = ENet()
    model.fit(X, y)

    for i in range(len(df)):
        cur_game = df.iloc[[i]]
        cur_season = get_seasons()[0]
        
        team_away_name = cur_game["TEAM_AWAY"].values[0]
        team_home_name = cur_game["TEAM_HOME"].values[0]
        
        team_away = Team().set_team(season=cur_season, name=team_away_name)
        team_home = Team().set_team(season=cur_season, name=team_home_name)
        
        combined_stats = pd.concat([team_away.stats.add_suffix("_A"), team_home.stats.add_suffix("_H")], axis=1)
        
        X_pred = dh.get_X_pred(team_away_name, team_home_name)
        y_pred = model.predict(X_pred)
        
        df.loc[i, "PREDICTED"] = y_pred
        df.loc[i, combined_stats.columns] = combined_stats.iloc[0].values
        
    df = df.drop(["TEAM_AWAY", "TEAM_HOME", "TEAM_NAME_A", "TEAM_ID_A", "GP_A", "W_A", "L_A", "SEASON_A",
             "TEAM_NAME_H", "TEAM_ID_H", "GP_H", "W_H", "L_H", "SEASON_H", "TOTAL_POINTS"], axis=1)

    # df = df.drop(["TEAM_AWAY", "TEAM_HOME", "TOTAL_POINTS"], axis=1)
        
    df.to_csv(os.path.join(csv_path, "predicted_points.csv"), index=False)


if __name__ == "__main__":
    build_csv()
    df = pd.read_csv(os.path.join(csv_path, "predicted_points.csv"), index_col=False)
    
    dh = DataHandler()
    dh.load_data()
    
    X = df.drop(["OVER"], axis=1)
    y = df["OVER"]
    
    # model = LogisticRegression(C=3, penalty="l2", solver="liblinear").fit(X, y)
    # model = GradientBoostingClassifier(learning_rate=0.1, max_depth=3, min_samples_leaf=2, min_samples_split=5, n_estimators=50, subsample=0.6).fit(X, y)
    model = LogisticRegression(C=125, penalty="l2", solver="newton-cg").fit(X, y)
    
    # FOR OPTIMIZING CLASSIFICATION MODEL
    # LOGISTIC REGRESSION MODEL
    # OPTIMIZED PARAMETERS: {'C': 3, 'penalty': 'l2', 'solver': 'liblinear'}
    # OPTIMIZED PARAMETERS 2: {'C': 10000.0, 'max_iter': 10000000, 'penalty': 'l2', 'solver': 'newton-cg'}
    # parameters = {
    #     "penalty" : ["l1", "l2", "elasticnet", "none"],
    #     "C" : np.logspace(-4, 4, 20),
    #     "solver" : ["lbfgs","newton-cg","liblinear","sag","saga"],
    #     "max_iter": [10000000]
    # }

    # GRADIENT BOOSTING CLASSIFIER
    # OPTIMIZED PARAMETERS: {'learning_rate': 0.1, 'max_depth': 3, 'min_samples_leaf': 2, 'min_samples_split': 5, 'n_estimators': 50, 'subsample': 0.6}
    # parameters = {
    #     "learning_rate": [0.05, 0.1, 0.2],
    #     "n_estimators": [50, 100, 200],
    #     "max_depth": [3, 5, 8],
    #     "min_samples_split": [2, 5, 10],
    #     "min_samples_leaf": [1, 2, 4],
    #     "subsample": [0.6, 0.8, 1.0]
    # }

    # SVC
    # OPTIMIZED PARAMETERS: {'C': 0.5, 'gamma': 0.001}
    # parameters = {
    #     "C": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],  
    #     "gamma": [.001, .01, .1, 1, 10, 100, 1000],
    # }
    
    # RANDOM FOREST CLASSIFIER
    # OPTIMIZED PARAMETERS: {'bootstrap': False, 'max_depth': 20, 'max_features': 'sqrt', 'min_samples_leaf': 2, 'min_samples_split': 2, 'n_estimators': 200}
    # parameters = {
    #     'bootstrap': [True, False],
    #     'max_depth': [10, 20, None],
    #     'max_features': ['sqrt'],
    #     'min_samples_leaf': [1, 2, 4],
    #     'min_samples_split': [2, 5, 10],
    #     'n_estimators': [200, 400, 600]
    # }

    # grid = GridSearchCV(model, parameters, verbose=2)
    # grid.fit(X, y)
    # print(grid.best_params_)
    
    # model = LogisticRegression(**grid.best_params_).fit(X, y)
    
    accuracy = cross_val_score(model, X, y, scoring="accuracy")
    precision = cross_val_score(model, X, y, scoring="precision")
    f1 = cross_val_score(model, X, y, scoring="f1")
    
    print("Classification Cross Validation Results:")
    print(f"Accuracy: {accuracy.mean()*100:.2f}%")
    print(f"Precision: {precision.mean()*100:.2f}%")
    print(f"F1 Score: {f1.mean()*100:.2f}%")
    
    with open(os.path.join(picklepath, "team_overunder_classifier.pkl"), "wb") as f:
         pickle.dump(model, f)
