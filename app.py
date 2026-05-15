from click import prompt
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import random
import google.generativeai as genai
app = Flask(__name__)
CORS(app)
df = pd.read_csv('country.csv')
#Prediction logic
def predict_disaster(row):
    drought = (
        row['historical_frequency'] * 0.4 +
        row['population_density'] * 0.002
    )
    tsunami = (
        row['coastal_exposure'] * 100 * 0.7 +
        row['historical_frequency'] * 2
    )
    earthquake = (
        row['historical_frequency'] * 5 +
        (1 - row['infrastructure_index']) * 50
    )
    flood = (
        row['coastal_exposure'] * 80 +
        row['population_density'] * 0.001
    )
    disaster_scores = {
        'Drought': round(drought, 2),
        'Tsunami': round(tsunami, 2),
        'Earthquake': round(earthquake, 2),
        'Flood': round(flood, 2)
    }
    highest_disaster = max(disaster_scores, key=disaster_scores.get)
    return disaster_scores, highest_disaster
#Fall back responses
def get_safety_response(disaster):
    responses = {
        'Drought': [
            'Save water immediately and store packaged food supplies.',
            'Reduce unnecessary water usage and keep emergency food ready.',
            'Prepare for water shortages by storing clean drinking water.'
        ],

        'Tsunami': [
            'Evacuate coastal areas immediately and move to higher ground.',
            'Stay away from beaches and follow emergency evacuation routes.',
            'Keep emergency kits ready and move inland as soon as possible.'
        ],

        'Earthquake': [
            'Stay away from windows and keep emergency medical kits nearby.',
            'Drop, cover, and hold during shaking. Prepare emergency supplies.',
            'Secure heavy furniture and know safe evacuation zones.'
        ],

        'Flood': [
            'Move to elevated areas and avoid flooded roads.',
            'Keep emergency batteries and clean water supplies ready.',
            'Disconnect electrical appliances and stay indoors safely.'
        ]
    }
    return random.choice(responses.get(disaster, ['Stay alert and follow local safety guidelines.']))
@app.route('/')
def home():
    countries = df['country'].tolist()
    return render_template('index.html', countries=countries)
@app.route('/predict', methods=['POST'])
def predict():
    country_name = request.json.get('country')
    row = df[df['country'] == country_name].iloc[0]
    disaster_scores, highest_disaster = predict_disaster(row)
    return jsonify({
        'scores': disaster_scores,
        'highest_disaster': highest_disaster,
        'latitude': row['latitude'],
        'longitude': row['longitude']
    })
@app.route('/chatbot', methods=['POST'])
def chatbot():
    country_name = request.json.get('country')
    row = df[df['country'] == country_name].iloc[0]
    disaster_scores, highest_disaster = predict_disaster(row)
    API_KEY = "api-key"
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        print(response)
        if hasattr(response, "text"):
            bot_reply = response.text
        else:
            bot_reply = get_safety_response(highest_disaster)
    except Exception as e:
        print(e)
        bot_reply = get_safety_response(highest_disaster)
    return jsonify({
        'response': bot_reply,
        'highest_disaster': highest_disaster
    })
if __name__ == '__main__':
    app.run(debug=True)