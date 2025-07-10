def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))


op
Hello, Alice!



#function eith default argument 

def greet(name="stranger"):
    return f"Hello, {name}!"

print(greet())
print(greet("Bob"))


op
Hello, stranger!
Hello, Bob!


#with multiple arguments

def add(a, b):
    return a + b

print(add(3, 4))

op
7


