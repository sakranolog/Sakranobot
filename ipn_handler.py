from flask import Flask, request
app = Flask(__name__)

@app.route('/ipn', methods=['POST'])
def handle_ipn():
    ipn_message = request.form
    print(ipn_message)
    return 'OK', 200

if __name__ == "__main__":
    app.run(port=5000)