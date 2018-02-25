# Import requests (to download the page)
import requests
import datetime
import pickle
import os
import sys

# Import BeautifulSoup (to parse what we download)
from bs4 import BeautifulSoup

# Import the email modules we'll need
from email.message import EmailMessage

# Import Time (to add a delay between the times the scape runs)
import time

# Import smtplib (to allow us to email)
import smtplib

# restore last result set from disk
f=open('bikes.bin','rb')
oldset=pickle.load(f)
f.close()

# url that lists all blems
url = "http://ibd.specialized.com/bb/SBCBBBlemsPicker.jsp"
# set the headers like we are a browser,
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# cookie to allow access to URL (i think this expires once a month)
jar = requests.cookies.RequestsCookieJar()
cookie = str(os.environ.get('GOLD_COOKIE'))
jar.set('GOLD', cookie, domain='', path='')

# download all the blems
response = requests.get(url, headers=headers, cookies=jar)
if response.status_code != 200:
    print("error making request")
    sys.exit()
# parse the downloaded data and pull out just the names
# this will stop working if the site structure changes
soup = BeautifulSoup(response.text, "lxml")
bikes = soup("td","price") 
newset=set(map((lambda x: x.text), bikes))

# find items that were not there last time we checked
setdiff=newset-oldset

# uncomment to debug
#import pdb; pdb.set_trace()

# send an email if there are any new items
if len(setdiff) > 0 and len(setdiff) < 100:
    print(str(setdiff))

    msg = EmailMessage()
    msg.set_content(str(setdiff))

    email = str(os.environ.get('MY_EMAIL'))
    pword = str(os.environ.get('MY_PWORD'))
    msg['Subject'] = 'new stuff'
    msg['From'] = email
    msg['To'] = ['christianwparker@yahoo.com', 'johnwilde@gmail.com']

    # setup the email server,
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # add my account login name and password,
    server.login(email, pword)

    # Send the message via our own SMTP server.
    server.send_message(msg)
    server.quit()

# print time so we know script is running
print(str(datetime.datetime.now()))

# save the last results
oldset = newset

# save to disk in case process dies
f=open('bikes.bin','wb')
pickle.dump(oldset, f)
f.close()
