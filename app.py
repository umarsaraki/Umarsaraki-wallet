from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)
FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")

@app.route('/')
def home():
    return '<h2>Umarsaraki Wallet</h2><a href="/deposit">Danna Nan Don Biya Kudi</a>'

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = request.form['amount']
        email = request.form['email']
        payload = {"tx_ref": "UMAR-" + os.urandom(4).hex(), "amount": amount, "currency": "NGN", "redirect_url": "https://umarsaraki-wallet.onrender.com/webhook", "customer": {"email": email}}
        headers = {"Authorization": "Bearer " + FLW_SECRET_KEY}
        res = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
        return redirect(res.json()['data']['link'])
    return '<form method="POST">Email: <input name="email" required><br><br>Adadi: <input name="amount" value="100" required><br><br><button type="submit">Biya Yanzu</button></form>'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data['data']['status'] == 'successful':
        print("An biya: ", data['data']['amount'])
    return {"status": "success"}, 200
