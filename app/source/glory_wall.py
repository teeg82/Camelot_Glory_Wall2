import logging
from slacker import Slacker
import os
import re
import sys
import websocket
import json
import datetime
from chatterbot import ChatBot

from db import (
    User,
    GloryWall,
    Category,
    close_connection,
    )

from parser import parse


SLACK_TOKEN = os.getenv('SLACK_TOKEN', '')
SLACK_USERNAME = os.getenv('SLACK_USERNAME', '')


if len(sys.argv) > 1 and sys.argv[1] is not None:
    logging.basicConfig(level=logging.DEBUG)


chatbot = ChatBot(
    'Glory Wallters',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri="postgresql+psycopg2://camelot:camelot@db:5432/camelot",
    database='camelot'
)


chatbot.train("chatterbot.corpus.english.greetings")
# chatbot.train("chatterbot.corpus.english.conversations")
# chatbot.train("chatterbot.corpus.english")


# Stores messages
message_buffer = {}
url = None
bot_userid = None
slack = None

bot_mention = None
summary_text_re = None


def on_message(ws, message):
    print(message)
    message_json = json.loads(message)

    message_type = message_json.get('type')
    if message_type == 'message':
        text = message_json.get(u'text')

        if text and bot_mention in text:
            print("The bot was mentioned!")
            user_id = message_json.get(u'user')

            # For now, we're going to update everybody every time the bot receives a message
            users = slack.users.list().body
            update_user_list(users)

            user_profile = get_user_profile(user_id)
            print("Found user profile with id %s" % user_id)

            # strip off the bot mention and grab the summary text
            summary_text = summary_text_re.search(text).group()

            print("Attempting to parse text...")
            success = parse_summary(summary_text, user_profile)
            if not success:
                response = chatbot.get_response(summary_text)
                if not response or len(str(response)) == 0:
                    response = "I don't know what you want from me"
                slack.chat.post_message('#glory-wall', response)


def on_error(ws, error):
    print(error)


def on_close(ws=None):
    print("### Closed ###")
    close_connection()


def on_open(ws):
    print("### Opened ###")


# Checks the database to see whether we know of this user
def user_exists(user_id):
    # TODO: Replace this with a database lookup
    return False


# Give a list of users in JSON format, create or update user profiles in the database
def update_user_list(users):
    for user_data in users['members']:
        user = User.get_or_none(slack_id=user_data.get('id'))
        if user is None:
            user = User.create(name=user_data.get('name'),
                               slack_id=user_data.get('id'),
                               is_bot=user_data.get('is_bot'),
                               is_deleted=user_data.get('deleted'))
        else:
            user.name = user_data.get('name')
            user.is_bot = user_data.get('is_bot')
            user.is_deleted = user_data.get('deleted')
            user.save()


# Given a user id, retrieve the user profile from the database with that id
def get_user_profile(user_id):
    return User.get_or_none(User.slack_id == user_id)


def parse_summary(summary_text, user_profile):
    results = parse(summary_text)
    if results:
        glory_walls = save_glory_walls(results, user_profile)
        send_response(glory_walls, user_profile)
        json_results = json.dumps(results)
        # slack.chat.post_message('#glory-wall', "Thanks @%s! I was able to parse this from your message: %s" % (user_profile.name, json_results), link_names=True)
        return True
    return False


# Take the parsed results and compare them to existing glory walls.
# Create or update glory walls as necessary.
def save_glory_walls(results, user_profile):
    top_score = [] # when the user's score has beaten the top score
    own_score = [] # when the user's score has beaten their own score
    new_score = [] # when the user does not have an entry for the given category
    for result in results:
        category = Category.select().where(Category.name == result['category_name']).get()
        # Get the existing glory wall entry for the current user and category
        user_glory_wall = GloryWall.get_or_none(GloryWall.category == category.id,
                                                GloryWall.user == user_profile.id)

        new_entry = False
        # Create a glory wall entry if the user does not yet have one
        if user_glory_wall is None:
            new_entry = True
            user_glory_wall = GloryWall.create(category=category.id,
                                               user=user_profile.id,
                                               full_summary_text=result['summary_text'],
                                               value=result['value'],
                                               timestamp=datetime.datetime.now())

        try:
            # Grab the top score
            high_score = GloryWall.select().where(GloryWall.category == category.id) \
                                           .order_by(GloryWall.value.desc()) \
                                           .limit(1).get()
        except GloryWall.DoesNotExist:
            high_score = None

        # A player only qualifies for top score if they beat the existing top score that was not their own,
        # or there was no existing top score in that category.
        if high_score and high_score.user != user_profile and \
           ((category.compare_greater and result['value'] > high_score.value) or \
           (not category.compare_greater and result['value'] < high_score.value)):
                print("Existing high score exceeded")
                update_glory_wall(user_glory_wall, result)
                top_score.append({'old_score': high_score, 'current_high_score': user_glory_wall})
        elif high_score == None:
            print("High score did not exist.")
            # If there was no high score for this entry, it means nobody had ever entered anything.
            # In which case, this user gets the top score by default.
            update_glory_wall(user_glory_wall, result)
            top_score.append({'old_score': None, 'current_high_score': user_glory_wall})
        elif (category.compare_greater and result['value']) > user_glory_wall.value or \
           (not category.compare_greater and result['value'] < user_glory_wall.value):
            print("User's own score exceeded")
            # Check if the user's new score exceeds their old score
            # Logic note: Whether the category is meant to be compared greater than or less than,
            # the result is still the same.
            update_glory_wall(user_glory_wall, result)
            own_score.append(user_glory_wall)
        elif new_entry:
            print("New entry")
            # If they did not beat the top score, but they did not have an entry for this category yet...
            new_score.append(user_glory_wall)

    return {'top_score': top_score, 'own_score': own_score, 'new_score': new_score}


def update_glory_wall(glory_wall, result):
    glory_wall.value = result['value']
    glory_wall.full_summary_text = result['summary_text']
    glory_wall.timestamp = datetime.datetime.now()
    glory_wall.save()


def send_response(glory_walls, user_profile):
    response = ["Thanks @%s!" % user_profile.name]

    top_score = glory_walls["top_score"]
    if len(top_score) > 0:
        response.append("You have achieved the top score in the following categories:\n")
        for score in top_score:
            current_high_score = score['current_high_score']
            response.append(" - %s, with a score of %d" % (current_high_score.category.display_name, current_high_score.value))
            old_score = score.get('old_score', None)
            if old_score:
                response.append("beating the previous score held by @%s" % old_score.user.name)
        response.append("\n\n")

    own_score = glory_walls["own_score"]
    if len(own_score) > 0:
        response.append("You have beaten your own score in the following categories:\n")
        for score in own_score:
            response.append(" - %s, with a score of %d\n" % (score.category.display_name, score.value))
        response.append("\n\n")

    new_score = glory_walls["new_score"]
    if len(new_score) > 0:
        response.append("I've added the following scores to the glory wall for you:\n")
        for score in new_score:
            response.append(" - %s, with a score of %d\n" % (score.category.display_name, score.value))

    if len(response) == 1:
        response.append("Unfortunately, this post did not exceed either your own existing scores, nor any of the top scores.")

    slack.chat.post_message('#glory-wall', " ".join(response), link_names=True)


slack = Slacker(SLACK_TOKEN)
response = slack.rtm.connect()
connection_info = response.body
url = connection_info[u'url']
bot_userid = connection_info[u'self'][u'id']

bot_mention = "<@%s>" % bot_userid
summary_text_re = re.compile('(?<=%s\s)(.+)((?:\n.+)*)' % bot_mention, re.MULTILINE)


websocket.enableTrace(True)
ws = websocket.WebSocketApp(url,
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close)
ws.on_open = on_open
ws.run_forever()

on_close()
# channels = slack.channels.list().body
# {u'channels':
#     [
#         {u'topic': {u'last_set': 0,
#                     u'value': u'',
#                     u'creator': u''
#                    },
#          u'is_general': False,
#          u'name_normalized': u'aid_requests',
#          u'name': u'aid_requests',
#          u'is_channel': True,
#          u'created': 1509249790,
#          u'is_member': False,
#          u'is_mpim': False,
#          u'is_archived': False,
#          u'creator': u'U1XUBVAVD',
#          u'is_org_shared': False,
#          u'previous_names': [],
#          u'num_members': 22,
#          u'purpose': {u'last_set': 1509249791,
#                       u'value': u'Post here for immediate aid needs. If you are unable to get a response, please use munk to send the aid request.',
#                       u'creator': u'U1XUBVAVD'
#                      },
#          u'members': [u'U1XU5RFUY', u'U1XUBVAVD', u'U1Y07P6JW', u'U1YAGLQ06', u'U2HS8DN65', u'U2MCGGGJG', u'U4CQ6AKBP', u'U5H1JGLSH', u'U5N6V9UCS', u'U6J5GB2E4', u'U6SDATNBF', u'U789G3L2X', u'U7BKZV5PU', u'U7EPN8NE8', u'U7PKN3YRK', u'U7VL7GAH2', u'U7VR9GV2B', u'U7W5MM09K', u'U82LSJ9SR', u'U83BC1P54', u'U8MTDK4KB', u'U8P0P1Y1Z', u'U8VF7868H', u'U8XJCG31A'],
#          u'unlinked': 0,
#          u'id': u'C7RH7FPT4',
#          u'is_private': False,
#          u'is_shared': False
#         }
#          ...
#     ]
# }
# users = slack.users.list().body
# {u'members': [
#     {
#       u'profile': {
#         u'first_name': u'keshang',
#         u'status_text': u'',
#         u'display_name': u'arjay',
#         u'status_emoji': u'',
#         u'title': u'',
#         u'team': u'T1XU43X5E',
#         u'image_512': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2F7fa9%2Fimg%2Favatars%2Fava_0004-512.png',
#         u'real_name': u'keshang mccarthy',
#         u'image_24': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2F0180%2Fimg%2Favatars%2Fava_0004-24.png',
#         u'phone': u'',
#         u'real_name_normalized': u'keshang mccarthy',
#         u'last_name': u'mccarthy',
#         u'image_72': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0004-72.png',
#         u'image_32': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0004-32.png',
#         u'image_48': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0004-48.png',
#         u'skype': u'',
#         u'avatar_hash': u'gb58e3a75a9e',
#         u'display_name_normalized': u'arjay',
#         u'email': u'keshang.mccarthy@gmail.com',
#         u'image_192': u'https://secure.gravatar.com/avatar/b58e3a75a9e5ab1fe20290640091d296.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2F7fa9%2Fimg%2Favatars%2Fava_0004-192.png'
#       },
#       u'updated': 1515774911,
#       u'name': u'arjay',
#       u'deleted': True,
#       u'is_app_user': False,
#       u'is_bot': False,
#       u'team_id': u'T1XU43X5E',
#       u'id': u'U1Y25954G'
#     },
#     ...
#     }

# import pdb; pdb.set_trace()
