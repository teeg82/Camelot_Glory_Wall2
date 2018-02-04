import logging
from slacker import Slacker
import os
import re
import sys
import websocket
import json


SLACK_TOKEN = os.getenv('SLACK_TOKEN', '')
SLACK_USERNAME = os.getenv('SLACK_USERNAME', '')


if len(sys.argv) > 1 and sys.argv[1] is not None:
    logging.basicConfig(level=logging.DEBUG)


# Stores messages
message_buffer = {}
url = None
bot_userid = None
slack = None

def on_message(ws, message):
    print(message)
    message_json = json.loads(message)

    message_type = message_json.get('type')
    if message_type == 'message':
        text = message_json.get(u'text')
        bot_mention = "<@%s>" % bot_userid

        if bot_mention in text:
            print("The bot was mentioned!")
            user_id = message_json.get(u'target')

            if not user_exists(user_id):
                print("User does not exist in database, updating list...")
                users = slack.users.list().body
                update_user_list(users)

            user_profile = get_user_profile(user_id)
            print("Found user profile with id %s" % user_id)

            # strip off the bot mention and grab the summary text
            summary_text = re.search('%s(.+?)' % bot_mention, text).group(1)

            print("Attempting to parse text...")
            parse_summary(summary_text, user_profile)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### Closed ###")


def on_open(ws):
    print("### Opened ###")


# Checks the database to see whether we know of this user
def user_exists(user_id):
    # TODO: Replace this with a database lookup
    return False


# Give a list of users in JSON format, create or update user profiles in the database
def update_user_list(users):
    pass


# Given a user id, retrieve the user profile from the database with that id
def get_user_profile(user_id):
    pass


def parse_summary(summary_text, user_profile):
    pass


slack = Slacker(SLACK_TOKEN)
response = slack.rtm.connect()
connection_info = response.body
url = connection_info[u'url']
bot_userid = connection_info[u'self'][u'id']

websocket.enableTrace(True)
ws = websocket.WebSocketApp(url,
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close)
ws.on_open = on_open
ws.run_forever()

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

import pdb; pdb.set_trace()
