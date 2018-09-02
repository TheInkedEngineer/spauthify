import base64
import json

from flask import (
    Flask,
    redirect,
    render_template,
    request,
)
import requests
import urllib.parse

app = Flask(__name__)


# These three constants below are used to build the bast URL
SPOTIFY_BASE_URL = "https://accounts.spotify.com"
SPOTIFY_AUTH_ENDPOINT = "/authorize"
SPOTIFY_TOKEN_ENDPOINT = "/api/token"

# The client ID provided by Spotify.
# It can be retrieved from the App's Spotify dashboard
CLIENT_ID = ""

# The client secret provided by Spotify.
# It can be retrieved from the App's Spotify dashboard
CLIENT_SECRET = ""

# Constant needed by Spotify inside of the request body
RESPONSE_TYPE = "code"

# This URL should be registered on the App's Spotify dashboard.
# It lets Spotify auth know where to redirect the request to so the user can parse the information.
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# The list of scopes requesting authorization for
# Scopes can be found here: https://developer.spotify.com/documentation/general/guides/scopes/ (last opened 01/09/18)
SCOPE = "user-read-private user-read-email"


@app.route('/')
def index():

    """
    This is the root directory.
    It builds the Spotify URL and redirects the user to the Spotify login page.
    """

    payload = {
        "client_id": CLIENT_ID,
        "response_type": RESPONSE_TYPE,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }

    url = SPOTIFY_BASE_URL + SPOTIFY_AUTH_ENDPOINT + '?' + urllib.parse.urlencode(payload, doseq=True)

    return redirect(url)


@app.route('/callback')
def callback():

    """
    After the login Spotify redirects the user to this path registered inside of the Spotify App.
    Here we parse the response provided by Spotify and request the Access Token.

    For the sake of this example this route will print the returned data to your browser.
    """

    try:
        # The auth token returned by Spotify
        auth_token = request.args['code']
    except KeyError:
        # TODO: manage when access_denied in the future
        error = request.args['error']
        return error

    # The bare minimum payload requested by Spotify
    payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    url = SPOTIFY_BASE_URL + SPOTIFY_TOKEN_ENDPOINT
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        # This content includes the access token which will be included in all headers for future requests
        # authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        content = json.loads(response.content)

    else:
        # TODO: manage error cases
        return

    return render_template("index.html", dict=content)


def get_new_token(refresh_token):
    """

    :param refresh_token: The refresh token provided with the access token
    :return: a dictionary containing token information as follow
    {
        "access_token": access_token,
        "token_type": token_type,
        "expires_in": expires_in,
        "scope": scope,
    }

    """

    # In order to request the new access token, the header must contain a Base 64 encoded string made of the client ID and client secret key. 
    # The field must have the format: Authorization: Basic *<base64 encoded client_id:client_secret>*
    auth_b64encode = base64.b64encode(CLIENT_ID.encode() + ":".encode() + CLIENT_SECRET.encode()).decode("utf-8")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + auth_b64encode
    }

    url = SPOTIFY_BASE_URL + SPOTIFY_TOKEN_ENDPOINT
    response = requests.post(url=url, data=payload, headers=headers)

    if response.status_code == 200:
        content = json.loads(response.content)

    else:
        # TODO: manage error cases
        return

    return content


if __name__ == '__main__':
    app.run()
