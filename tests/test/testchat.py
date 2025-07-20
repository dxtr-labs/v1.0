import requests

response = requests.post("http://127.0.0.1:8000/chat/", json={
    "user_input": "Send a good morning email every day at 8 AM",
    "user_id": "test-user"
})

print(response.status_code)
print(response.json())

