import apiai
import json
import requests
from msg import *
from flask import Flask, request, render_template

app = Flask(__name__)

# Facebook Messenger Configuration
recipient_id = None
VTK = 'pythonchatbot'
PAT = 'EAAFZBS4wgWGgBAOId4696jh6b3kUgWLP4ozGKfBPH7mVDFpIY9ujY2GGs0NgCXWc9cZBIEE2LPLOwtplH5XNldzeFQ4z1DGMc2MxZCqKDa' \
      '2fY0tPZCun0CbApKXK4o5i8w6d2VM58IMytyg4vgAineLBNcyQaDElZAAAvxyN4Mz92wXy4fjp7Ey0mW5ZBq4r0ZD'

# Dialogflow Configuration
CAT = 'a7adb35ce07a4701af7f2383808622da'

# images
IMG_URL = 'https://i.giphy.com/xT0GqrJNbZkRcr2Jgc.gif'

def nlp_fallback(input_text, session_id):
    ai = apiai.ApiAI(CAT)
    req = ai.text_request()
    req.lang = 'en'  # 'sp' para español
    req.session_id = session_id
    req.query = input_text
    response = req.getresponse()
    raw = json.loads(response.read())
    if raw['status']['code'] == 200:
        response_text = raw['result']['fulfillment']['messages'][0]['speech']
    else:
        raise Exception('Dialogflow Exception:' + raw['status']['errorType'])
    return response_text


@app.route('/', methods=['GET'])
def verify():

    # Cuando el endpoint esta registrado como webhook, debe responder el echo de vuelta
    # El valor del 'hub.challenge' se recibe en los argumentos de la consulta
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VTK:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return render_template("index.html"), 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    # log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                # the facebook ID of the person sending you the message
                sender_id = messaging_event["sender"]["id"]
                # the recipient's ID, which should be your page's facebook ID
                recipient_id = messaging_event["recipient"]["id"]
                if messaging_event.get("message"):  # someone sent us a message
                    if "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]
                        response = nlp_fallback(message_text, sender_id)
                        send_message(sender_id, str(response), PAT)
                    if "attachments" in messaging_event["message"]:  # contains an image, location or other
                        attachment = messaging_event["message"]["attachments"][0]
                        if attachment['type'] == 'image':
                            message_image = attachment["payload"]["url"]
                            send_location_message(sender_id, "Please let me know where can we pick the bike up", PAT)
    return "ok", 200


# def send_message(recipient_id, message_text):
#     params = {
#         "access_token": PAT
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "text": message_text
#         }
#     })
#     r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
#     if r.status_code != 200:
#         print(r.status_code)
#         print(r.text)

if __name__ == '__main__':
    app.run(debug = True, port=5500)