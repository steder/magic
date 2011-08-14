import sqlite3

connection = sqlite3.connect("magic2010_images.db")
cursor = connection.cursor()
cursor.execute("select image from cards where id = 100;")
imageData = cursor.fetchone()[0]

print imageData
