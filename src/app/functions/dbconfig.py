from configparser import ConfigParser
from loguru import logger


@logger.catch
def config(filename='../../database.ini', section='db'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
            db = db['database_url'].replace("\"", "")  # remove ' " ' and make it work
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
