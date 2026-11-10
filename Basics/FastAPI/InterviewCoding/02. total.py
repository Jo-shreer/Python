"""
Write a function that:
1. Calls the API.
2. Extracts results.
3. Calculates the sum of all compliance scores.
4. Returns the total.
5. Returns "" if an error occurs.
This time, practise using an accumulator variable such as total = 0.
"""

import requests

url = "API_URL"

def get():
    
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        data = response.json()
        
        results = data["results"]
        
        total = 0
        
        for result in results:
            total += result["compliance_score"]
            
        return total
         
    except(requests.except.RequestError,KeyError, ValueError):
            return ""
