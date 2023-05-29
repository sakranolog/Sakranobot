from flask import Flask, request, render_template
import db
import config



app = Flask(__name__)

@app.route('/ipn', methods=['POST'])
def handle_ipn():
    ipn_data = request.form
    user_id = int(ipn_data['userid'])
    db.add_payment(user_id, ipn_data)
    print(ipn_data)
    return 'OK', 200

@app.route('/')
def hello():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(port=5000)
