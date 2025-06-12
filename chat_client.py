import json
import time
import threading
import requests
from websocket import WebSocketApp
import datetime
import os

class ChatClient:
    def __init__(self):
        self.api_base_url = "https://rcapi.onrender.com/"
        self.ws_base_url = "wss://rcapi.onrender.com/ws/chat/groups"
        self.access_token = None
        self.user_info = {}
        self.ws = None
        self.room_name = ""
        self.ws_thread = None
        self.session_file = "session.json"

        self._load_session()

    def _load_session(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.user_info = data.get("user_info", {})
                    print(f"Session loaded for {self.user_info.get('email', 'unknown')}")
            except Exception as e:
                print("Failed to load session:", e)

    def _save_session(self):
        try:
            with open(self.session_file, "w") as f:
                json.dump({
                    "access_token": self.access_token,
                    "user_info": self.user_info
                }, f)
        except Exception as e:
            print("Failed to save session:", e)

    def register(self, email, password,first_name,last_name):
        url = f"{self.api_base_url}auth/register/"
        data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name

            }
        response = requests.post(url, json=data)
        response.raise_for_status()
        self.user_info['email'] = email
        print("Registered successfully")

    def login(self, email, password):
        url = f"{self.api_base_url}auth/login/"
        data = {'email': email, 'password': password}
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        self.access_token = result['access_token']
        self.user_info = {
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'phone_number': result['phone_number'],
            'email': email
        }
        self._save_session()
        print(f"Logged in as {email}")

    def connect(self, room_name):
        self.room_name = room_name
        url = f"{self.ws_base_url}/{room_name}/"
        headers = {'Authorization': f"Token {self.access_token}"}
        self.ws = WebSocketApp(
            url,
            header=headers,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        self.ws_thread = threading.Thread(target=self._run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def _run_forever(self):
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket error: {e}")
            time.sleep(5)
            print("Reconnecting WebSocket...")

    def _on_message(self, ws, message):
        self.onReceive(json.loads(message))

    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def _on_open(self, ws):
        print("WebSocket connection opened")

    def send(self, message):
        if self.ws:
            name = ""
            if(self.user_info['first_name']):
                name = f"{self.user_info['first_name']} {self.user_info['last_name']}"
            payload = {
                "message": message,
                "emailFrom": f"{self.user_info['email']}",
                "nameFrom": name,
                "date": str(datetime.datetime.now())
            }
            self.ws.send(json.dumps(payload))
        else:
            print("WebSocket is not connected")

    def onReceive(self, message_data):
        print("Received message:", message_data)








client = ChatClient()
client.connect("room4")

def custom_receive(data):
    print("Custom message handler:", data)

client.onReceive = custom_receive

while True:
    time.sleep(2)
    client.send("Hello Every one, i am Robot")