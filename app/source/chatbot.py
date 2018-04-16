"""
Author: Paul Richter, 2018.

Handles all chatbot related stuff, including initial training data.
"""

from chatterbot import ChatBot
from db import connection

chatbot = ChatBot(
    'Glory Wallters',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    database_uri="postgresql+psycopg2://camelot:camelot@db:5432/camelot"
)

MAX_MESSAGE_SIZE = 400


conversation_id = connection.execute_sql('select id from conversation order by id DESC limit 1;').fetchone()


def get_response(message):
    """Get a response from the chat bot. Returns a default string if the bot returned nothing."""

    if len(message) > MAX_MESSAGE_SIZE:
        message = "I sent you a really long message."

    response = chatbot.get_response(message, conversation_id)
    if not response or len(str(response)) == 0:
        response = "I don't know what you want from me"
    return response

# chatbot.train("chatterbot.corpus.english.greetings")
# chatbot.train("chatterbot.corpus.english.conversations")

# Check if we need to train the bot. This should only ever happen on the first run with a fresh database.
cursor = connection.execute_sql('select count(*) from response;')
response_count = cursor.fetchone()
if response_count[0] == 0:
    print("Training chat bot, please stand by...")
    chatbot.train("chatterbot.corpus.english")
else:
    print("The chat bot appears to be already trained. Skipping training...")
