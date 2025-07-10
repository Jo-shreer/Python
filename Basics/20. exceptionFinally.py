try:
    print("Opening file...")
    f = open("fakefile.txt")
except FileNotFoundError:
    print("File not found!")
finally:
    print("Cleanup done.")



op
Opening file...
File not found!
Cleanup done.

