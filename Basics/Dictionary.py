
Keys must be unique and immutable (e.g., strings, numbers, tuples).
Values can be any data type (strings, numbers, 
                             lists, other dictionaries, etc.).
Dictionaries are unordered (as of Python 3.6+, they maintain insertion order).

my_dict.keys()     # dict_keys(['name', 'age', 'email'])
my_dict.values()   # dict_values(['Alice', 31, 'alice@example.com'])
my_dict.items()    # dict_items([('name', 'Alice'), ('age', 31), ...])
                            

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
