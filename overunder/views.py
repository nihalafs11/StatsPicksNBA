import pickle
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .forms import PredictionForm
from django.shortcuts import get_object_or_404
from .objects.datahandler import DataHandler
from .models import TeamData



regressor = None
classifier = None

def load_models():
    global regressor, classifier
    try:
        regressor_path =  os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'modelspickle', 'team_overunder_regressor.pkl')
        classifier_path =  os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'modelspickle', 'team_overunder_classifier.pkl')
        
        with open(regressor_path, 'rb') as f:
            regressor = pickle.load(f)
        with open(classifier_path, 'rb') as f:
            classifier = pickle.load(f)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Failed to load models: {e}")
        regressor = classifier = None

def get_regressor_classifier():
    global regressor, classifier
    if regressor is None or classifier is None:
        load_models()
    return regressor, classifier

def index(request):
    form = PredictionForm(request.POST or None)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        regressor, classifier = get_regressor_classifier()
        if regressor is None or classifier is None:
            return JsonResponse({'error': "Models are not loaded."})
        team_away_input = request.POST.get('team_away_name')
        team_home_input = request.POST.get('team_home_name')
        vegas_line = float(request.POST.get('vegas_line', 0))
        
        dh = DataHandler()
        dh.load_data()
        dh.set_X_y()
        
        X_pred = dh.get_X_pred(team_away_input, team_home_input)
        if X_pred is not False:
            y_pred_regressor = regressor.predict(X_pred)[0]
            
            X_pred_classifier = X_pred.copy()
            X_pred_classifier.insert(0, "PREDICTED", [y_pred_regressor])
            X_pred_classifier.insert(0, "VEGAS_LINE", [vegas_line])
            
            y_pred_probability = classifier.predict_proba(X_pred_classifier)[0]
            y_pred_classification = classifier.predict(X_pred_classifier)[0]
            
            response_data = {
                'match_up': f"{dh.team_away.info.nickname[0].capitalize()} vs {dh.team_home.info.nickname[0].capitalize()}",
                'predicted_points': f"{y_pred_regressor:.2f} points",
                'percent_diff': f"{(y_pred_regressor/vegas_line-1)*100:.2f}%",
                'line': 'Over' if y_pred_classification else 'Under',
                'probability': f"{y_pred_probability[1 if y_pred_classification else 0]*100:.2f}%"
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': "Invalid team names provided."})
    
    context = {'form': form}
    return render(request, 'index.html', context)

def get_team_logo(request):
    team_input = request.GET.get('team_input')
    if team_input.isdigit():
        team = get_object_or_404(TeamData, pk=team_input)
    else:
        team = get_object_or_404(TeamData, team_input=team_input)  
    logo_url = f"{request.build_absolute_uri('/static/nba_team_logos/')}{team.logo}"
    return JsonResponse({'logo_url': logo_url}, safe=False)
