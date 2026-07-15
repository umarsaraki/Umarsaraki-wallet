from flask import Flask, request, jsonify
import os
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
FLW_SECRET_KEY = os.environ.get("FLW_SECRET_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if request.headers.get('verif-hash') != FLW_SECRET_KEY:
        return jsonify({'status': 'error'}), 401

    if data['data']['status'] == 'successful':
        amount = data['data']['amount']
        user_id = data['data']['meta']['user_id']
        
        supabase.rpc('add_balance', {'user_id': user_id, 'amount': amount}).execute()
        
        return jsonify({'status': 'success'})

    return jsonify({'status': 'ignored'})

if __name__ == '__main__':
    app.run()
