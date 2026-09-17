LIST COMPREHENSION
==================
WHAT IS LIST COMPREHENSION?
---------------------------
List comprehension is a short way to create a new list
from an existing iterable.

Basic pattern:
[expression for item in iterable]

NORMAL FOR LOOP
---------------
numbers = [1, 2, 3, 4]
result = []
for number in numbers:
    result.append(number * 2)

result:
[2, 4, 6, 8]

LIST COMPREHENSION
------------------
result = [number * 2 for number in numbers]
Same result:
[2, 4, 6, 8]

BASIC EXAMPLE
=============
names = ["john", "sarah", "mike"]
upper_names = [name.upper() for name in names]

Result:
["JOHN", "SARAH", "MIKE"]

WHEN TO USE LIST COMPREHENSION
==============================
1. You want to create a new list
2. The transformation is simple
3. The logic is easy to read
4. You are filtering simple conditions

DO NOT USE IT EVERYWHERE
========================
List comprehension is NOT automatically better.
If the logic becomes complicated,
use a normal for loop.

Good:
squares = [x * x for x in numbers]
Less readable:

result = [
    complicated_function(x, y)
    for x in data
    if condition1(x)
    if condition2(x)
]

If the logic is complex:
Use a normal loop.

FILTERING WITH LIST COMPREHENSION
=================================
You can use an IF condition.

Basic pattern:
[expression for item in iterable if condition]

Example:
numbers = [1, 2, 3, 4, 5, 6]
even_numbers = [x for x in numbers if x % 2 == 0]

Result:
[2, 4, 6]

NORMAL LOOP VERSION
-------------------
even_numbers = []
for x in numbers:
    if x % 2 == 0:
        even_numbers.append(x)


COMPREHENSION VERSION
---------------------
even_numbers = [x for x in numbers if x % 2 == 0]

TRANSFORMATION + FILTER
=======================
numbers = [1, 2, 3, 4, 5]
result = [x * 10 for x in numbers if x > 2]

Result:
[30, 40, 50]

Meaning:
1. Loop through numbers
2. Check x > 2
3. Multiply matching values by 10
4. Put them into a new list

ETL EXAMPLE
===========
records = [
    {"id": 1, "status": "active"},
    {"id": 2, "status": "inactive"},
    {"id": 3, "status": "active"}
]
Get active IDs:
active_ids = [
    record["id"]
    for record in records
    if record["status"] == "active"
]

Result:
[1, 3]

ANOTHER ETL EXAMPLE
===================
records = [
    {"name": "John", "age": 30},
    {"name": "Sarah", "age": 25},
    {"name": "Mike", "age": 40}
]

Get names:
names = [record["name"] for record in records]

Result:
["John", "Sarah", "Mike"]


GET NAMES OF PEOPLE OVER 30
---------------------------
names = [
    record["name"]
    for record in records
    if record["age"] > 30
]

Result:
["Mike"]

IMPORTANT:
==========
List comprehension creates a NEW LIST.

Example:
result = [x * 2 for x in numbers]

TIME COMPLEXITY
===============
A list comprehension that loops through n items:  → O(n)

Example:
[x * 2 for x in numbers]
If numbers contains 1,000 items:  → approximately 1,000 iterations

SPACE COMPLEXITY
================
The resulting list stores n items: → O(n)

LIST COMPREHENSION VS NORMAL LOOP
=================================
NORMAL LOOP:
result = []
for x in numbers:
    result.append(x * 2)


LIST COMPREHENSION:
result = [x * 2 for x in numbers]

Both:
Time → O(n)
Space → O(n)

WHEN NOT TO USE LIST COMPREHENSION
==================================
Avoid it when:
1. Logic is complicated
2. Multiple nested loops make it difficult to read
3. You need several statements
4. You need exception handling
5. You need debugging/logging inside the loop
6. You are not actually creating a list

Example where normal loop is better:
result = []
for record in records:
    try:
        value = transform(record)
        validate(value)
        result.append(value)
    except Exception:
        log_error(record)

VERY IMPORTANT INTERVIEW POINT
==============================
Q: Should we always use list comprehension?
No.Use list comprehension when it makes simple
transformation or filtering more concise and readable.

For complex business logic, a normal for loop is
usually more readable and maintainable.

EASY MEMORY RULE
================
TRANSFORM:
[x * 2 for x in numbers]
FILTER:
[x for x in numbers if x > 10]
TRANSFORM + FILTER:
[x * 2 for x in numbers if x > 10]

GENERAL PATTERN:
[expression for item in iterable if condition]

NORMAL LOOP → COMPREHENSION
===========================
result = []
for x in data:
    if condition:
        result.append(expression)
becomes:
result = [
    expression
    for x in data
    if condition
]

FOR YOUR 5-YOE PYTHON / ETL INTERVIEW
=====================================
Know these patterns:
1. Transform records
2. Extract fields from dictionaries
3. Filter records
4. Transform + filter
5. Know when NOT to use comprehension
6. Know O(n) time and O(n) output space

KEY EXAMPLES TO REMEMBER
========================
# Extract IDs
ids = [record["id"] for record in records]

# Filter IDs
ids = [
    record["id"]
    for record in records
    if record["status"] == "active"
]

# Transform values
squares = [x * x for x in numbers]
# Filter numbers
even = [x for x in numbers if x % 2 == 0]

FINAL MEMORY
============

List comprehension =
CREATE NEW LIST
+
OPTIONAL FILTER
+
OPTIONAL TRANSFORMATION

Basic:
[expression for item in iterable]

With filter:
[expression for item in iterable if condition]

DO NOT use it just because it is shorter.
Use it when it makes the code CLEAR and READABLE.
