import secrets
import string
import time

# generate a random string of letters, digits, and symbols
alphabet = string.ascii_letters + string.digits
print(alphabet)
token = ''.join(secrets.choice(alphabet) for i in range(50))
print(token)

# append a unique identifier to the token
token += str(time.time())
print(token)

# hash the token for added security
hashed_token = hash(token)
print(hashed_token)
