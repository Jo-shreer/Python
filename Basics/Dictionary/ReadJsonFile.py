file name data.json

{
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "Django", "Machine Learning"],
    "is_active": true
}

***********************
import json

with open("data.json") as f:
    data = json.load(f)
    print(data)


op
{
    'name': 'Alice',
    'age': 30,
    'skills': ['Python', 'Django', 'Machine Learning'],
    'is_active': True
}
