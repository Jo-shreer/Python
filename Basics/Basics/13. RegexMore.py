# ✅ Common Regex Patterns in Python (for copy-paste use)

import re

# --------------------------
# 🔹 1. Character Classes
# --------------------------

# \d  : Digit (0–9)
# \D  : Not a digit
# \w  : Word character (letters, digits, underscore)
# \W  : Not a word character
# \s  : Whitespace (space, tab, newline)
# \S  : Not whitespace

text = "User123 @ 5pm"
print(re.findall(r"\d", text))   # ['1', '2', '3']
print(re.findall(r"\w", text))   # ['U', 's', 'e', 'r', '1', '2', '3']
print(re.findall(r"\s", text))   # [' ', ' ']

# --------------------------
# 🔹 2. Quantifiers
# --------------------------

# *   : 0 or more repetitions
# +   : 1 or more repetitions
# ?   : 0 or 1 (optional)
# {n} : Exactly n times
# {n,}: At least n times
# {n,m}: Between n and m times

text = "aa ab aaaa a"
print(re.findall(r"a+", text))     # ['aa', 'a', 'aaaa', 'a']
print(re.findall(r"a{2}", text))   # ['aa', 'aa']

# --------------------------
# 🔹 3. Anchors
# --------------------------

# ^ : Start of string
# $ : End of string
# \b: Word boundary
# \B: Not a word boundary

text1 = "Python is powerful"
text2 = "Start with Python"
print(re.findall(r"^Python", text1))  # ['Python']
print(re.findall(r"Python$", text2))  # []

# Word boundary example
text = "code coders coding"
print(re.findall(r"\bcod", text))     # ['cod']
print(re.findall(r"cod\b", text))     # ['cod']

# --------------------------
# 🔹 4. Groups and Alternation
# --------------------------

# ()     : Grouping
# |      : OR (alternation)

text = "cat bat rat"
print(re.findall(r"c|b", text))         # ['c', 'b']
print(re.findall(r"(cat|bat)", text))   # ['cat', 'bat']

# --------------------------
# 🔹 5. Character Sets
# --------------------------

# [abc]     : Matches a, b, or c
# [a-z]     : Any lowercase letter
# [^abc]    : NOT a, b, or c

text = "abc xyz 123"
print(re.findall(r"[a-z]", text))     # all lowercase letters
print(re.findall(r"[^a-z]", text))    # excludes lowercase letters

# --------------------------
# 🔹 6. Email Regex Example
# --------------------------

text = "Contact me at test123@example.com"
email_pattern = r"\b[\w.-]+@[\w.-]+\.\w+\b"

match = re.search(email_pattern, text)
if match:
    print("Email found:", match.group())
# Output: Email found: test123@example.com









| Feature  | `re.search()`                       | `re.findall()`                     |
| -------- | ----------------------------------- | ---------------------------------- |
| Finds    | First match only                    | All matches                        |
| Returns  | Match object                        | List of strings                    |
| Use case | Presence check or extract one match | Extracting all occurrences         |
| Stops at | First match                         | Continues through the whole string |

