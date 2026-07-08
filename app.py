from flask import Flask, request, redirect, render_template_string
import requests
import os
import uuid

app = Flask(__name__)
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umarsaraki Wallet</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: linear-gradient(135deg, #00b74a, #007bff); display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
      .container { background: white; padding: 40px 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 100%; max-width: 400px; text-align: center; }
        h2 { font-size: 26px; color: #333; margin-bottom: 10px; }
      .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        input { width: 100%; padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 12px; text-align: center; margin-bottom: 15px; outline: none; }
        input:focus { border-color: #00b74a; }
        button { width: 100%; padding: 15px; background: #00b74a; color: white; border: none; border-radius: 12px; font-size: 17px; font-weight: bold; cursor: pointer; }
        button:hover { background: #009c3e; }
      .note { font-size: 12px; color: #888; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>💰 Fund Your Wallet</h2>
        <p class="subtitle">Top up your balance instantly</p>
        <form method="POST">
            <input type="email" name="email" placeholder="Enter Your Email" required>
            <input type="number" name="amount" placeholder="Enter Amount" required min="100">
            <button type="submit">Pay Now</button>
        </form>
        <p class="note">Minimum: ₦100 | Secured by Flutterwave</p>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_FORM)

    email = request.form["email"]
    amount = request.form["amount"]

    # Create unique tx_ref with email
    tx_ref = f"umarsaraki-{email}-{uuid.uuid4().hex[:8]}"

    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}", "Content-Type": "application/json"}

    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "redirect_url": "https://umarsaraki-wallet.onrender.com/callback",
        "customer": {
            "email": email,
            "name": email.split("@")[0]
        }
    }

    response = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
    data = response.json()

    if data["status"] == "success":
        return redirect(data["data"]["link"])
    else:
        return f"Error: {data['message']}"

@app.route("/callback", methods=["GET"])
def callback():
    status = request.args.get("status")
    if status == "successful":
        return "<div style='text-align:center; padding:50px;'><h2>Payment Successful ✅</h2><p>Verifying your payment. Wallet will be credited shortly.</p></div>"
    else:
        return "<div style='text-align:center; padding:50px;'><h2>Payment Cancelled</h2></div>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook Received:", data)

    if data.get("event") == "charge.completed" and data["data"]["status"] == "successful":
        tx_ref = data["data"]["tx_ref"] # umarsaraki-test@gmail.com-8f2a1b
        amount = data["data"]["amount"]

        # Extract email from tx_ref
        try:
            email = tx_ref.split("-")[1]
            print(f"CREDIT WALLET: {email} with ₦{amount}")

            # PUT YOUR CREDIT WALLET FUNCTION HERE
            # credit_wallet_by_email(email, amount)

        except Exception as e:
            print("Error:", e)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(debug=True)
