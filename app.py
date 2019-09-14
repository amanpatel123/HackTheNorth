from flask import Flask, request, render_template
import requests
from pyrebase import pyrebase

config = {
  "apiKey": "AIzaSyBrTraklyfhPk2BNhPsmw_djvKwVSy7oF4",
  "authDomain": "pricechecker-71a78.firebaseapp.com",
  "databaseURL": "https://pricechecker-71a78.firebaseio.com",
  "storageBucket": "pricechecker-71a78.appspot.com"
}

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'aBaNIgB/sj70tCgtPpK50ZIf9fHLVTx/S1V/A4P6STM='
PAGE_ACCESS_TOKEN = 'EAAGfED5iSXUBABjOntWKe6dEqhtpK5qAZAhHKvaqXdqKzZAfez3miGnbreftfyTzuKRyMDZCf0WAOHBLsawX2NiibqMoVTpDNgW7YE8QaO3akWwi694WfOBQVxIAAowMHK32sOBvvyoskb3ZBuBD1eIEpX6oG0bd6JrsZCszZBXwZDZD'


def get_bot_response(message):
    """This is just a dummy function, returning a variation of what
    the user said. Replace this function with one connected to chatbot."""
    return "This is a dummy response to '{}'".format(message)


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

counter = 0
def pushItem(url, userId):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    newItem = {"userId": userId, "pname": None, "URL": url,   "initial_price": None, "lowest_price":None ,"difference": None , "change": None}
    counter+=1
    db.child("DATA").child(counter).set(newItem)


@app.route("/webhook", methods=['GET','POST'])
def listen():
    print("listening code")
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        print("start listening")
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            print("start x in event")
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                print("start before push item")
                pushItem(text, sender_id)
                
                print("after push item")
                respond(sender_id, text)

        return "ok"






@app.route("/")
def home():
    return render_template("home.html")




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

if __name__ == "__main__":
    app.run(debug=True)