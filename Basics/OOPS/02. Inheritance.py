class Animal:
    def speak(self):
        print("Animal speaks")


class Dog(Animal):
    pass


dog = Dog()
dog.speak()



class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} makes a sound")


# Inherit from Animal
class Cat(Animal):
    def speak(self):
        print(f"{self.name} says Meow!")
      

cat = Cat("Whiskers")
cat.speak()    # ➜ Whiskers says Meow!
