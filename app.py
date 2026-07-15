from flask import Flask, request, redirect, render_template_string
import requests
import os
import uuid
from supabase import create_client, Client

app = Flask(__name__)

# 1. KEYS DAGA ENVIRONMENT
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")
FLW_SECRET_HASH = "UMARSHOYI_SUB_0891" # Kamar yadda ka ce
SUPABASE_URL = "https://lvlbxliuqrgyizxjmmyx.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Mun fitar dashi daga code domin tsaro
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_REGISTER = """
<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {box-sizing: border-box; margin: 0; padding: 0;}
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex; justify-content: center; align-items: center; height: 100vh;
        }
      .box {
            background: #fff; padding: 40px 30px; border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2); width: 90%; max-width: 400px; text-align: center;
        }
        h2 {color: #667eea; margin-bottom: 25px; font-size: 28px;}
        input {
            width: 100%; padding: 14px; margin: 12px 0; border: 2px solid #e0e0e0;
            border-radius: 10px; font-size: 16px; transition: 0.3s;
        }
        input:focus {border-color: #667eea; outline: none;}
        button {
            width: 100%; padding: 14px; margin-top: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer;
        }
        button:hover {opacity: 0.9; transform: translateY(-2px);}
    </style>
</head>
<body>
    <div class="box">
        <h2>Register</h2>
        <form method="POST">
            <input type="email" name="email" placeholder="Your Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
    </div>
</body>
</html>
"""

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Fund Wallet</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {box-sizing: border-box; margin: 0; padding: 0;}
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* COLOR */
            display: flex; justify-content: center; align-items: center; height: 100vh; /* FULL SCREEN + CENTER */
        }
      .box {
            background: #fff; padding: 40px 30px; border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2); width: 90%; max-width: 400px; text-align: center;
        }
        h1 {color: #667eea; margin-bottom: 25px; font-size: 30px;}
        input {
            width: 100%; padding: 14px; margin: 12px 0; border: 2px solid #e0e0e0;
            border-radius: 10px; font-size: 16px; transition: 0.3s;
        }
        input:focus {border-color: #667eea; outline: none;}
        button {
            width: 100%; padding: 14px; margin-top: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s;
        }
        button:hover {opacity: 0.9; transform: translateY(-2px);}
    </style>
</head>
<body>
    <div class="box">
        <h1>Fund Wallet</h1>
        <form method="POST">
            <input type="email" name="email" placeholder="Your Email" required>
            <input type="number" name="amount" placeholder="Enter Amount ₦" required>
            <button type="submit">Fund Wallet</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template_string(HTML_REGISTER)

    email = request.form["email"]
    password = request.form["password"]

    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        user_id = user.user.id
        supabase.table("wallets").insert({"user_id": user_id, "email": email, "wallet": 0}).execute()
        return "<h2 style='text-align:center; padding:50px; color:white;'>Registration Successful ✅<br>Wallet Balance: ₦0</h2>"

    except Exception as e:
        return f"<h2 style='text-align:center; padding:50px; color:white;'>Error: {str(e)}</h2>"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_FORM)

    email = request.form["email"]
    amount = request.form["amount"]
    tx_ref = f"umarsaraki-{email}-{uuid.uuid4().hex[:8]}"

    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}", "Content-Type": "application/json"}
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "redirect_url": f"https://umarsaraki-wallet.onrender.com/callback?tx_ref={tx_ref}&email={email}",
        "customer": {"email": email, "name": email.split("@")[0]}
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
    if request.headers.get("verif-hash")!= FLW_SECRET_HASH:
        return {"status": "unauthorized"}, 401

    if data.get("event") == "charge.completed" and data["data"]["status"] == "successful":
        amount = data["data"]["amount"]
        email = data["data"]["customer"]["email"]
        try:
            wallet_data = supabase.table("wallets").select("wallet").eq("email", email).execute()
            if wallet_data.data:
                old_balance = wallet_data.data[0]['wallet']
                new_balance = old_balance + float(amount)
                supabase.table("wallets").update({"wallet": new_balance}).eq("email", email).execute()
        except Exception as e:
            print("Error:", e)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
