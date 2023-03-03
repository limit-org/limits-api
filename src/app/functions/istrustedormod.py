import psycopg2
from .dbconfig import config


def checkTORM(username):
    conn = psycopg2.connect(config())

    with conn.cursor() as cur:
        cur.execute(
            "SELECT (trusted, moderator) FROM users WHERE username = %s",
            (username,)
        )
        TORMod = cur.fetchone()

        print(TORMod)
        if not TORMod[0] or TORMod[1]:  # if not trusted or a mod
            return 1

        else:
            if TORMod[0]:
                return "trusted"
            if TORMod[1]:
                return "moderator"
