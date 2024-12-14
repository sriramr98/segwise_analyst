import os
from configparser import ConfigParser

class PostgresConfig:
    def __init__(self, host: str, db: str, password: str, user: str) -> None:
        self.__host = host
        self.__db = db
        self.__password = password
        self.__user = user

    def getConnectionString(self) -> str:
        return f"host={self.__host} db_name={self.__db} user={self.__user} password={self.__password}"

def parseFromEnv():
    host = os.getenv('POSTGRES_HOST') or ''
    db = os.getenv('DB_NAME') or ''
    db_password = os.getenv('POSTGRES_PASSWORD') or ''
    user = os.getenv('DB_USER') or ''

    return PostgresConfig(host, db, db_password, user)

def parseFromFile(filePath = 'database.ini', section = 'postgresql'):
    parser = ConfigParser()
    parser.read(filePath)
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filePath))
    return PostgresConfig(config['host'], config['database'], config['password'], config['user'])

def getConfig():
    if os.getenv('PG_CONFIG_PATH'):
        return parseFromFile(os.getenv('PG_CONFIG_PATH') or '')
    else:
        return parseFromEnv()
