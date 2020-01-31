import os
from flask import Flask, redirect, url_for, render_template, jsonify, session
from flask_dance.contrib.google import make_google_blueprint, google
from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "341976011899-630kjb2m9cen1lqm5267aqc5bjnm8fk7.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "2CX58C_QcUrVQLdLTGNJkxdA"
blueprint = make_google_blueprint(scope=["https://www.googleapis.com/auth/analytics", "https://www.googleapis.com/auth/userinfo.email"])


app.register_blueprint(blueprint, url_prefix="/login")


def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
                accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                    accountId=account,
                    webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def get_results(service, profile_id):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    return service.data().ga().get(
            ids='ga:' + profile_id,
            start_date='7daysAgo',
            end_date='today',
            metrics='ga:sessions').execute()


def print_results(results):
    # Print data nicely for the user.
    if results:
        print ('View (Profile):', results.get('profileInfo').get('profileName'))
        print ('Total Sessions:', results.get('rows')[0][0])

    else:
        print ('No results found')


def main():
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = 'client_secret.json'

    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    profile_id = get_first_profile_id(service)
    print_results(get_results(service, profile_id))

@app.route("/")
def index():
    """Index route."""
    
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
   
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = 'client_secret.json'

    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    profile_id = get_first_profile_id(service)
    print_results(get_results(service, profile_id))

    token = blueprint.token["access_token"]
    print(token)
    assert resp.ok, resp.text
    print(resp.text)
    return "You are {email} on Google".format(email=resp.json()["email"])
    
    
@app.route('/select')
def select():
    account_summaries = analytics.management().accountSummaries().list().execute()
    accounts = []

    for account in account_summaries.get('items', []):
        account_id_name = account.get('id') + account.get('name')
        accounts = accounts.append(account_id_name)

    # return render_template('select.html', accounts=accounts)


@app.route('/results')
def results():
    return "GA Audit Results"
    #del blueprint.token