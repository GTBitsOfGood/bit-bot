import re


def extract_user_id(text):
    pattern = r"<@(\w+)>"
    match = re.search(pattern, text)

    if match:
        user_id = match.group(1)
        return user_id
    else:
        return None
        
def is_positive_integer(number):
    try:
        number = int(number)
        return number > 0
    except ValueError:
        return False
