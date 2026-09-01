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
