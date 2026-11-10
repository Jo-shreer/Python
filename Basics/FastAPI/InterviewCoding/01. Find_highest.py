
{
    "results": [
        {
            "name": "Charlie",
            "compliance_score": 85
        },
        {
            "name": "Alice",
            "compliance_score": 95
        },
        {
            "name": "Bob",
            "compliance_score": 95
        },
        {
            "name": "David",
            "compliance_score": 78
        }
    ]
}


import requests

url = "API_URL"

def get():
    
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        data = response.json()
        
        results = data["results"]
        
        high_score = results[0]
        
        for result in results:
            if result["compliance_score"] > high_score["compliance_score"]:
                high_score = result
                
        name_list = []
        
        for result in results:
            if result["compliance_score"] == high_score["compliance_score"]:
                name_list.append(result["name"])
                
        name_list.sort(reverse=True)
        
        return name_list
            
    except(requests.exceptions.RequestException, KeyError, ValueError):
        return ""
            
        
    

