from flask import Flask, request, redirect, render_template_string
import requests
import os

app = Flask(__name__)
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umarsaraki Wallet - Fund Wallet</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        body {
            background: #f5f7fa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px 30px;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h2 {
            font-size: 24px;
            color: #333;
            margin-bottom: 30px;
        }
        input {
            width: 100%;
            padding: 14px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            outline: none;
        }
        input:focus {
            border-color: #00b74a;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #00b74a;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background: #009c3e;
        }
        .note {
            font-size: 12px;
            color: #888;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>💰 Fund Your Wallet</h2>
        <form method="POST">
            <input type="number" name="amount" placeholder="Enter Amount" required min="100">
            <button type="submit">Pay Now</button>
        </form>
        <p class="note">Minimum amount: ₦100</p>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_FORM)
    
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
        },
        "payment_options": "card,banktransfer,ussd" # Card za ta dauke 1.4% fee
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
        print(f"Credited {data['amount']} to wallet ✅")
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
