from selenium import webdriver
from flask import Flask
import pyrebase
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import json

config = {
  "apiKey": "AIzaSyBrTraklyfhPk2BNhPsmw_djvKwVSy7oF4",
  "authDomain": "pricechecker-71a78.firebaseapp.com",
  "databaseURL": "https://pricechecker-71a78.firebaseio.com",
  "storageBucket": "pricechecker-71a78.appspot.com"
}

app = Flask(__name__)


@app.route("/")

# run this script every day (manually for testing and demo)
def check_price(url):
    try:
        browser = webdriver.Chrome(executable_path=r'C:\chromedriver.exe')
        print("a")
        browser.get(url)
        print("a")
        try:
          price = browser.find_element_by_id("priceblock_ourprice").text[5:]
        except:
          try:
            price = browser.find_element_by_id("priceblock_dealprice").text[5:]
          except:
            price = browser.find_element_by_id("item_price").text
        print("a")
        price = float(price)
        print("a")
        browser.quit()
        print("a")
        return price
    except:
        return -1

# function to manipulate database:
def do_the_thing():   
  firebase = pyrebase.initialize_app(config)
  db = firebase.database()

  # fetch initial price from Firebase
  data = db.child("DATA").get()
  a = data.val()
  for key, value in a.items():

    #variables
    ID = value['userId']
    # pname = value['pname']
    lowest_price = value['lowest_price']  #initally null
    initial_price = value['initial_price'] # null
    change = value['change'] # null
    url = value['URL'] 
    difference = value['difference'] # null

    key_ = key
    # print(ID, pname, lowest_price, initial_price, change, url, difference)

    # parse price!
    current_price = check_price(url)
    print(current_price)
    if (initial_price == "null"):
      initial_price = check_price(url)

    result, lowest = 0, current_price

    if current_price != -1:
        if(current_price < initial_price):
            result = initial_price - current_price
            lowest = current_price
        elif(current_price > initial_price):
            result = current_price - initial_price
        else:
          result = 0 # no change in price

    if(current_price == initial_price):
      change = 0
    elif(current_price > initial_price):
      change = -1
    else:
      change = 1
    # update values in database

    db.child("DATA").child(key_).update({"change" : change, "difference" : result, "lowest_price" : lowest, "initial_price" : initial_price})


  # userid = 1
  
  # data = {"userId": userid, "pname": "Dryer", "URL": "https://www.amazon.ca/Revlon-Collection-Dryer-Volumizer-Count/dp/B01HZ5K8UE", "initial_price": 40, "lowest_price": "null", "difference": "null", "change": "null"}
  # db.child("DATA").push(data)


do_the_thing()
