from flask import Flask, render_template, request
from flask_cors import CORS
import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "PLACE THE API KEY HERE"       

token_response = requests.post("https://iam.cloud.ibm.com/identity/token",data = {
    "apikey":API_KEY , "grant_type":"urn:ibm:params:oauth:grant-type:apikey"
})

mltoken = token_response.json()["access_token"]

header = {"Content-Type" : "application/json" , "Authorization" : "Bearer " + mltoken}


app = Flask(__name__,static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# No cacheing at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

CORS(app)

@app.route('/',methods=['GET','POST'])
def sendHomePage():
    if(request.method == "GET"):
        return render_template('index.html' , notification = 'Welcome!')
    else:
        return render_template('index.html' , notification = 'You have given ' + request.form['rating'] + ' Stars Feedback')

@app.route('/predict',methods=['POST'])
def PredictPossibility():
    GREScore = float(request.form['GREScore'])
    TOEFLScore = float(request.form['TOEFLScore'])
    UnivRating = float(request.form['UnivRating'])
    SOP = float(request.form['SOP'])
    LOR = float(request.form['LOR'])
    CGPA = float(request.form['CGPA'])
    Research = 0
    if('Research' in request.form):
        Research = 1
    X = [[GREScore , TOEFLScore , UnivRating , SOP , LOR , CGPA , Research ]]
    print(X)
    # NOTE: manually define and pass the array(s) of values to be scored in the next line
    payload_scoring = {"input_data": [{"fields": [["GREScore","TOEFLScore","UnivRating","SOP","LOR","CGPA","Research"]], "values": X}]}
    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/1b254abd-eaec-4f59-9e86-a3674f3eea4c/predictions?version=2022-11-15', json=payload_scoring,
    headers=header)
    print("Scoring response")
    print(response_scoring.json())
    probability = int(round((response_scoring.json()["predictions"][0]["values"][0][0]),2)*100)
    print(probability)
    prob_comment = ""
    color_scheme = ""
    if(probability > 100):
        probability = 100
    elif(probability < 0):
        probability = 0
    if(probability < 50):
        prob_comment = "The Chances of Getting an Admission is less likely"
        color_scheme = 'darkorange'
    elif(probability < 70):
        prob_comment = "There is a slight Chance of Possibility."
        color_scheme = 'yellow'
    else:
        prob_comment = "There is High Chances of Possibility"
        color_scheme = 'lawngreen'
    return render_template('predict.html',predict=probability,comment=prob_comment,color_scheme=color_scheme)

if __name__ == '__main__':
    app.run(debug = True)