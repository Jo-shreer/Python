polymorphism using inheritance, specifically method overriding.

class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} makes a sound")


class Cat(Animal):
    def speak(self):
        print(f"{self.name} says Meow!")
      

cat = Cat("Whiskers")
cat.speak()    # ➜ Whiskers says Meow!

*********************************************************************************************

class Bird:
    def speak(self):
        print("Chirp chirp")

class Duck:
    def speak(self):
        print("Quack quack")

# Polymorphism in action

for animal in [Bird(), Duck()]:
    animal.speak()


op
# ➜ Chirp chirp
# ➜ Quack quack
