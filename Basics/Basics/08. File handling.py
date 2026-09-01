# Write to a file
with open("example.txt", "w") as f:
    f.write("Hello, file!")



# Read from a file
with open("example.txt") as f:
    content = f.read()
    print(content)
  
