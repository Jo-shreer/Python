person = {
    "name": "Bob",
    "age": 25,
    "country": "Canada"
}

print("Name:", person["name"])
person["age"] = 26
person["email"] = "bob@example.com"

for k, v in person.items():
    print(f"{k} => {v}")



op
Name: Bob
name => Bob
age => 26
country => Canada
email => bob@example.com
