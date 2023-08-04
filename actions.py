import os
from database import give_bits_to_user, remove_bits_from_user, get_leaderboard_documents
from helper import extract_user_id, is_positive_integer
from dotenv import load_dotenv

load_dotenv()
def give_bit(client, arguments, user_id, channel_id):
    if len(arguments) - 1 < 3:
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: Command expects at least three arguments, {len(arguments) - 1} were given"
        )
        raise Exception(f"Command expects at least three arguments, {len(arguments) - 1} were given");
    
    users = set(arguments[2:-1])
    amount = int(arguments[-1])

    if not is_positive_integer(amount):
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: {amount} is not a valid amount; {amount} must be an integer amount > 0"
        )
        raise Exception(f"{amount} is not a valid amount; {amount} must be an integer amount > 0")

    for rewarded_user in users:
        rewarded_user = extract_user_id(rewarded_user)

        if not client.users_info(user=rewarded_user)['ok']:
            client.chat_postMessage(
                channel=os.environ["BOT_LOGS_CHANNEL"],
                text=f"<@{user_id}>: Mentioned user, {rewarded_user}, does not exist."
            )
            raise Exception(f"Mentioned user, {rewarded_user}, does not exist.");

        give_bits_to_user(rewarded_user, amount)
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}> gave {amount} bits from {rewarded_user}"
        )



def remove_bit(client, arguments, user_id, channel_id):
    if len(arguments) - 1 < 3:
        raise Exception(f"Command expects at least three arguments, {len(arguments) - 1} were given");
    
    users = set(arguments[2:-1])
    amount = int(arguments[-1])

    if not is_positive_integer(amount):
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}>: {amount} is not a valid amount; {amount} must be an integer amount > 0"
        )
        raise Exception(f"{amount} is not a valid amount; {amount} must be an integer amount > 0")

    for punished_user in users:
        punished_user = extract_user_id(punished_user)
        if not client.users_info(user=punished_user)['ok']:
            client.chat_postMessage(
                channel=os.environ["BOT_LOGS_CHANNEL"],
                text=f"<@{user_id}>: Mentioned user, {punished_user}, does not exist."
            )
            raise Exception(f"Mentioned user, {punished_user}, does not exist.");

        remove_bits_from_user(punished_user, amount)
        client.chat_postMessage(
            channel=os.environ["BOT_LOGS_CHANNEL"],
            text=f"<@{user_id}> removed {amount} bits from {punished_user}"
        )


def get_leaderboard(client, arguments, user_id, channel_id):
    users = get_leaderboard_documents()
    user_bit_info = []
    for user in users:
        user_bit_info.append((
            client.users_info(user=user['userId'])['user'].get('real_name', 'Unknown User'), 
            user['bits']))
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

    
    client.chat_postMessage(
        channel=channel_id,
        text=top_users_string)
    
    client.chat_postMessage(
        channel=os.environ["BOT_LOGS_CHANNEL"],
        text=f"<@{user_id}> just printed the leaderboard!"
    )