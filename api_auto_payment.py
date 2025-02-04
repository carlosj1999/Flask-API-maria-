from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/payment', methods=['POST'])
def handle_payment():
    # Get 'pay_amount' from the JSON body
    data = request.json
    pay_amount = data.get('pay_amount')

    # Check if 'pay_amount' was provided
    if not pay_amount:
        return jsonify({"error": "Missing 'pay_amount' field in request body"}), 400

    # Print the value to the console (for debugging purposes)
    print(f"Received payment amount: {pay_amount}")

    # Return a JSON response
    return jsonify({"message": f"Payment amount received: {pay_amount}"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
