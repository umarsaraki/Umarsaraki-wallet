from flask import Flask, request, redirect, render_template_string
import requests
import os
import uuid
from supabase import create_client, Client

app = Flask(__name__)
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

SUPABASE_URL = "https://lvlbxliuqrgyizxjmmyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2bGJ4bGl1cXJneWl6eGptbXl4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzUwNzU5NiwiZXhwIjoyMDk5MDgzNTk2fQ.QHyfi1jfdHZTwUvz9F5f0vFUIl0iD051Mz3urjxwQHs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HTML_REGISTER = """...same form..."""
HTML_FORM = """...same form..."""

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template_string(HTML_REGISTER)

    email = request.form["email"]
    password = request.form["password"]

    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        user_id = user.user.id

        # GYARA 1: wallets karama + GYARA 2: user_id
        supabase.table("wallets").insert({
            "user_id": user_id,
            "email": email,
            "wallet": 0
        }).execute()

        return "<h2 style='text-align:center; padding:50px;'>Registration Successful ✅<br>Wallet Balance: ₦0</h2>"

    except Exception as e:
        return f"<h2 style='text-align:center; padding:50px;'>Error: {str(e)}</h2>"

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
        "redirect_url": "https://umarsaraki-wallet.onrender.com/callback",
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

    if data.get("event") == "charge.completed" and data["data"]["status"] == "successful":
        tx_ref = data["data"]["tx_ref"]
        amount = data["data"]["amount"]

        try:
            email = tx_ref.split("-")[1]
            # GYARA: wallets karama
            wallet_data = supabase.table("wallets").select("wallet").eq("email", email).execute()

            if wallet_data.data:
                old_balance = wallet_data.data[0]['wallet']
                new_balance = old_balance + float(amount)
                supabase.table("wallets").update({"wallet": new_balance}).eq("email", email).execute()

        except Exception as e:
            print("Error:", e)

    return {"status": "success"}, 200
