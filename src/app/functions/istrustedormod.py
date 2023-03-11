import psycopg2
from .dbconfig import config


def checkTORM(username):
    conn = psycopg2.connect(config())

    with conn.cursor() as cur:
        cur.execute(
            "SELECT (trusted, moderator) FROM users WHERE username = %s",
            (username,)
        )
        TORMod = cur.fetchall()
        if "t" not in [TORMod[0][0][1], TORMod[0][0][3]]:  # if not trusted or a mod
            return 1

        else:
            if TORMod[0][0][1] == "t" and TORMod[0][0][3] == "t":
                return "mod+trusted"
            else:
                if "t" in TORMod[0][0][1]:
                    return "trusted"
                if "t" in TORMod[0][0][3]:
                    return "moderator"
