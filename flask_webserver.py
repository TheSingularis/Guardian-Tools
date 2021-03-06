from model.Progression_Management import *
from model.Inventory_Management import *
from model.Account_Management import *
from os import path, sys
from flask import Flask, abort, request, redirect, url_for, render_template, session
import pickle
import requests
import urllib

sys.path.append('../model')


# Initialize the app
app = Flask(__name__)
app.secret_key = '-yeM18EccWjLD935ZTC-cg0ohkpNPJm5xYFV9AlsBk-'

oauth_session = requests.Session()

API_KEY = '55afdf046d1b4ce4bf124a3fc86438b8'
CLIENT_ID = '39035'
HEADERS = {'X-API-Key': API_KEY}

BASE_URL = 'https://bungie.net/Platform/Destiny2/'
REDIRECT_URL = 'https://localhost:5000/callback/bungie'
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize?client_id='+CLIENT_ID+'&response_type=code&'
TOKEN_URL = 'https://www.bungie.net/Platform/App/OAuth/token/'

# -------------------------
# -----Handle Manifest-----
# -------------------------

if not path.exists('data/manifest.pickle'):
    print("Manifest is missing...")
    import get_manifest
else:
    print("Manifest Found...")

# Open Manifest:
print("Opening Manifest...")
with open('data/manifest.pickle', 'rb') as data:
    all_data = pickle.load(data)
print("Finished!")

# -----------------
# -----Routing-----
# -----------------


@app.route('/')
@app.route('/index')
def index():
    # TODO: Design a dashboard page that shows basic character information
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/seasonal')
def seasonal():
    setAccountSession()

    accountSummary = GetAccountInfo(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))

    progress = getProgress(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))
    triumphs = parseProgress(oauth_session, progress, all_data, GetCharId(oauth_session, session, 0))

    characters = GetCharacters(accountSummary, all_data)

    return render_template('seasonal.html',
                           triumphs=triumphs,
                           characters=characters
                           )


@app.route('/vault')
def vault():
    setAccountSession()

    accountSummary = GetAccountInfo(oauth_session, session.get('membershipType'), session.get('destinyMembershipId'))
    vault = getVault(oauth_session, session['membershipType'], session.get('destinyMembershipId'))
    weaponList = parseVault(oauth_session, vault, all_data)

    firstChar = list(accountSummary.json()['Response']['characters']['data'])[0]

    return render_template('vault.html',
                           invItems=invItems,
                           weaponList=weaponList,
                           charId=accountSummary.json()['Response']['characters']['data'][firstChar]['characterId'],
                           character=session.get('displayName'),
                           lightLevel=accountSummary.json()['Response']['characters']['data'][firstChar]['light'],
                           emblemImage=accountSummary.json()['Response']['characters']['data'][firstChar]['emblemPath'],
                           backgroundImage=accountSummary.json()['Response']['characters']['data'][firstChar]['emblemBackgroundPath'],
                           )


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
    session['token'] = token
    return redirect(url_for(session['path'][1:]))


@app.route('/error/<cause>')
def errorReport(cause):
    text = None

    if cause == "bungieServer":
        text = "Bungie servers unavailable, check @BungieHelp for more information."
        print(text)

    return render_template('index.html', info=text, error=True)


@app.before_request
def check_login():

    # Ignore local requests
    if ('static' not in request.path) and ('error' not in request.path) and ('/' != request.path):

        # Check bungie server status
        cause = None

        # TODO: find a way to check if the service is up or not, this aint it chief
        # if "Endpoint not found." in oauth_session.get(base_url).text:
        #    # Servers are down
        #    cause = 'bungieServer'

        print(f"Error Redirect: {cause}")

        if cause != None:
            print("error")
            return redirect(url_for('errorReport', cause=cause), code=302)

        # Redirect to bungie auth if not logged in
        if (not request.path == '/callback/bungie'):
            session['path'] = request.path
            if "Authorization" in oauth_session.get('https://httpbin.org/headers').text:
                # logged in, do nothing
                pass
            else:
                # run login routine then continue
                state = make_authorization_url()
                state_params = {'state': state}
                url = AUTH_URL + urllib.parse.urlencode(state_params)

                return redirect(url, code=302)

# -------------------
# -----Functions-----
# -------------------


def setAccountSession():
    userSummary = GetCurrentBungieAccount(oauth_session)
    session['destinyMembershipId'] = str(userSummary.json()['Response']['destinyMemberships'][0]['membershipId'])
    session['membershipType'] = str(userSummary.json()['Response']['destinyMemberships'][0]['membershipType'])
    session['displayName'] = str(userSummary.json()['Response']['destinyMemberships'][0]['displayName'])
    return


# Generate a random string for the state parameter
# Save it for use later to prevent CSRF attacks
def make_authorization_url():
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    return state


def get_token(code):
    AUTH_HEADERS = {'X-API-Key': API_KEY}
    post_data = {'grant_type': 'authorization_code',
                 'code': code,
                 'client_id': CLIENT_ID}
    response = requests.post(TOKEN_URL, data=post_data, json=post_data, headers=AUTH_HEADERS)
    token_json = response.json()['access_token']
    # refresh_json = response.json()['refresh_token']
    # refresh_expired = datetime.now() + timedelta(seconds=int(response.json()['expires_in']))
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
    session['state_token'] = str(state)
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
