LIST
====
WHAT IS A LIST?
---------------
A list is an ordered collection of values.
Example:
numbers = [10, 20, 30, 40]
The order is maintained.

Index:
0 → 10
1 → 20
2 → 30
3 → 40

WHEN TO USE LIST
================
Use a list when you need:
1. Ordered data
2. Duplicate values
3. Index-based access
4. To store multiple records
5. To loop through data
6. A collection that can grow/change

CREATE A LIST
-------------
numbers = [10, 20, 30, 40]
names = ["John", "Sarah", "Mike"]

ACCESS BY INDEX
---------------
numbers = [10, 20, 30]
numbers[0]
→ 10
numbers[1]
→ 20
numbers[2]
→ 30

IMPORTANT:
Python indexes start at 0.

NEGATIVE INDEX
--------------

numbers = [10, 20, 30]
numbers[-1]
→ 30

numbers[-2]
→ 20

-1 means:
→ last element

CHANGE A VALUE
--------------
numbers = [10, 20, 30]
numbers[1] = 50
Result:
[10, 50, 30]

ADD TO END — append()
---------------------
numbers = [10, 20]
numbers.append(30)
Result:
[10, 20, 30]
append()
→ adds one item to the END.

ADD AT POSITION — insert()
--------------------------
numbers = [10, 20, 30]
numbers.insert(1, 99)
Result
[10, 99, 20, 30]

Pattern:
list.insert(index, value)

REMOVE BY VALUE — remove()
--------------------------
numbers = [10, 20, 30]
numbers.remove(20)

Result:
[10, 30]

IMPORTANT:
remove() removes the first matching value.


REMOVE BY INDEX — pop()
-----------------------

numbers = [10, 20, 30]
x = numbers.pop(1)
x
→ 20
numbers
→ [10, 30]

pop() without an index:
numbers.pop()
Removes and returns the LAST item.

CHECK MEMBERSHIP
----------------
numbers = [10, 20, 30]
20 in numbers
→ True

LOOP THROUGH LIST
-----------------
numbers = [10, 20, 30]

for number in numbers:
    print(number)

Output:
10
20
30

LIST LENGTH
-----------
numbers = [10, 20, 30]
len(numbers)
→ 3

SLICING
=======
Slicing gets a portion of a list.
numbers = [10, 20, 30, 40, 50]

numbers[1:4]
Result:
[20, 30, 40]

Pattern:
list[start:end]

IMPORTANT:
The END index is NOT included.

Example:
numbers[0:3]

→ [10, 20, 30]

COPY A LIST
===========
a = [1, 2, 3]
b = a.copy()

Now b is a separate shallow copy of the list.

LIST CAN CONTAIN DUPLICATES
===========================
numbers = [1, 2, 2, 3, 3]
Duplicates are allowed.
This is different from a SET.

LIST VS SET
===========
LIST:
[1, 2, 2, 3]
→ ordered
→ duplicates allowed
→ index access

SET:
{1, 2, 3}
→ unique values
→ no normal index access
→ fast membership checking

LIST VS DICTIONARY
==================
LIST:
["John", "Sarah", "Mike"]
Use when:
→ order/sequence matters
→ you access by position

DICTIONARY:
{
    101: "John",
    102: "Sarah"
}

Use when:
→ key → value mapping is needed
→ you want lookup by key

IMPORTANT LIST METHODS
======================
append(x) → add to end
insert(i, x) → add at index
remove(x) → remove first matching value
pop(→ remove last value
pop(i) → remove value at index
clear() → remove everything
sort() → sort list in place
reverse() → reverse list in place
copy() → shallow copy

LIST COMPLEXITY
===============
Access by index:
list[i] → O(1)
Append:
append() → O(1) amortized
Search:
x in list → O(n)

Remove by value:
remove(x) → O(n)

Insert at beginning:
insert(0, x) → O(n)

Pop from end:
pop() → O(1)

Pop from beginning:
pop(0) → O(n)

WHY pop(0) IS O(n)
==================
List : [A, B, C, D]
pop(0)
A is removed.
Remaining elements need to shift:
[B, C, D]
Therefore:
→ O(n)

FOR ETL
=======
Lists are commonly used for:
1. Collection of records

records = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Sarah"}
]

2. API response data

response = [
    {...},
    {...},
    {...}
]

3. Batch processing
batch = [record1, record2, record3]

4. Storing transformed records
transformed = []
for record in records:
    transformed.append(process(record))

IMPORTANT INTERVIEW QUESTION
============================

Q: When would you use a list instead of a set?
Use a list when order, duplicates, or index-based access
are required.

Use a set when uniqueness and fast membership checking
are more important.

EASY MEMORY RULE
================
LIST
→ ORDERED
→ DUPLICATES ALLOWED
→ INDEX ACCESS
→ SEARCH O(n)

SET
→ UNIQUE
→ FAST MEMBERSHIP
→ AVERAGE O(1)

DICTIONARY
→ KEY → VALUE
→ FAST LOOKUP
→ AVERAGE O(1)

NEXT TOPIC
==========
LIST COMPREHENSION
Normal loop:  Not recommended

result = []
for x in numbers:
    result.append(x * 2)

Can be written as:
result = [x * 2 for x in numbers]
This is the next important Python pattern.
