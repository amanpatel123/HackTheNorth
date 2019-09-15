from flask import Flask, request, render_template
import requests
from pyrebase import pyrebase
import sched, time


s = sched.scheduler(time.time, time.sleep)


config = {
  "apiKey": "AIzaSyBrTraklyfhPk2BNhPsmw_djvKwVSy7oF4",
  "authDomain": "pricechecker-71a78.firebaseapp.com",
  "databaseURL": "https://pricechecker-71a78.firebaseio.com",
  "storageBucket": "pricechecker-71a78.appspot.com"
}

app = Flask(__name__)
# scheduler = BackgroundScheduler()


FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'aBaNIgB/sj70tCgtPpK50ZIf9fHLVTx/S1V/A4P6STM='
PAGE_ACCESS_TOKEN = 'EAAGfED5iSXUBADpODELNQ5L91rQTVcc4oZBeNMPX6blm3qCpdIdnkcD5aGXqL6mP2YnGv6jjl1q6NlbYs9EZCz4ij3bP0JHJIZCtK4vZBSKrrnfNLDJweZCZASrtVfRPbJcaD8yFs6g373aSfrAJVDIDJSpu3RYQeSOZCnghM6mLQZDZD'


def trigger(url, userid):
    checkDatabaseTask(url, userid)


def get_bot_response(message):
    """This is just a dummy function, returning a variation of what
    the user said. Replace this function with one connected to chatbot."""
    return 'I will keep a track of the provided URL!'

def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response = get_bot_response(message)
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


def pushItem(url, userId):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    try:
        all_datas=db.child("DATA").get().val()
        for key, data in all_datas.items():
            user_id = data["userId"]
            URL = data["URL"]
            if user_id == userId and url == URL:
                strw = "Item is already being monitored. Kindly provide the URL of new element"
                print("Item is already being monitored. Kindly provide the URL of new element")
                send_message(userId, strw)
                return
    except:
        print("Nothing Found")
    newItem = {"userId": userId, "pname": "null", "URL": url,   "initial_price": "null", "lowest_price":"null" ,"difference": "null" , "change": "null"}
    db.child("DATA").push(newItem)

def checkDatabaseTask(url, userId):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    try:
        a=db.child("DATA").get()
        all_datas = a.val()
        for key, data in all_datas.items():
            user_id=data["userId"]
            user_url=data["URL"]
            if user_id==data["userId"] and url==user_url:
                change = data["change"]
                if change==1:
                    difference=data["difference"]
                    string=str.format("The price goes down by ${}", difference)
                    difference=data["difference"]
                    string=str.format("The price has decreased by ${}, time to consider buying it!", difference)
                    difference=data["difference"]
                    string=str.format("The price went down by ${}", difference) 
                    print("*****************\n",string,"\n**************")
                    send_message(userId, string)
    except:
        print("lol")
    
   
@app.route("/webhook", methods=['GET','POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                print("user sends msg")
                text = x['message']['text']
                sender_id = x['sender']['id']
                pushItem(text, sender_id)
                checkDatabaseTask(text, sender_id)
                respond(sender_id, text)
                i = 0
                while(i < 1000):
                    s.enter(10000, 1, trigger, argument=(text, sender_id))
                    i += 1
                    print("____________\n")
        return "ok"

@app.route("/")
def home():
    return render_template("home.html")




if __name__ == "__main__":
    app.run(debug=True)
