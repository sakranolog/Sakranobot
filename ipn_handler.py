from flask import Flask, request, render_template
import db
import config
import os



app = Flask(__name__)

@app.route('/ipn', methods=['POST'])
def handle_ipn():
    try:
        ipn_data = request.form
        user_id = int(ipn_data['userid'])
        db.add_payment(user_id, ipn_data)
        print(ipn_data)
        return 'OK', 200
    except Exception as e:
        print(f"Error handling IPN: {e}")
        return 'Bad Request', 400

@app.route('/')
def hello():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.getenv("PORT",5000))
