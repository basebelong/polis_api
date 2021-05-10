#!/usr/bin/env python3

import requests
import json
import os
import sys
import mysql.connector
from datetime import datetime

try:
    db_server = os.environ['PA_DBSERVER']
    db_user = os.environ['PA_USER']
    db_password = os.environ['PA_PASSWORD']
    db_database = os.environ['PA_DATABASE']
except:
    print(f"Error: Environment variables not set. Please make sure ", end="")
    print(f"PA_DBSERVER, PA_USER, PA_PASSWORD, PA_DATABASE are set.")
    sys.exit(2)

db = mysql.connector.connect(
    host=db_server,
    user=db_user,
    password=db_password,
    database=db_database
)

if db:
    print("Connected!")
    cursor = db.cursor()
else:
    print("Failed!")

r = requests.get("https://polisen.se/api/events")

if r:
    data = r.json()
    print("Data downloaded.")
else:
    print("Error downloading data.")

print(f"Inserting data to database ...", end="")
for i in range(500):
    id = data[i]['id']
    type = data[i]['type']
    date = (datetime.strptime(data[0]['datetime'],
        "%Y-%m-%d %H:%M:%S +02:00").strftime("%Y-%m-%d"))
    time = (datetime.strptime(data[i]['datetime'],
        "%Y-%m-%d %H:%M:%S +02:00").strftime("%H:%M"))
    time_with_sec = (datetime.strptime(data[i]['datetime'],
        "%Y-%m-%d %H:%M:%S +02:00").strftime("%H:%M:%S"))
    name = data[i]['name']
    location = data[i]['location']['name']
    gps = data[i]['location']['gps']
    summary = data[i]['summary']
    url = data[i]['url']
#    print(f"{date.ljust(12)}{time.ljust(7)}{location.ljust(16)}\t{type}")

    sql = ("INSERT IGNORE INTO polis_handelser (id, type, date, time, name, summary, location, gps, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    val = (id, type, date, time_with_sec, name, summary, location, gps, url) 
    cursor.execute(sql, val)
    db.commit()
    
    if i % 10 == 0:
        print(f".", end = "")

cursor.close()
db.close()
print(f"Done!")

