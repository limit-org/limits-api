# this file hashes whatever the user puts into it.
# THIS IS NOT SECURE. TESTING ONLY.

import bcrypt

while True:
    # Generate a salt for the password
    salt = bcrypt.gensalt()

    # Hash the password using the salt
    password = input()
    hashed_text = bcrypt.hashpw(
        str(password).encode('utf-8'), salt
    )
    salt = ""

    # Verify the password
    if bcrypt.checkpw(input().encode('utf-8'), hashed_text):
        print('Password is correct')
    else:
        print('Password is incorrect')
