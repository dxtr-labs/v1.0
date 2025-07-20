import re

user_message = "service:inhouse Using AI generate a sales pitch to sell healthy mango ice cream and send email to slakshanand1105@gmail.com"
print(f"Original: {user_message}")

clean_request = re.sub(r'service:\s*\w+\s*', '', user_message, flags=re.IGNORECASE).strip()
print(f"Clean: '{clean_request}'")
