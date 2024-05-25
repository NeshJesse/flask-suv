import os
import pathlib
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import requests
from flask import Flask, session, abort, redirect, request,render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask(__name__, template_folder='templates')
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
"""
get the credentials like google client id from cloud.google.console
"""
GOOGLE_CLIENT_ID = " "
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
"""
So, authorization_url leads to Google's authentication page where users can log in 
and authorize the application to access their profile information based on the specified scopes.
After authorization, Google will redirect the user back to the redirect 
URI specified in the OAuth flow configuration (redirect_uri="http://127.0.0.1:5000/callback"),
along with an authorization code that can be exchanged for access and refresh tokens.
"""

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


@app.route("/land")
def landing():
    return render_template("index.html")


"""
landing page code is set to the default page on launching the flask server
"""
@app.route("/")
def first():
    return render_template("landin.html")


@app.route("/index")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"

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

myend_point = ''

#initiate an express pay request,MpesaExpay is Mpesa express pay in short
#the password consists of the business shortcode,passkey in that order
"""
To test enter the port e.g. http://127.0.1.5000/pay?phone=254710340633&amount=20
this will send a request to pay 20 bob to the number and then print the data on the page
The data will include checkout request id, customermessage,merchant requestid,response code and responsedescription
The number will receive the stk push and if they pay or cancel,the message will be conveyed accordingly
if you want to set a default amount just remove the amount = request.form['amount'] and replace this 
line in data ={ AMount : amount} amount : with ur desired cash e.g 200}
"""

@app.route('/payment', methods=['GET', 'POST'])
def MpesaExpay():
    if request.method == 'POST':
        amount = request.form['amount']
        phone = request.form['phone']
        endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        access_token = getAccesstoken()
        headers = {"Authorization": "Bearer %s" % access_token }
        Timestamp = datetime.now()
        times = Timestamp.strftime("%Y%m%d%H%M%S")
        password = "174379" + "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" + times
        password = base64.b64encode(password.encode('utf-8'))

        data ={
            "BusinessShortCode": "174379",
            "Password": password,
            "Timestamp": times,
            "TransactionType": "CustomerPayBillOnline",
            "PartyA": phone,
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": myend_point + '/the-callback',
            "AccountReference": "TestPay",
            "TransactionDesc": "HelloTest",
            "Amount": amount
        }
        
        res= requests.post(endpoint, json = data, headers = headers)
        return res.json()
    #Uncomment the code below to route to login page after success of payment
        #Assuming the payment is successful, redirect to the login page
        #return redirect(url_for('login'))
    return render_template('payform.html')
"""
the above ending for return returns json data.The data can then be saved to a database of 
your choice
"""

# here you then consume the mpesa express callback
@app.route('/the-callback', methods=["POST"])
def incoming():
    data = request.get_json()
    print(data)
    return "ok"

"""
In the above code, i have chosen to print,feel free to save the data to database if needed
"""

"""
Get the consumer keys from safaricom sandbox,no error handling has been done for below code
"""
#the access token
#the code format below also assumes you are using a paybill number

def getAccesstoken():
    consumer_key =""
    consumer_secret =""
    endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']
if __name__ == "__main__":
    app.run(debug=True)
