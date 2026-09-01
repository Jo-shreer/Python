

def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@decorator
def add(a, b):
    return a + b

print(add(5, 3))


op
Before
After
8
