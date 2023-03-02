# This file checks if a given string meets the standards of our password system.

def CheckPassword(plainTextPass, username):
    if len(plainTextPass) >= 257:  # check if too long
        return {"err": "Password too long.", "ui": "Your password is too long (over 256 characters)."},

    if len(plainTextPass) <= 7:  # equal to or less than 7 characters # check if too short
        return {"err": "Password not long enough.", "ui": "Your password needs to be longer (8 characters or more)."},

    # check if it contains one symbol (it should contain)
    symbols = False
    for char in plainTextPass:
        while not symbols:
            if char in "!@#$%^&*()'/\"":
                symbols = True
    if not symbols:  # if no symbols, do nothing if there are symbols.
        return {"err": "No symbols.",
                "ui": "There are no symbols(!@#$%^&*()'/\") in your password. At least 1 is required."}

    # check if it contains one digit (it should contain)
    digits = False
    for char in plainTextPass:
        while not digits:
            if char in "0123456789":
                digits = True
    if not digits:  # if no digits, do nothing if there are digits.
        return {"err": "No digits.", "ui": "There are no numbers in your password. At least 1 is required."}

    # Check if the password contains the username
    if username in plainTextPass:
        return {"err": "Username in password.", "ui": "Your password cannot contain your username."}

    return 0  # return 0 if everything looks good!
