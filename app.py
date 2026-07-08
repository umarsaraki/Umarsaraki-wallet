from flask import Flask, request, redirect, render_template_string
import requests
import os

app = Flask(__name__)
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

HTML_FORM = """
<!DOCTYPE html>
<html lang="ha">
<head>
    <meta charset="UTF-8">
    <title>Umarsaraki Wallet</title>
</head>
<body style="font-family: Arial; text-align: center; padding-top: 50px;">
    <h2>💰 Caja Wallet Dinka</h2>
    <form method="POST">
        <input type="number" name="amount" placeholder="Shigar da Adadi" required style="padding: 10px; width: 200px;">
        <br><br>
        <button type="submit" style="padding: 10px 20px; background: green; color: white; border: none;">Biya Yanzu</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_FORM)
    
    # Wannan shine POST - lokacin da aka latsa Biya
    amount = request.form["amount"]
    
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tx_ref": f"umarsaraki-{request.remote_addr}-{amount}",
        "amount": amount,
        "currency": "NGN",
        "redirect_url": "https://umarsaraki-wallet.onrender.com/webhook",
        "customer": {
            "email": "test@umarsaraki.com",
            "name": "Test User"
        }
    }
    
    response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
    data = response.json()
    
    if data["status"] == "success":
        return redirect(data["data"]["link"])
    else:
        return f"Error: {data['message']}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data["status"] == "successful":
        print(f"An tura {data['amount']} cikin wallet ✅")
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run()
