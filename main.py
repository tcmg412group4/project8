from flask import Flask, jsonify, request, abort
import hashlib                                              # used for MD5 Hash
import requests                                             # used for slack alert
import requests
import redis 

app = Flask(__name__)

r = redis.Redis(host="redis-server", port=6379, decode_responses=True)                              # port 6379 for redis

slackURL = "" 

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


#########################################
#########################################
#########################################
## CRUD functions #######################

@app.route("/keyval", methods=["POST", "PUT"])

def POST():
    
    user_input = request.get_json()
    
    if request.method == "POST":
        
        cmd = "CREATE " + user_input["key"] + "/" + user_input["value"]
        
        if r.exists(user_input["key"]):
            #build return val to return if key is found
            KeyFound = {
                "Key" : user_input["key"],
                "Value" : user_input["value"],
                "Command" : cmd,
                "Result" : False,
                "Error" : "Unable to add key pair: key already exists"
            }
            # return json object and abort code
            return jsonify(KeyFound), abort(409)
        # if key is not found
        else:
            key = user_input["key"]
            value = user_input["value"]
            r.set(key, value)

            #build return val to return if key is not found
            createKeyVal = {
                "Key" : key,
                "Value" : value,
                "Command" : cmd,
                "Result" : True,
                "Error" : ""
            }
            return jsonify(createKeyVal), 200
        
    elif request.method == "PUT":

        cmd = "CREATE " + user_input["key"] + "/" + user_input["value"]
        key = user_input["key"]
        value = user_input["value"]

        if r.exists(user_input["key"]):
            r.set(key, value)

            keypair = {
                "Key" : key,
                "Value" : value,
                "Command" : cmd,
                "Result" : True,
                "Error" : ""
            }
            return jsonify(keypair)
        else:
            keypair = {
                "Key" : key,
                "Value" : value,
                "Command" : cmd,
                "Result" : False,
                "Error" : "Key not found"
            }
            return jsonify(keypair)


@app.route("/keyval/<string:input>", methods=['GET', 'DELETE'])
def GET(input):

    if request.method == 'GET':

        cmd = "READ value for key " + input

        if r.exists(input):
            value = r.get(input)
            keypair = {
                "Key" : input,
                "Value" : value,
                "Command" : cmd,
                "Result" : True,
                "Error" : ""
            }
            return jsonify(keypair)
        else:
            keypair = {
                "Key" : input,
                "Value" : value,
                "Command" : cmd,
                "Result" : False,
                "Error" : "Key not found"
            }
            return jsonify(keypair)
        
    elif request.method == 'DELETE':

        cmd = "DELETE value for key " + input

        if r.exists(input) == 1:
            value = r.get(input)
            r.delete(input)
            keypair = {
                "Key" : input,
                "Value" : value,
                "Command" : cmd,
                "Result" : True,
                "Error" : ""
            }
            return jsonify(keypair)
        else:
            keypair = {
                "Key" : input,
                "Value" : value,
                "Command" : cmd,
                "Result" : False,
                "Error" : "Unable to delete key: Key not found"
            }
            return jsonify(keypair)
             




if __name__ == "__main__":                                  # debug mode for testing, port 4000 as per assignment instructions
    app.run(host='0.0.0.0',port=4000, debug=True)