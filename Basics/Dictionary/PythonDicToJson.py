import json

py_dict = {
    "name": "Bob",
    "age": 25,
    "city": "Toronto"
}

json_data = json.dumps(py_dict)
print(json_data)


op
{"name": "Bob", "age": 25, "city": "Toronto"}
