try:
    num = int("abc")  # invalid conversion
except Exception as e:
    print("Something went wrong:", e)



op
Something went wrong: invalid literal for int() with base 10: 'abc'
