import os
from database import *
from helper import extract_user_id, is_positive_integer
from config import questions
from dotenv import load_dotenv
from config import teams

load_dotenv()


def get_bits(client, arguments, user_id, channel_id):
    if len(arguments) > 2:
        tag = " ".join(arguments[2:])
        bits = get_bits_by_user_id_from_history(user_id, tag)
    else:
        bits = get_bits_by_user_id(user_id)

    client.chat_postMessage(
        channel=channel_id,
        text=f"You have {bits} bits",
    )
    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> printed their bit count",
    )


def give_bit(client, arguments, user_id, channel_id):
    if len(arguments) - 1 < 3:
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: Command expects at least three arguments, {len(arguments) - 1} were given",
        )
        raise Exception(
            f"Command expects at least three arguments, {len(arguments) - 1} were given"
        )

    if not user_is_admin(user_id):
        raise Exception("Only admins can grant bits to others!")

    users = set(arguments[2:-1])
    amount = int(arguments[-1])

    if not is_positive_integer(amount):
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: {amount} is not a valid amount; {amount} must be an integer amount > 0",
        )
        raise Exception(
            f"{amount} is not a valid amount; {amount} must be an integer amount > 0"
        )

    for rewarded_user in users:
        rewarded_user = extract_user_id(rewarded_user)

        if not client.users_info(user=rewarded_user)["ok"]:
            client.chat_postMessage(
                channel=os.environ["BOT_LOGS_CHANNEL"],
                text=f"<@{user_id}>: Mentioned user, {rewarded_user}, does not exist.",
            )
            raise Exception(f"Mentioned user, {rewarded_user}, does not exist.")

        give_bits_to_user(rewarded_user, amount)
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}> gave {amount} bits to <@{rewarded_user}>",
        )


def remove_bit(client, arguments, user_id, channel_id):
    if len(arguments) - 1 < 3:
        raise Exception(
            f"Command expects at least three arguments, {len(arguments) - 1} were given"
        )

    if not user_is_admin(user_id):
        raise Exception("Only admins can remove bits from others!")

    users = set(arguments[2:-1])
    amount = int(arguments[-1])

    if not is_positive_integer(amount):
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: {amount} is not a valid amount; {amount} must be an integer amount > 0",
        )
        raise Exception(
            f"{amount} is not a valid amount; {amount} must be an integer amount > 0"
        )

    for punished_user in users:
        punished_user = extract_user_id(punished_user)
        if not client.users_info(user=punished_user)["ok"]:
            client.chat_postMessage(
                channel=os.environ["BOT_LOGS_CHANNEL"],
                text=f"<@{user_id}>: Mentioned user, {punished_user}, does not exist.",
            )
            raise Exception(f"Mentioned user, {punished_user}, does not exist.")

        remove_bits_from_user(punished_user, amount)
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}> removed {amount} bits from <@{punished_user}>",
        )


def get_leaderboard(client, arguments, user_id, channel_id):
    if len(arguments) > 2:
        tag = " ".join(arguments[2:])
        users = get_leaderboard_documents_from_history(tag)
    else:
        users = get_leaderboard_documents()

    user_bit_info = []
    for user in users:
        user_bit_info.append(
            (
                client.users_info(user=user["userId"])["user"].get(
                    "real_name", "Unknown User"
                ),
                user["bits"],
            )
        )
    top_users_string = "🎉 Current Bit Leaders 🎉\n\n"

    for index, info in enumerate(user_bit_info):
        medal = ""
        if index == 0:
            medal = "🥇"

        if index == 1:
            medal = "🥈"

        if index == 2:
            medal = "🥉"

        if 3 <= index <= 4:
            medal = "🎖️"

        if info[1] == 1:
            top_users_string += f"\t{medal}{info[0]} - {info[1]} Bit\n"
        else:
            top_users_string += f"\t{medal}{info[0]} - {info[1]} Bits\n"

    client.chat_postMessage(channel=channel_id, text=top_users_string)

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> just printed the leaderboard!",
    )


def set_team_action_handler(client, team_value, user_id, channel_id):
    set_team_by_user_id(user_id, team_value)
    client.chat_postMessage(
        channel=channel_id, text=f"You set your team to {team_value}!"
    )
    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> set their team to {team_value}!",
    )


def print_team_leaderboard(client, arguments, user_id, channel_id):
    if len(arguments) > 2:
        tag = " ".join(arguments[2:])
        team_leaderboard = get_team_leaderboard_from_history(tag)
    else:
        team_leaderboard = get_team_leaderboard()

    team_leaderboard = sorted(
        team_leaderboard, key=lambda obj: obj["total_bits"], reverse=True
    )

    top_teams_string = "🎉 Current Team Bit Leaders 🎉\n\n"
    for index, info in enumerate(team_leaderboard):
        medal = ""
        if index == 0:
            medal = "🥇"

        if index == 1:
            medal = "🥈"

        if index == 2:
            medal = "🥉"

        if 3 <= index <= 4:
            medal = "🎖️"

        if info.get("total_bits") == 1:
            top_teams_string += (
                f"\t{medal}{info.get('_id')} - {info.get('total_bits')} Bit\n"
            )
        else:
            top_teams_string += (
                f"\t{medal}{info.get('_id')} - {info.get('total_bits')} Bits\n"
            )

    client.chat_postMessage(channel=channel_id, text=top_teams_string)

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> just printed the team leaderboard!",
    )


def get_help(client, arguments, user_id, channel_id):
    BOT_ID = client.api_call("auth.test")["user_id"]
    client.chat_postMessage(
        channel=channel_id,
        text=f"""
    Hello! This is the bits of good bit bot! Example commands:
    
    *View how many bits you have:*
    - <@{BOT_ID}> get-bits

    *View how many bits you have in a previous semester:*
    - <@{BOT_ID}> get-bits
    - I.e., <@{BOT_ID}> get-bits Spring 2024

    *Set your team:*
    - <@{BOT_ID}> set-team

    *View the bit leaderboard:*
    - <@{BOT_ID}> leaderboard

    *View the bit leaderboard in a previous semester:*
    - <@{BOT_ID}> leaderboard <semester tag>
    - I.e., <@{BOT_ID}> leaderboard Spring 2024

    *View the team bit leaderboard:*
    - <@{BOT_ID}> team-leaderboard

    *View the team bit leaderboard in a previous semester:*
    - <@{BOT_ID}> team-leaderboard <semester tag>
    - I.e., <@{BOT_ID}> team-leaderboard Spring 2024

    
    ⛔ Admin Only Commands ⛔

    *Give 10 bits to a user:*
    - <@{BOT_ID}> give <tag the user> 10 

    *Remove 10 bits from a user:*
    - <@{BOT_ID}> remove <tag the user> 10 

    *Give 10 Bits to multiple users:*
    - <@{BOT_ID}> give <tag user 1> <tag user 2> 10 

    *Remove 10 bits from multiple users:*
    - <@{BOT_ID}> remove <tag user 1> <tag user 2> 10 

    *Promote a user to admin:*
    - <@{BOT_ID}> promote <tag the user> 
    
    *Demote a user:*
    - <@{BOT_ID}> demote <tag the user> 

    *Clear Teams:*
    - <@{BOT_ID}> clear-teams 

    *Clear Bits:*
    - <@{BOT_ID}> clear-bits 

    *Save Bit History:*
    - <@{BOT_ID}> save-bit-history <semester tag> 
    - I.e., <@{BOT_ID}> save-bit-history Spring 2024

    *Delete Bit History:*
    - <@{BOT_ID}> delete-bit-history <semester tag> 
    - I.e., <@{BOT_ID}> delete-bit-history Spring 2024

    """,
    )


def set_team(client, arguments, user_id, channel_id):
    team_blocks = []
    for team in teams:
        team_blocks.append(
            {"text": {"type": "plain_text", "text": team}, "value": team}
        )

    blocks = [
        {
            "type": "actions",
            "block_id": "action1",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": questions.get("TEAM"),
                    },
                    "action_id": "select_team_action",
                    "options": team_blocks,
                }
            ],
        }
    ]
    client.chat_postMessage(channel=channel_id, blocks=blocks)


def promote_user(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can promote users")

    user = extract_user_id(arguments[2])
    change_user_role(user, "admin")

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> promoted <@{user}> to admin!",
    )


def demote_user(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can demote users")

    user = extract_user_id(arguments[2])
    change_user_role(user, "user")

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> demoted <@{user}> to user!",
    )


def clear_bits(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can demote users")

    set_user_bits_to_zero()
    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"], text=f"<@{user_id}> cleared bits!"
    )


def clear_teams(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can clear teams")

    set_teams_to_no_team()

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"], text=f"<@{user_id}> cleared all teams!"
    )


def save_bit_history(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can save bit history")

    tag = " ".join(arguments[2:])

    record_bit_history(tag)

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> saved bit history for {tag}!",
    )


def delete_bit_history(client, arguments, user_id, channel_id):
    if not user_is_admin(user_id):
        raise Exception("Only admins can delete bit history")

    tag = " ".join(arguments[2:])

    remove_bit_history_by_tag(tag)

    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> deleted bit history for {tag}!",
    )
