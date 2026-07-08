from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def fund():
    if request.method == "POST":
        amount = request.form["amount"]
        return f"""
        <div style='display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa;'>
            <div style='background:white; padding:30px; border-radius:16px; text-align:center; max-width:400px;'>
                <h2>Thank You</h2>
                <p>Transfer <b>₦{amount}</b> to the account below:</p>
                <div style='background:#e8f5e9; padding:15px; border-radius:10px; margin:15px 0;'>
                    <p><b>Bank:</b> Flutterwave MFB</p>
                    <p><b>Account:</b> 9993707934</p>
                    <p><b>Name:</b> Umar Idris</p>
                </div>
                <p style='font-size:12px;'>Your wallet will be credited automatically once payment is confirmed.</p>
            </div>
        </div>
        """

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fund Wallet</title>
        <style>
            body{display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f7fa; margin:0; font-family:Arial;}
            .box{background:white; padding:30px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:100%; max-width:400px; text-align:center;}
            input{width:100%; padding:14px; border:2px solid #ddd; border-radius:10px; margin:15px 0; font-size:16px; text-align:center;}
            button{width:100%; padding:14px; background:#00b74a; color:white; border:none; border-radius:10px; font-size:16px; font-weight:bold;}
            .free{color:#00b74a; font-weight:bold; margin-bottom:10px;}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Fund Your Wallet</h2>
            <p class="free">Bank Transfer - 0% Fee</p>
            <form method="POST">
                <input type="number" name="amount" placeholder="Enter Amount" required>
                <button type="submit">Continue</button>
            </form>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)
