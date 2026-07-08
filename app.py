from flask import Flask, request, render_template_string, session
import requests
import os
import uuid

app = Flask(__name__)
app.secret_key = "change_this_to_random" 
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def fund():
    if request.method == "POST":
        amount = request.form["amount"]
        
        if int(amount) < 100: # Flutterwave min 100
            return "Error: Minimum amount is ₦100"
        
        # Bayanin user - ka canza da login info na gaske
        email = "user" + str(uuid.uuid4())[:6] + "@umarsaraki.com"
        name = "Wallet User " + str(uuid.uuid4())[:6]
        
        headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}", "Content-Type": "application/json"}
        
        # 1. Generate Virtual Account - BA MU TURA AMOUNT BA A NAN
        payload = {
            "email": email,
            "is_permanent": False, 
            "tx_ref": f"va-{uuid.uuid4()}",
            "fullname": name
        }
        res = requests.post("https://api.flutterwave.com/v3/virtual-account-numbers", json=payload, headers=headers)
        data = res.json()
        
        if data["status"] == "success":
            va = data["data"]
            session['amount'] = amount
            session['account'] = va["account_number"]
            
            return render_template_string("""
            <style>
            body{display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa; font-family:Arial; margin:0;}
            .box{background:white; padding:30px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:100%; max-width:400px; text-align:center;}
            .acc{font-size:22px; font-weight:bold; background:#e8f5e9; padding:12px; border-radius:8px; margin:10px 0; letter-spacing:1px;}
            .btn{width:100%; padding:14px; background:#00b74a; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold; margin-top:10px; cursor:pointer;}
            .btn2{background:#007bff;}
            </style>
            
            <div class="box">
                <h2>Transfer ₦{{amount}}</h2>
                <p style="color:#00b74a; font-weight:bold;">0% Fee - Use this account only</p>
                
                <p><b>Bank:</b> {{va['bank_name']}}</p>
                <p><b>Account Number:</b></p>
                <div class="acc" id="acc">{{va['account_number']}}</div>
                <button class="btn btn2" onclick="navigator.clipboard.writeText('{{va['account_number']}}')">Copy Account Number</button>
                
                <p><b>Account Name:</b> {{va['account_name']}}</p>
                
                <form method="POST" action="/confirm">
                    <button type="submit" class="btn">I Have Paid</button>
                </form>
                <p style="font-size:11px; margin-top:10px; color:#666;">Account expires in 24 hours. Click after transfer.</p>
            </div>
            """, amount=amount, va=va)
        else:
            return f"Error: {data['message']}"

    return render_template_string("""
    <style>body{display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa; font-family:Arial; margin:0;}
    .box{background:white; padding:30px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:100%; max-width:400px; text-align:center;}
    input{width:100%; padding:14px; border:2px solid #ddd; border-radius:10px; margin:15px 0; font-size:16px; text-align:center;}
    button{width:100%; padding:14px; background:#00b74a; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold;}</style>
    <div class="box"><h2>Fund Your Wallet</h2><p style="color:#00b74a;">Bank Transfer - 0% Fee</p>
    <form method="POST"><input type="number" name="amount" placeholder="Enter Amount - Min ₦100" required min="100"><button>Generate Account</button></form></div>
    """)

@app.route("/confirm", methods=["POST"])
def confirm():
    return f"<div style='text-align:center; padding:50px;'><h2>Thank You</h2><p>We are verifying your payment of ₦{session.get('amount')}.<br>Your wallet will be credited automatically in 2 minutes.</p></div>"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data["event"] == "virtual.account.credit":
        account = data["data"]["account_number"]
        amount = data["data"]["amount"]
        print(f"Credit {account} with {amount} ✅")
        # Nan zaka duba DB ka san wane user ne sannan ka credit
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)
