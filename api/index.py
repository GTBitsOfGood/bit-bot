import slack
import os
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
load_dotenv()

import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from actions import give_bit, remove_bit, get_leaderboard
from helper import extract_user_id

client = slack.WebClient(
    token=os.environ["SLACK_BOT_TOKEN"]
)

slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"],
    '/slack/events',
    app
)

valid_channels = [
    os.environ['BOT_TESTING_CHANNEL'],
]
    
Action = {
    "GIVE": "give",
    "REMOVE":  "remove",
    "LEADERBOARD":  "leaderboard"
}
ActionNameToAction = {
    Action.get("GIVE"): give_bit,
    Action.get("REMOVE"): remove_bit,
    Action.get("LEADERBOARD"): get_leaderboard,
}

BOT_ID = client.api_call("auth.test")["user_id"]

@app.route('/health')
def health():
    return {"health": os.environ["ENV_TEST"]}

@app.route('/slack/events', methods=['POST'])
def handle_challenge():
    return {"challenge": request.json()['challenge']}


@slack_event_adapter.on('app_mention')
def app_mention(payload):
    try:
        event = payload.get('event', {})
        channel_id = event.get('channel')
        timestamp = event.get('ts')
        user_id = event.get('user_id')
        if channel_id not in valid_channels:
            return

        text = event.get('text')
        arguments = text.split(' ')
        bot_id = extract_user_id(arguments[0])
        if bot_id != BOT_ID:
            return;

        action = arguments[1]
        if action not in Action.values():
            raise Exception(f"{action} is not a valid action")
        
        ActionNameToAction[action](client, arguments)

        client.reactions_add(
            channel=channel_id,
            timestamp=timestamp,
            name="white_check_mark"
        )  
    except Exception as e:
        print(e)
        client.reactions_add(
                channel=channel_id,
                timestamp=timestamp,
                name="x"
            )        

if __name__ == "__main__":
    app.run(debug=True)