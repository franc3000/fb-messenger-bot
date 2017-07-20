import json
import os
import random
import sys
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

msg = [
    "Success is the ability to go from failure to failure without losing your enthusiasm",
    "Fall seven times, stand up eight. - Japanese Proverb",
    "Hold fast to dreams, for if dreams die, life is a broken-winged bird that cannot fly. - Langston Hughes",
    "Where there is no hope, we must invent hope. - Albert Camus",
    "Do you want to know who you are? Don't ask. Act! Action will delineate and define you. - Thomas Jefferson",
    "Do one thing every day that scares you. Eleanor Roosevelt",
]


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    # from flask import Flask, render_template
    # return render_template('index.html')
    timestamp = datetime.today().strftime("%A, %B %d, %Y at %H:%M:%S")
    html = """
    <html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css" integrity="sha384-rwoIResjU2yc3z8GV/NPeZWAv56rSmLldC3R/AZzGRnGxQQKnKkoFVhFQhNUwEyJ" crossorigin="anonymous">
    </head>
    <body>
    <div class="container">
      <div class="header clearfix">
        <nav>
        </nav>
        <h3 class="text-muted"> </h3>
      </div>

      <div class="jumbotron">
        <h1 class="display-2">I'm a chatbot for Extraordinary Comebacks</h1>
        <p class="lead">It's {TIME}</p>
      </div>
      
      <center>
      <div class="row marketing">
        <div class="col-lg-4">
          <h4>#1</h4>
          <p>{a}</p>
        </div>

        <div class="col-lg-4">
          <h4>#2</h4>
          <p>{b}</p>
        </div>

        <div class="col-lg-4">
          <h4>#3</h4>
          <p>{c}</p>
        </div>
    </div>
    </center>

      <footer class="footer">
        <p>&copy; Pareto.AI 2017</p>
      </footer>

    </div> <!-- /container -->
    """.format(TIME=timestamp, a=msg[0], b=msg[1], c=msg[2])
    return html, 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    timestamp = datetime.today().strftime("%A, %B %d, %Y at %H:%M:%S")
    log(timestamp)
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    
                    # the recipient's ID, which should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]

                    # send a random quote
                    index = random.randint(0,len(msg))
                    send_message(sender_id, msg[index])

                if messaging_event.get("delivery"):
                    # delivery confirmation
                    pass

                if messaging_event.get("optin"):  
                    # optin confirmation
                    pass

                if messaging_event.get("postback"):
                    # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    """."""
    log("sending message to {recipient}: {text}".format(
        recipient=recipient_id, text=message_text))

    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(debug=True)
