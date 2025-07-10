#before lamda
# Regular function

def add(x, y):
    return x + y

print(add(3, 5))  # ➜ 8



# Lambda function equivalent
add_lambda = lambda x, y: x + y
print(add_lambda(3, 5))  # ➜ 8

#lamda using with map
numbers = [1, 2, 3, 4]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # ➜ [1, 4, 9, 16]

#lamda using with filter
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # ➜ [2, 4, 6]


#lamda sorted by key
pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
sorted_pairs = sorted(pairs, key=lambda x: x[1])
print(sorted_pairs)
# ➜ [(4, 'four'), (1, 'one'), (3, 'three'), (2, 'two')]

pairs = [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
# sorted() function sorts the list 'pairs'
# key=lambda x: x[1] tells sorted() to use the second item of each tuple as the sorting key
#resulting alphabetical order
sorted_pairs = sorted(pairs, key=lambda x: x[1])

print(sorted_pairs)
# Output: [(4, 'four'), (1, 'one'), (3, 'three'), (2, 'two')]



