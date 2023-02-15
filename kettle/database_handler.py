import sqlite3

from pydantic import BaseSettings
from enum import Enum

from datetime import datetime

from log_handler import Logger

logger = Logger(__name__)


class DBConfig(BaseSettings):
    """Loads kettle configuration from TOML file."""
    database: str

    class Config:
        env_file = "pyproject.toml"
        env_file_encoding = "utf-8"


class QueryTemplates(Enum):
    """Stores SQL templates for the module."""
    create_table = "CREATE TABLE messages (ID INTEGER PRIMARY KEY "\
        "AUTOINCREMENT, timestamp TEXT, message TEXT);"
    add_entry = "INSERT INTO messages (timestamp, message) VALUES "\
        "('{timestamp}', '{message}');"


class LogTemplates(Enum):
    """Stores templates for the logger."""
    connection_established = "The connection to the database was "\
        "successfully established."
    connection_closed = "The connectuion to the database is closed."
    creating_table = "Trying to create the database table."
    adding_message = "Trying to add a message to the database table."
    success_execution = "The query was successfully executed."
    failed_execution = "The execution of query ended with an error: {}."


def execute_query(message: str = None):
    """Creates connection to the database and executes queries. If no
    message was provided, tries to creat a new table in the database."""
    CONNECTION = sqlite3.connect(DBConfig().database)
    logger.debug(LogTemplates.connection_established.value)
    if not message:
        # Using create_table template, if no message was provided
        # to create a new table in the database.
        logger.debug(LogTemplates.creating_table.value)
        query = QueryTemplates.create_table.value
    else:
        # Using template for adding message entry.
        logger.debug(LogTemplates.adding_message.value)
        timestamp = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
        query = QueryTemplates.add_entry.value.format(
            timestamp=timestamp, message=message)
    try:
        # Executes the query in the database.
        cursor = CONNECTION.cursor()
        cursor.execute(query)
        logger.debug(LogTemplates.success_execution.value)
    except Exception as error:
        # Logging if the error was occured, while executing the query.
        logger.error(LogTemplates.failed_execution.value.format(error))
    finally:
        CONNECTION.commit()
        CONNECTION.close()
        logger.debug(LogTemplates.connection_closed.value)
