import slack
import os
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter
import json
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/bog/*": {"origins": "*"}})
load_dotenv()

import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from actions import *
from helper import extract_user_id

client = slack.WebClient(token=os.environ["SLACK_BOT_TOKEN"])

slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)

valid_channels = [
    os.environ["BOT_LOGS_CHANNEL"],
    os.environ["GT_BITS_CHANNEL"],
    os.environ["MAPSCOUT_NOTIFICATIONS_CHANNEL"],
]

Action = {
    "GIVE": "give",
    "REMOVE": "remove",
    "LEADERBOARD": "leaderboard",
    "SET_TEAM": "set-team",
    "TEAM_LEADERBOARD": "team-leaderboard",
    "HELP": "help",
    "PROMOTE": "promote",
    "DEMOTE": "demote",
}
ActionNameToAction = {
    Action.get("GIVE"): give_bit,
    Action.get("REMOVE"): remove_bit,
    Action.get("LEADERBOARD"): get_leaderboard,
    Action.get("SET_TEAM"): set_team,
    Action.get("TEAM_LEADERBOARD"): print_team_leaderboard,
    Action.get("HELP"): get_help,
    Action.get("PROMOTE"): promote_user,
    Action.get("DEMOTE"): demote_user,
}

BOT_ID = client.api_call("auth.test")["user_id"]


@app.route("/health")
def health():
    return {"health": os.environ["ENV_TEST"]}


@app.route("/slack/events", methods=["POST"])
def handle_challenge():
    return {"challenge": request.json()["challenge"]}


@app.route("/slack/events/interactivity", methods=["POST"])
def handle_interactivity():
    try:
        message = json.loads(request.form.get("payload"))
        action = message.get("actions")[0].get("action_id")
        user_id = message.get("user").get("id")
        channel_id = message.get("channel").get("id")

        if action == "select_team_action":
            selected_option = (
                message.get("actions")[0].get("selected_option").get("value")
            )
            set_team_action_handler(client, selected_option, user_id, channel_id)
        return {}
    except Exception as e:
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: an exception occurred - {e}",
        )


@app.route("/bog/analytics-log", methods=["POST"])
def handle_analytics_logs():
    message = request.json["message"]
    client.chat_postMessage(
        channel=os.environ["ANALYTICS_LOGS_CHANNEL"], text=f"{message}"
    )
    return {"success": True, "message": message}


@app.route("/bog/mapscout", methods=["POST"])
def handle_mapscount_event():
    email = request.json["email"]
    client.chat_postMessage(
        channel=os.environ["MAPSCOUT_NOTIFICATIONS_CHANNEL"],
        text=f"Mapscout Waitlist Notificaction: `{email}`",
    )
    return {"success": True, "email": email}


@slack_event_adapter.on("app_mention")
def app_mention(payload):
    try:
        event = payload.get("event", {})
        channel_id = event.get("channel")
        timestamp = event.get("ts")
        user_id = event.get("user")

        if channel_id not in valid_channels:
            return

        text = event.get("text")
        arguments = text.split(" ")
        bot_id = extract_user_id(arguments[0])
        if bot_id != BOT_ID:
            return

        action = arguments[1]
        if action not in Action.values():
            raise Exception(f"{action} is not a valid action")

        ActionNameToAction[action](client, arguments, user_id, channel_id)

        client.reactions_add(
            channel=channel_id, timestamp=timestamp, name="white_check_mark"
        )
    except Exception as e:
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: an exception occurred - {e}",
        )
        client.reactions_add(channel=channel_id, timestamp=timestamp, name="x")


@slack_event_adapter.on("message")
def message_im(payload):
    try:
        event = payload.get("event", {})
        if event.get("channel_type") != "im":
            return

        timestamp = event.get("ts")
        user_id = event.get("user")
        channel_id = event.get("channel")

        text = event.get("text")
        arguments = text.split(" ")
        bot_id = extract_user_id(arguments[0])

        if user_id == BOT_ID:
            return

        if bot_id != BOT_ID:
            return

        action = arguments[1]
        if action not in Action.values():
            raise Exception(f"{action} is not a valid action")

        ActionNameToAction[action](client, arguments, user_id, channel_id)

        client.reactions_add(
            channel=channel_id, timestamp=timestamp, name="white_check_mark"
        )
    except Exception as e:
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: an exception occurred - {e}",
        )
        client.reactions_add(channel=channel_id, timestamp=timestamp, name="x")


if __name__ == "__main__":
    app.run(debug=True)
