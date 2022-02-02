from os import access
from flask import Flask, abort, request, redirect, url_for, render_template, session
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import pickle
import requests
import requests.auth
import json
import time
import urllib

from Account_Management import *
from Inventory_Management import *
from Progression_Management import *

# Initialize the app
app = Flask(__name__)
app.secret_key = 'g0ohkpNPJm5xYFV9AlsBk--yeM18EccWjLD935ZTC-c'
bootstrap = Bootstrap(app)

oauth_session = requests.Session()

API_KEY = '55afdf046d1b4ce4bf124a3fc86438b8'
CLIENT_ID = '39035'
CLIENT_SECRET = 'g0ohkpNPJm5xYFV9AlsBk--yeM18EccWjLD935ZTC-c'
HEADERS = {'X-API-Key': API_KEY}

REDIRECT_URI = 'https://localhost:5000/callback/bungie'

AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize?client_id='+CLIENT_ID+'&response_type=code&'
access_token_url = 'https://www.bungie.net/Platform/App/OAuth/token/'
refresh_token_url = access_token_url

# Open Manifest:
print("Opening Manifest...")
with open('data/manifest.pickle', 'rb') as data:
    all_data = pickle.load(data)
print("Finished!")


def setAccountSession():
    userSummary = GetCurrentBungieAccount(oauth_session)
    session['destinyMembershipId'] = str(userSummary.json()['Response']['destinyMemberships'][0]['membershipId'])
    session['membershipType'] = str(userSummary.json()['Response']['destinyMemberships'][0]['membershipType'])
    session['displayName'] = str(userSummary.json()['Response']['destinyMemberships'][0]['displayName'])
    return


@app.route('/')
@app.route('/index')
def index():
    state = make_authorization_url()
    state_params = {'state': state}
    url = AUTH_URL + urllib.parse.urlencode(state_params)
    # print(url)
    return render_template('index.html', url=url)


@app.route('/seasonal')
def seasonal():
    setAccountSession()

    accountSummary = GetAccountInfo(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))

    progress = getProgress(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))
    triumphs = parseProgress(oauth_session, progress, all_data, GetCharId(oauth_session, session, 0))

    characters = GetCharacters(accountSummary, all_data)

    # with open("RecordsOutput.json", "w") as text_file:
    #    text_file.write(str(progress.json()['Response']).replace("'", "\"").replace("True", "true").replace("False", "false"))

    return render_template('seasonal.html',
                           triumphs=triumphs,
                           characters=characters
                           )


@app.route('/vault')
def vault():
    setAccountSession()

    accountSummary = GetAccountInfo(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))
    vault = getVault(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))
    weaponList = parseVault(oauth_session, vault, all_data)

    #print('User Summary: ' + str(userSummary.json()['Response']))
    #print('Account Summary: ' + str(accountSummary.json()['Response']))
    #print('Character Summary: ' + str(accountSummary.json()['Response']['characters']['data']))
    firstChar = list(accountSummary.json()['Response']['characters']['data'])[0]
    # print(firstChar)

    return render_template('vault.html',
                           invItems=invItems,
                           weaponList=weaponList,
                           charId=accountSummary.json()['Response']['characters']['data'][firstChar]['characterId'],
                           character=session.get('displayName'),
                           lightLevel=accountSummary.json()['Response']['characters']['data'][firstChar]['light'],
                           emblemImage=accountSummary.json()['Response']['characters']['data'][firstChar]['emblemPath'],
                           backgroundImage=accountSummary.json()['Response']['characters']['data'][firstChar]['emblemBackgroundPath'],
                           )


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    return state


@app.route('/callback/bungie')
def bungie_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = session.get('state_token')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        print("Uh-oh, this request wasn't started by us!")
        abort(403)
    session.pop('state_token', None)
    code = request.args.get('code')
    authorisation_code = code
    token = get_token(code)
    return redirect(url_for('index'))


def get_token(code):
    AUTH_HEADERS = {'X-API-Key': API_KEY}
    post_data = {'grant_type': 'authorization_code',
                 'code': code,
                 'client_id': CLIENT_ID}
    response = requests.post(access_token_url, data=post_data, json=post_data, headers=AUTH_HEADERS)
    token_json = response.json()['access_token']
    #refresh_json = response.json()['refresh_token']
    refresh_expired = datetime.now() + timedelta(seconds=int(response.json()['expires_in']))
    save_session(token_json)
    return token_json

# Update Session:


def save_session(token_json):
    print("Updating session")
    oauth_session.headers["X-API-Key"] = API_KEY
    oauth_session.headers["Authorization"] = 'Bearer ' + str(token_json)
    access_token = "Bearer " + str(token_json)


# Save state parameter used in CSRF protection:
def save_created_state(state):
    session['state_token'] = state
    pass


def is_valid_state(state):
    saved_state = session['state_token']
    if state == saved_state:
        print("States match, you are who you say you are!")
        return True
    else:
        return False


# Main program - call app:
if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context=('auth/cert.pem', 'auth/key.pem'))
