import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = ""##set this up if you wish to use google login

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "33674737284-srfbp7srvi8ie2m0sr426fved0hjq2tp.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")
"""
Above in the callback code change the redirect code to your products page 
main url
LETS SAY YOUR PRODUCT IS A DASHBOARD TO CHECK A SITES STATISTICS.
YOU CAN REPLACE THE URL WITH your dashboard home page link and use render template to
render the url as done below for index.html
"""


"""
In this logout url,you can remove that code and call the logout function
below using am html form like so:
    <form action="/logout" method="post">
        <input type="submit" value="Logout">
    </form>
    
@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.clear()
        return redirect("/")
    # If method is GET, you can render a template with a form to confirm logout
    return render_template("confirm_logout.html")
"""
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


#landing page code is set to the default page on launching the flask server
@app.route("/")
def landing():
    return render_template("index.html")

"""
@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"

"""

"""
YOU CAN NOW EDIT THE PROTECTED AREA URL TO BE YOUR PRODUCTS LOCATION
LETS SAY YOUR PRODUCT IS A DASHBOARD TO CHECK A SITES STATISTICS.
YOU CAN REPLACE THE URL WITH your dashboard link and use render template to
render the url as done above for index.html
"""
@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


if __name__ == "__main__":
    app.run(debug=True)
