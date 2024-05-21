import mysql.connector

dataBase = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'Password531!'
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE que_main_db")

print("Done!!")