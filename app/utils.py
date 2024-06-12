import json
from werkzeug.security import generate_password_hash, check_password_hash


def update_user_json(user_details, user_status):
    user_data = {}
    try:
        with open('user_data.json', 'r') as user_read_file:
            user_data = json.load(user_read_file)
    except Exception as exp:
        print(f"Exception : {exp}")

    if user_status == 'register':
        user_data[user_details['username']] = {
            'email': user_details['email'],
            'password_hash': generate_password_hash(user_details['password'])
        }
        with open('user_data.json', 'w') as user_write_file:
            json.dump(user_data, user_write_file)
    elif user_status == 'login':
        if user_details['username'] in list(user_data.keys()):
            if check_password_hash(user_data[user_details['username']]['password_hash'], user_details['password']):
                return "Valid"
            else:
                return "Entered Password is Wrong, Please Check"
        else:
            return "Username Not Found Please Register"
    return "Unknown Error"


def calculate_score(stats):
    """
    Calculate a score based on the stats and return a descriptive category.
    """
    right = stats['right']
    wrong = stats['wrong']
    hints = stats['hints']

    score = right * 10 - wrong * 5 - hints * 2

    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    elif score >= 20:
        return "Satisfactory"
    else:
        return "Need to Rework"
