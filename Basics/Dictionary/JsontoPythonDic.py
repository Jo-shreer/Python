import json

json_data = '{"name": "Alice", "age": 30, "city": "New York"}'
py_dict = json.loads(json_data)

print(py_dict)
print(py_dict["name"])


op
{'name': 'Alice', 'age': 30, 'city': 'New York'}
Alice
