from flask import Flask, jsonify, request, abort
from redis import Redis, RedisError
import redis
import hashlib                                              # used for MD5 Hash
import requests                                             # used for slack alert
import os
import socket
import json 


r = Redis(host="redis", port=6379, db=0, decode_responses=True)


app = Flask(__name__)

slackURL = "https://hooks.slack.com/services/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" 

#default local host page
@app.route("/")

def hello_world():
    return "<p>Howdy! We are Group 4. This is our API.</p>"


#MD5
@app.route("/md5/<string:strvalue>")

def md5(strvalue):
    md5val = hashlib.md5(strvalue.encode())
    hexval = md5val.hexdigest()
    return jsonify(
        input=strvalue,
        output=hexval
    )


#factorial
@app.route("/factorial/<int:x>")

def factorial(x):

    fact = 1
    if x < 0:
        return jsonify(
            input=x,
            output="Error, the input must be a positive integer"
        )       
    elif x == 0:
        return jsonify(
            input=x,
            output=1
        )    
    else:
        for i in range(1,x+1):
            fact = fact * i
        return jsonify(
            input=x,
            output=fact
        )
     
        
# fibonacci
@app.route("/fibonacci/<int:x>")

def fibonacci_num(x):
    num1= 0
    num2 = 1
    seq=[0]

    if x < 0:
        return jsonify(
            input=x,
            output="Please enter a positive integer"
        )
       
    elif x == 0:
        return jsonify(
            input=x,
            output=seq
            )

    elif x == 1:
        while num2 < 2:
            seq.append(num2)
            num1, num2 = num2, num1+num2
        return jsonify(
            input=x,
            output=seq
        )

    else:
        while num2 <= x:
            seq.append(num2)
            num1, num2 = num2, num1+num2
            
        return jsonify(
            input=x, 
            output=seq
        )              


# is-prime
@app.route("/is-prime/<int:n>")

def prime(n):
    flag = True
    
    if n == 1 or n == 0:
        flag = False
        return jsonify(
            input=n,
            output=flag
        )
    elif n > 1:
        for i in range(2, n):
            if n % i == 0:
                flag = False
                return jsonify(
                    input=n,
                    output=flag
                )
    else:
        return jsonify(
            input=n,
            output="Error, Input is Invalid"
        )
    return jsonify(
        input=n,
        output=flag
    )    


#slack-alert
@app.route("/slack-alert/<string:post>")

def slack_alert(post):
    flag = True
    response = requests.post(slackURL, json={'text': post, 'username':"Group4restAPI_Bot"})
    if response.status_code == 200:
        return jsonify(
            input=post,
            output=flag
        )
    else:
        flag = False
        return jsonify(
            input=post,
            output=flag
        )


@app.route("/keyval", methods=[ "POST", "PUT"])
def postKeyval():
    data = request.get_json()
    
    if request.method == 'POST':
       command = "Create " + data["key"] + "/" + data["value"]
       if r.exists(data["key"]):
           #create object to return if it exists
           keypair_found = {
               "storage-key": data["key"],
               "storage-val": data["value"],
               "command": command,
               "result": False,
               "error": "Unable to add key pair: key already exists"
           } 
           return jsonify(keypair_found), abort(409)
       else:
           key = data["key"]
           value = data[value]
           r.set(key, value)

           keypair = {
               "storage-key": data["key"],
               "storage-val": data["value"],
               "command": command,
               "result": True,
               "error": ""
           }
           return jsonify(keypair)
    elif request.method == "PUT":
        command = "Update " + data["key"] + "/" + data["value"]
        key = data["key"]
        value = data["value"]
        if r.exists(data["key"]):
            r.set(key,value)
            keypair = {
               "storage-key": data["key"],
               "storage-val": data["value"],
               "command": command,
               "result": True,
               "error": ""
           }
            return jsonify(keypair)
        else:
            keypair_notfound = {
               "storage-key": data["key"],
               "storage-val": data["value"],
               "command": command,
               "result": False,
               "error": "Key does not exist"
           } 
            return jsonify(keypair_notfound), abort(404)


@app.route("/keyval/<string:inputval>", methods=["GET", "DELETE"])
def getKeyval(inputval):
    
    if request.method =="GET":
        command = "READ value for the following key: " + inputval
        if r.exists(inputval):
            value = r.get(inputval)
            keypair = {
               "storage-key": inputval,
               "storage-val": value,
               "command": command,
               "result": True,
               "error": ""
           }
            return jsonify(keypair)
        else:
             keypair_notfound = {
               "storage-key": inputval,
               "storage-val": "Not found",
               "command": command,
               "result": False,
               "error": "Key does not exist"
           }
             return jsonify(keypair_notfound), abort(404)

    elif request.method == "DELETE":
        command = "Delete the stored value for key: " + inputval
        if r.exists(inputval) == 1: # 1 is True
            value = r.get(inputval)
            r.delete(inputval)
            keypair_deleted = {
               "storage-key": inputval,
               "storage-val": value,
               "command": command,
               "result": True,
               "error": "Key pair was found and deleted from database"
           }
            return jsonify(keypair_deleted)
        else:
            keypair_notfound = {
               "storage-key": inputval,
               "storage-val": "Not found",
               "command": command,
               "result": False,
               "error": "Unable to delete key: Key does not exist"
           }
            return jsonify(keypair_notfound), abort(404)

   
if __name__ == "__main__":                                  # debug mode for testing, port 4000 as stated assignment instructions
    app.run(host='0.0.0.0',port=4000, debug=True)
