import sqlite3

connection = sqlite3.connect("magic.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE cards
       (id INTEGER PRIMARY KEY,
        multiverseid TEXT, 
        title TEXT,
        manaCost TEXT,
        convertedManaCost TEXT,
        type TEXT,
        rules TEXT,
        cardSet TEXT,
        rarity TEXT,
        image BLOB)
""")


