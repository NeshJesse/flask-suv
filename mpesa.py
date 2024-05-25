from flask import Flask, request, render_template
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

app = Flask(__name__, template_folder='templates')

myend_point = ''

#initiate an express pay request,MpesaExpay is Mpesa express pay in short
#the password consists of the business shortcode,passkey in that order
"""
To test enter the port e.g. http://127.0.1.5000/pay?phone=254710340633&amount=20
this will send a request to pay 20 bob to the number and then print the data on the page
The data will include checkout request id, customermessage,merchant requestid,response code and responsedescription
The number will receive the stk push and if they pay or cancel,the message will be conveyed accordingly
"""
"""
as for the amount you can replace the amount with 100 in the data payload
you can then remove the amount=request.form['amount']
"""
@app.route('/pay', methods=['GET', 'POST'])
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
    app.run(host='0.0.0.0', port=5000, debug=True)
