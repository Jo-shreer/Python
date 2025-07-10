list is an ordered collection of items.
Items can be of any data type: numbers, strings, other lists, objects, etc.
Lists are mutable — you can change, add, or remove items.



fruits = ["apple", "banana", "cherry"]

print("Original list:", fruits)

fruits.append("orange")
fruits.remove("banana")
fruits[0] = "kiwi"

print("Updated list:", fruits)

for fruit in fruits:
    print(f"Fruit: {fruit}")

print("Total fruits:", len(fruits))



op
Original list: ['apple', 'banana', 'cherry']
Updated list: ['kiwi', 'cherry', 'orange']
Fruit: kiwi
Fruit: cherry
Fruit: orange
Total fruits: 3
