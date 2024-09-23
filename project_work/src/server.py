import json
import os
from flask import Flask, render_template, jsonify, request
from web3 import Web3

# Initialize Flask app with the correct template folder
app = Flask(__name__, template_folder='templates')  # Assuming you run this from the src directory

# Connect to Ganache (running locally on port 7545)
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection to Ganache
if web3.is_connected():
    print("Connected to Ganache!")
else:
    print("Failed to connect to Ganache.")
    exit()

# Load ABI and Contract Address
contract_address = "0xA6789884FC5460E09648fa78B317DC55179FeA6f"  # Replace with your deployed contract address

# Load the ABI from build/contracts/MicroPayments.json
abi_path = os.path.join('..', 'build', 'contracts', 'MicroPayments.json')  # Adjust path to point to the correct location
with open(abi_path, 'r') as abi_file:
    contract_data = json.load(abi_file)
    contract_abi = contract_data['abi']  # Access the 'abi' field

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Replace this with one of the accounts from Ganache
owner_account = web3.eth.account.from_key("0xbab228f2e1d93cebe76b92edb1b73563432b69c35c4bd037d6bd77a34fc1e01f")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_balance', methods=['GET'])
def get_balance():
    try:
        balance = contract.functions.getContractBalance().call()
        return jsonify({"balance": web3.fromWei(balance, 'ether')})  # Ensure we convert Wei to Ether
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deposit', methods=['POST'])
def deposit():
    amount = request.json.get('amount')
    try:
        # Ensure amount is a valid number
        if amount is None or float(amount) <= 0:
            return jsonify({"error": "Invalid deposit amount"}), 400
        
        wei_amount = web3.toWei(float(amount), 'ether')
        tx_hash = contract.functions.deposit().transact({
            'from': owner_account.address,
            'value': wei_amount,
            'gas': 2000000
        })
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        return jsonify({"tx_hash": tx_receipt.transactionHash.hex()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_payment', methods=['POST'])
def send_payment():
    recipient = request.json.get('recipient')
    amount = request.json.get('amount')
    try:
        if not recipient or not Web3.isChecksumAddress(recipient):
            return jsonify({"error": "Invalid recipient address"}), 400
        if amount is None or float(amount) <= 0:
            return jsonify({"error": "Invalid payment amount"}), 400

        wei_amount = web3.toWei(float(amount), 'ether')
        tx_hash = contract.functions.sendPayment(Web3.toChecksumAddress(recipient), wei_amount).transact({
            'from': owner_account.address,
            'gas': 2000000
        })
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        return jsonify({"tx_hash": tx_receipt.transactionHash.hex()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/withdraw', methods=['POST'])
def withdraw():
    try:
        tx_hash = contract.functions.withdraw().transact({
            'from': owner_account.address,
            'gas': 2000000
        })
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        return jsonify({"tx_hash": tx_receipt.transactionHash.hex()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
