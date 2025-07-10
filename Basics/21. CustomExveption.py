def vote(age):
    if age < 18:
        raise ValueError("You must be 18 or older to vote")
    return "You can vote!"

try:
    print(vote(16))
except ValueError as e:
    print("Error:", e)


op
Error: You must be 18 or older to vote
