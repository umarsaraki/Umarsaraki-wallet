from flask import Flask, request, render_template_string, session
import requests
import os
import uuid

app = Flask(__name__)
app.secret_key = "random_secret_key" # Canza shi
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def fund():
    if request.method == "POST":
        amount = request.form["amount"]
        email = "customer" + str(uuid.uuid4())[:8] + "@umarsaraki.com" # Ka canza da login email na user
        name = "Customer " + str(uuid.uuid4())[:8] # Ka canza da sunan user
        
        # 1. Mu kirkira Virtual Account na wannan user din
        headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}", "Content-Type": "application/json"}
        payload = {
            "email": email,
            "is_permanent": False, # Ya kare bayan awa 24
            "bvn": None,
            "tx_ref": f"va-{uuid.uuid4()}",
            "fullname": name,
            "phone_number": "08000000000"
        }
        res = requests.post("https://api.flutterwave.com/v3/virtual-account-numbers", json=payload, headers=headers)
        data = res.json()
        
        if data["status"] == "success":
            va = data["data"]
            session['amount'] = amount # Mu ajiye amount din
            session['account'] = va["account_number"]
            
            return render_template_string("""
            <style>body{display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa; font-family:Arial;} 
            .box{background:white; padding:30px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:100%; max-width:400px; text-align:center;}
            .acc{font-size:22px; font-weight:bold; background:#eee; padding:10px; border-radius:8px; margin:10px 0;}
            button{width:100%; padding:14px; background:#00b74a; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold; margin-top:10px;}</style>
            
            <div class="box">
                <h2>Transfer ₦{{amount}}</h2>
                <p style="color:#00b74a; font-weight:bold;">0% Fee - Account Expires in 24hrs</p>
                
                <p><b>Bank:</b> {{va['bank_name']}}</p>
                <p><b>Account:</b></p>
                <div class="acc" id="acc">{{va['account_number']}}</div>
                <button onclick="navigator.clipboard.writeText('{{va['account_number']}}')">Copy Account Number</button>
                
                <p><b>Name:</b> {{va['account_name']}}</p>
                
                <form method="POST" action="/confirm">
                    <button type="submit">I Have Paid</button>
                </form>
                <p style="font-size:11px; margin-top:10px;">Click after transfer. We will verify automatically.</p>
            </div>
            """, amount=amount, va=va)
        else:
            return "Error: " + data["message"]

    return render_template_string("""
    <style>body{display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa; font-family:Arial;} 
    .box{background:white; padding:30px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:100%; max-width:400px; text-align:center;}
    input{width:100%; padding:14px; border:2px solid #ddd; border-radius:10px; margin:15px 0; font-size:16px; text-align:center;}
    button{width:100%; padding:14px; background:#00b74a; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold;}</style>
    <div class="box"><h2>Fund Your Wallet</h2><p style="color:#00b74a;">Bank Transfer - 0% Fee</p>
    <form method="POST"><input type="number" name="amount" placeholder="Enter Amount" required><button>Generate Account</button></form></div>
    """)

@app.route("/confirm", methods=["POST"])
def confirm():
    # Nan za ka jira webhook. "I Have Paid" kawai yana nuna mana ya tura
    return f"<div style='text-align:center; padding:50px;'><h2>Thank You</h2><p>We are verifying your payment of ₦{session.get('amount')}.<br>Your wallet will be credited in 2 minutes.</p></div>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    # Saboda account na kowane user ne, za mu iya duba data['data']['account_number'] 
    # sannan mu san wanda ya biya mu credit wallet din sa
    if data["event"] == "virtual.account.credit":
        account = data["data"]["account_number"]
        amount = data["data"]["amount"]
        print(f"Credit {account} with {amount} ✅")
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
