@decorator means: say_hello = decorator(say_hello)
The wrapper() function adds behavior before and 
after calling the original function.
####################

def decorator(func):
    def wrapper():
        print("Before the function runs")
        func()
        print("After the function runs")
    return wrapper

@decorator
def say_hello():
    print("Hello!")

say_hello()

op
Before the function runs
Hello!
After the function runs

