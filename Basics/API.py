
import requests

response = requests.get("https://official-joke-api.appspot.com/random_joke")

if response.status_code == 200:
    joke = response.json()
    print(f"{joke['setup']}")
    print(f"{joke['punchline']}")
else:
    print("Failed to get a joke.")


op
Knock knock. 
 Who's there? 
 Opportunity.
That is impossible. Opportunity doesn’t come knocking twice!
