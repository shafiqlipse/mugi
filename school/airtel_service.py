# Load environment variables from .env file
import requests
class AirtelMoney:
    BASE_URL = "https://openapi.airtel.africa/standard/v1"
    AUTH_URL = f"{BASE_URL}/oauth/token"
    PAYMENT_URL = f"{BASE_URL}/payments/"

    def __init__(self):
        self.client_id = 'your_client_id'
        self.client_secret = 'your_client_secret'
        self.api_key = 'your_api_key'
        self.token = None

    def authenticate(self):
        headers = {"Content-Type": "application/json"}
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(self.AUTH_URL, json=data, headers=headers)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            raise Exception("Authentication failed: " + response.text)

    def initiate_payment(self, phone_number, amount, currency="USD"):
        if not self.token:
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "amount": amount,
            "currency": currency,
            "receiver_phone_number": phone_number,
            "transaction_reference": "TXN" + phone_number[-4:],  # Example transaction ref
            "description": "School Games Payment",
        }
        response = requests.post(self.PAYMENT_URL, json=data, headers=headers)
        return response.json()
