import base64
import requests
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_pymongo import PyMongo
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/yourdbname"
mongo = PyMongo(app)

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
        password = base64.b64encode(password.encode('utf-8')).decode('utf-8')

        data = {
            "BusinessShortCode": "174379",
            "Password": password,
            "Timestamp": times,
            "TransactionType": "CustomerPayBillOnline",
            "PartyA": phone,
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": request.url_root + 'the-callback',
            "AccountReference": "TestPay",
            "TransactionDesc": "HelloTest",
            "Amount": amount
        }
        
        res = requests.post(endpoint, json=data, headers=headers)
        res_data = res.json()

        # Save payment request data to MongoDB
        payment_data = {
            "amount": amount,
            "phone": phone,
            "timestamp": times,
            "response": res_data
        }
        mongo.db.payments.insert_one(payment_data)

        return res_data

    return render_template('payform.html')

@app.route('/the-callback', methods=["POST"])
def incoming():
    data = request.get_json()
    print(data)
    
    # Save callback data to MongoDB
    mongo.db.payment_callbacks.insert_one(data)
    
    return "ok"

def getAccesstoken():
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']
