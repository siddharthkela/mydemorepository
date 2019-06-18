from copy import deepcopy
import csv
import os
from flask import Flask, render_template, request,flash
import pypyodbc
import random
import redis
import numpy as np
# import scipy
import math

from time import time
# import itertools
# from sklearn.cluster import KMeans

app = Flask(__name__)
app.secret_key = "Secret"
connection = pypyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=tcp:sid74.database.windows.net,1433;Database=mydemodatabase;Uid=siddharth@sid74;Pwd=Keni1234;")
cursor = connection.cursor()
port = (os.getenv("VCAP_APP_PORT"))
r=redis.StrictRedis(host='mydemoredis.redis.cache.windows.net',port=6380, password='59xqmNAIAiWdMsnqzbhD+DLuS12ms5qjLFtBlDuFvXE=', ssl=True)
@app.route('/')
def index():
    starttime = time()
    result = r.ping()
    print("Ping returned : " + str(result))
    result = r.set("Message", "Hello!, The cache is working with Python!")
    print("SET Message returned : " + str(result))
    result = r.get("Message")
    print("GET Message returned : " + result.decode("utf-8"))
    endtime = time()
    timetaken = (starttime - endtime)
    return render_template('index.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():

    k = request.args.get("k")
    min = request.args.get("min")
    max = request.args.get("max")
    print(min)

    start_time = time()
    for i in range(0, int(k)):
     b="mycache"
     mag = random.uniform(float(min), float(max))
     cursor.execute("select * from quakes where mag>=" + min + "and mag<=" + max)
     result=cursor.fetchall()
     in_cache=False
     if r.get(b) != None:
         in_cache = True
         print('Cached')
         data=r.get(b)
         result = data
     else:
         print('Not Cached')
         cursor.execute("select * from quakes where mag>=" + min + "and mag<=" + max)
         get = cursor.fetchall();
         r.set(b,str(get))

    end_time = time()
    time_taken = (end_time - start_time)
    flash('The Average Time taken to execute the random queries is : ' + "%.4f" % time_taken + " seconds")
    return render_template('output.html',r=result,t=time_taken)
@app.route('/case',methods = ['POST', 'GET'])
def case():
    cursor = connection.cursor()
    k = request.args.get("k")
    i = int(k)
    query = "SELECT case \
    while i < 5:\
              when mag between " + str(i) + " and " + str(i + 0.01) + " then '" + str(i) + " and " + str(
            i + 0.01) + "' \
        i = i + 0.01\
            else 'OTHERS' end as 'mag', count(*) as 'count' from  quakes group by mag"
    print(query)
    cursor.execute(query)
    print(query)
    rows = cursor.fetchall()
    print(rows)
    connection.close()
    return render_template('case.html', r=rows)

@app.route('/count',methods = ['POST', 'GET'])
def count():

    mag = request.args.get("mag")
    cursor.execute("Select count(*) from quakes where mag>='"+mag+"'")
    rows=cursor.fetchall()

    return render_template('count.html', a=rows)

@app.route('/list',methods = ['POST', 'GET'])
def list():

    min = request.args.get("min")
    max = request.args.get("max")
    # loc = request.args.get("loc")
    cursor.execute("select  latitude, longitude, place from quakes where mag Between '"+min+"' and '"+max+"' ")
    rows=cursor.fetchall()
    print(rows)
    return render_template('list.html', ci=rows)

if __name__ == '__main__':
   app.run()
