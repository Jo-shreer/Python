Regex is a powerful way to search, match, and manipulate text using patterns.
Python provides the re module to work with regex.

#
#re.search() scans through the string to find the first location where the regex pattern matches.
#The regex pattern r"\d{3}-\d{3}-\d{4}" means:
#\d{3}: exactly 3 digits
#- : a hyphen (dash)
#\d{3}: exactly 3 digits
#- : a hyphen (dash)
#\d{4}: exactly 4 digits
#This matches phone numbers like 123-456-7890.


| Pattern | Description                          | Example Matches       |
| ------- | ------------------------------------ | --------------------- |
| `\d`    | Digit (0–9)                          | `0`, `5`, `9`         |
| `\D`    | Not a digit                          | `a`, `-`, `@`         |
| `\w`    | Word character (letters, digits, \_) | `a`, `Z`, `0`, `_`    |
| `\W`    | Not a word character                 | `@`, `#`, ` ` (space) |
| `\s`    | Whitespace (space, tab, newline)     | ` `, `\t`, `\n`       |
| `\S`    | Not whitespace                       | `a`, `9`, `.`         |




#

import re

text = "My phone number is 123-456-7890."

# Search for a phone number pattern
match = re.search(r"\d{3}-\d{3}-\d{4}", text)

if match:
    print("Found phone number:", match.group())
else:
    print("No phone number found.")




op
Found phone number: 123-456-7890

