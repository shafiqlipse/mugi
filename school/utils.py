import base64
import json
import requests
import uuid
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Load private key
PRIVATE_KEY_PATH = "E:/django/usssa/private-key.pem"

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

def sign_data(data):
    """Sign data using SHA256withRSA"""
    private_key = load_private_key()
    signature = private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def initiate_payment(mobileNumber, amount, reference):
    """Initiate Payment Request"""
    command="EPGPAYMENT",
    action="INITIATE",
    api_user = "599784e9-dd53-44c2-8a88-2718cadce0ea"
    request_id = str(uuid.uuid4())  # Generate a unique request ID
    biller_id = "USSSAUG"
    payment_method = "UGMM"
    currency = "UGX"
    memo = "test memo"
    apiPassword = "M@542nGB8#E78!mQ"

    # Generate the data to sign for the payment
    data_to_sign = f"EPGPAYMENTINITIATE{request_id}{api_user}{biller_id}{payment_method}{mobileNumber}{currency}{amount}{reference}{memo}{apiPassword}"
    
    # Generate the signature
    signature = sign_data(data_to_sign)

    # Construct the payload for the payment initiation request
    payload = {
        "command": "EPGPAYMENT",
        "action": "INITIATE",
        "apiUser": api_user,
        "requestId": request_id,
        "billerId": biller_id,
        "reference": reference,
        "amountToPay": amount,
        "paymentMethod": payment_method,
        "mobileNumber": mobileNumber,
        "currency": currency,
        "memo": memo,
        "signature": signature
    }

    headers = {
        "Authorization": f"Bearer {api_user}:{request_id}",
        "Content-Type": "application/json"
    }

    # Send the request to the payment API
    response = requests.post("https://caramel-group.com/eig", json=payload, headers=headers)
    print(response.json())
    # Ensure the response is parsed as JSON and return it along with the request_id
    return response.json(), request_id
    

def check_payment_status(request_id, mobileNumber):
    """Check Payment Status"""
    apiUser = "599784e9-dd53-44c2-8a88-2718cadce0ea"
    billerId = "USSSAUG"
    command = "EPGPAYMENT"
    action = "STATUS"
    apiPassword = "M@542nGB8#E78!mQ"

    # Generate dataToSign (concatenate all parameters as in the example)
    data_to_sign = (
    command + action + request_id + mobileNumber + apiUser + billerId + apiPassword
    )


    message_bytes = data_to_sign.encode('utf-8')
    private_key = load_private_key()
    signature = private_key.sign(
            message_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

    signature_b64 = base64.b64encode(signature).decode()

    print("Generated Signature:", signature_b64)

    # Construct API Request
    payload = {
        "command": "EPGPAYMENT",
        "action": "STATUS",
        "apiUser": apiUser,
        "requestId": request_id,
        "billerId": billerId,
        "signature": signature_b64,
        "mobileNumber": mobileNumber
    }

    headers = {
        "Authorization": f"Bearer {apiUser}:{request_id}",
        "Content-Type": "application/json"
    }

    # Send Request to payment gateway
    response = requests.post("https://caramel-group.com/eig", json=payload, headers=headers)
    print(response.json())
    return response.json() 
