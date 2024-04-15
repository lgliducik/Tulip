from database import mycol

# Define a document (similar to a row in SQL databases)
mydict = [{"day": "monday", "activity": ["школа 8:30 - 14:45", "гимнастика 16:00 - 18:00"]},
          {"day": "tuesday", "activity": ["школа 8:30 - 14:45", "библиотека 15:50 - 16:50"]},
          {"day": "wednesday", "activity": ["школа 8:30 - 12:15", "музыка 13:45 - 14:45", "гимнастика 17:30 - 19:00"]},
          {"day": "thursday", "activity": ["школа 8:30 - 14:45", "минимайкеры 14:45 - 15:45", "русский 18:00 - 19:00"]},
          {"day": "friday", "activity": ["школа 8:30 - 12:15", "гимнастика 16:00 - 18:00"]},
          {"day": "saturday", "activity": []},
          {"day": "sunday", "activity": []}]

# Insert the document into the collection
for day in mydict:
    mycol.insert_one(day)

print("Document inserted successfully.")
