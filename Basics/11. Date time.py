from datetime import datetime, date, time, timedelta

# 1️⃣ Current Date and Time
now = datetime.now()
print("Now:", now)

# 2️⃣ Creating Specific Date and Time
my_date = date(2025, 7, 10)
my_time = time(14, 30, 0)
print("Date:", my_date)
print("Time:", my_time)

# 3️⃣ Formatting Dates
formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
print("Formatted Now:", formatted_date)

formatted_long = now.strftime("%A, %B %d, %Y")
print("Formatted Long:", formatted_long)

# 4️⃣ Parsing String to Date
date_str = "2025-07-10 14:30:00"
parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print("Parsed Date:", parsed_date)

# 5️⃣ Date Arithmetic
today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)
print("Today:", today)
print("Tomorrow:", tomorrow)
print("Yesterday:", yesterday)

# 6️⃣ Difference Between Dates
difference = tomorrow - today
print("Difference in days:", difference.days)




op
Now: 2025-07-10 14:23:45.123456
Date: 2025-07-10
Time: 14:30:00
Formatted Now: 2025-07-10 14:23:45
Formatted Long: Thursday, July 10, 2025
Parsed Date: 2025-07-10 14:30:00
Today: 2025-07-10
Tomorrow: 2025-07-11
Yesterday: 2025-07-09
Difference in days: 1

