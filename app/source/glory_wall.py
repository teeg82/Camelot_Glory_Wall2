"""
Author: Paul Richter, 2018.

Main entrypoint module for parsing Utopia summaries from slack
"""

import traceback
import logging
from slacker import Slacker
import os
import re
import sys
import websocket
import json
import datetime

from db import (
    User,
    GloryWall,
    Category,
    close_connection,
)

import chatbot

from parser.parser import parse


from wikirenderer import render_to_wiki

SLACK_TOKEN = os.getenv('SLACK_TOKEN', '')
SLACK_USERNAME = os.getenv('SLACK_USERNAME', '')
APP_ENV = os.getenv('APP_ENV', 'DEBUG')


if APP_ENV == 'DEBUG':
    OUTPUT_CHANNEL = '#area51'
    UTOPIA_AGE = 'DEV'
else:
    OUTPUT_CHANNEL = '#glory-wall'
    UTOPIA_AGE = os.getenv('UTOPIA_AGE', '')

WIKI_URL = "https://camelot.miraheze.org/wiki/Glory_Wall_-_Age_%s" % UTOPIA_AGE


if len(sys.argv) > 1 and sys.argv[1] is not None:
    logging.basicConfig(level=logging.DEBUG)


class GloryWallConstants(object):
    """Hold slack connection details."""

    def __init__(self):
        """Set instance variables to None."""
        self.clear()

    def connect(self):
        """Connect to slack websockets."""
        self.slack = Slacker(SLACK_TOKEN)
        response = self.slack.rtm.connect()
        connection_info = response.body
        self.url = connection_info[u'url']
        self.bot_userid = connection_info[u'self'][u'id']

        self.bot_mention = "<@%s>" % self.bot_userid
        self.summary_text_re = re.compile(r'(?P<bot_mention>%s)' % self.bot_mention, re.MULTILINE)

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()

    def clear(self):
        """Reset fields to none."""
        self.slack = None
        # Stores messages
        self.message_buffer = {}
        self.url = None
        self.bot_userid = None
        self.slack = None

        self.bot_mention = None
        self.summary_text_re = None


constants = GloryWallConstants()


def on_message(ws, message):
    """Called when slack bot receives a message event from slack."""
    try:
        _handle_on_message(ws, message)
    except BaseException as e:
        logging.error('An exception occurred: %s' % e)
        logging.error(traceback.format_exc())
        constants.slack.chat.post_message(OUTPUT_CHANNEL,
                                          "Aww crap, something went horribly wrong with the bot. @the_round_table will check the logs and fix it.",
                                          link_names=True,
                                          as_user=True)


def _handle_on_message(ws, message):
    """Handle when a message is sent to the bot."""
    print(message)

    message_json = json.loads(message)

    message_type = message_json.get('type')
    if message_type == 'message':
        text = message_json.get(u'text')

        if text and constants.bot_mention in text:
            print("The bot was mentioned!")
            user_id = message_json.get(u'user')

            # For now, we're going to update everybody every time the bot
            # receives a message
            try:
                users = constants.slack.users.list().body
                update_user_list(users)
            except:
                print("WARN: Unable to connect to slack to obtain a user list")

            user_profile = get_user_profile(user_id)
            print("Found user profile with id %s" % user_id)

            # strip off the bot mention and grab the summary text
            summary_text = re.sub(constants.summary_text_re, '', text).strip()

            command_response = handle_command_response(summary_text)

            if not command_response:
                handle_summary_parsing(summary_text, user_profile)


def handle_summary_parsing(summary_text, user_profile):
    print("Attempting to parse text...")
    results = parse_summary(summary_text, user_profile)

    if results is not None and len(results) > 0:
        glory_walls = save_glory_walls(results, user_profile)
        render_to_wiki(Category.select(), UTOPIA_AGE)
        send_response(glory_walls, user_profile)
    else:
        response = chatbot.get_response(summary_text)
        constants.slack.chat.post_message(OUTPUT_CHANNEL, response, as_user=True)

def on_error(ws, error):
    """Called on error."""
    print(error)


def on_close(ws=None):
    """Called when the stream is closed."""
    print("### Closed ###")

    close_connection()


def on_open(ws):
    """Called when the stream is opened."""
    print("### Opened ###")


def handle_command_response(message):
    command_response = False
    message = message.lower()
    if message == "help":
        show_help()
        command_response = True
    elif message == "categories":
        show_categories()
        command_response = True
    elif 'scores' in message:
        show_scores(message.replace('scores', '').strip())
        command_response = True

    return command_response


def show_help():
    """Display bot usage information to the user in slack"""

    help_text = r"""
Glory Wall bot usage

*Send a glory wall entry to the bot:*

```
@glorywall Your forces arrive at foobarbaz...
```

*Bot commands:*

_Usage:_
  `@glorywall <command>`

_Available Commands:_
  - help
      This help message
  - categories
      Displays a list of all currently available categories
  - scores [category] [limit]
      Displays the list of scores for the given category
      Parameters:
        category - The underscored category name. The `categories` command lists the underscored name in parenthesis.
        limit - Optional; by default the `scores` command will list ALL scores. This parameter limits the list by the given number.
      Example:
        `@glorywall most_kills`
        `@glorywall most_acres 3`
    """

    constants.slack.chat.post_message(OUTPUT_CHANNEL, help_text, as_user=True)


def show_categories():
    category_text = ["Here are the list of categories the bot knows about:\n"]

    for category in Category.select():
        category_text.append(" - *%s* (_%s_)" % (category.display_name, category.name))

    constants.slack.chat.post_message(OUTPUT_CHANNEL, "\n".join(category_text), as_user=True)


def show_scores(message):
    message_parts = message.split()
    message_parts.reverse()

    if len(message_parts) == 0:
        constants.slack.chat.post_message(OUTPUT_CHANNEL, "I need to know what category of scores to look up. See `@glorywall help` for more details.\n Example: `@glorywall [category] [limit]`.", as_user=True)
        return

    category_name = message_parts.pop()

    limit = None
    if len(message_parts) > 0:
        limit = message_parts.pop()
        try:
            limit = int(limit)
        except ValueError:
            constants.slack.chat.post_message(OUTPUT_CHANNEL, "I don't know what limit _%s_ means" % limit, as_user=True)
            return

        if limit is not None and limit <= 0:
            constants.slack.chat.post_message(OUTPUT_CHANNEL, "Tell me honestly, does asking for a limit of zero or less make any sense to you?", as_user=True)
            return

    try:
        category = Category.select().where(Category.name == category_name).get()
    except Category.DoesNotExist:
        constants.slack.chat.post_message(OUTPUT_CHANNEL, "Sorry, I don't have any categories called '%s'" % category_name, as_user=True)
        return

    scores_query = GloryWall.select() \
                            .where(GloryWall.category == category, GloryWall.age == UTOPIA_AGE)
    if category.compare_greater:
        scores_query.order_by(GloryWall.value.desc())
    else:
        scores_query.order_by(GloryWall.value.asc())

    if limit:
        scores_query = scores_query.limit(limit)

    if scores_query.count() == 0:
        constants.slack.chat.post_message(OUTPUT_CHANNEL, "Sorry, I could not find any scores for category %s" % category_name, as_user=True)
        return

    output = ["*Here are the list of scores for _%s_*" % category_name]
    for score in scores_query:
        output.append('%s: %s' % (score.user.name, score.value))
    constants.slack.chat.post_message(OUTPUT_CHANNEL, "\n".join(output), as_user=True)


def update_user_list(users):
    """Give a list of users in JSON format, create or update user profiles in the database."""
    for user_data in users['members']:
        user = User.get_or_none(slack_id=user_data.get('id'))
        if user is None:
            user = User.create(name=user_data.get('name'),
                               display_name=user_data.get('profile').get('display_name'),
                               slack_id=user_data.get('id'),
                               is_bot=user_data.get('is_bot'),
                               is_deleted=user_data.get('deleted'))
        else:
            user.name = user_data.get('name')
            user.display_name = user_data.get('profile').get('display_name')
            user.is_bot = user_data.get('is_bot')
            user.is_deleted = user_data.get('deleted')
            user.save()


def get_user_profile(user_id):
    """Given a user id, retrieve the user profile from the database with that id."""
    return User.get_or_none(User.slack_id == user_id)


def parse_summary(summary_text, user_profile):
    """Parse the summary text and return any found glory-wallable parts."""
    return parse(summary_text)


def save_glory_walls(results, user_profile):
    """Take the parsed results and compare them to existing glory walls. Create or update glory walls as necessary."""
    top_score = []  # when the user's score has beaten the top score
    own_score = []  # when the user's score has beaten their own score
    new_score = []  # when the user does not have an entry for the given category

    for result in results:
        category = Category.select().where(Category.name == result['category_name']).get()
        # Get the existing glory wall entry for the current user and category
        user_glory_wall = GloryWall.get_or_none(GloryWall.category == category.id,
                                                GloryWall.user == user_profile.id,
                                                GloryWall.age==UTOPIA_AGE)

        new_entry = False
        # Create a glory wall entry if the user does not yet have one
        if user_glory_wall is None:
            new_entry = True
            user_glory_wall = GloryWall.create(category=category.id,
                                               user=user_profile.id,
                                               full_summary_text=result['summary_text'],
                                               value=result['value'],
                                               timestamp=datetime.datetime.now(),
                                               age=UTOPIA_AGE)

        try:
            if category.compare_greater:
                # Grab the top score
                high_score = GloryWall.select().where(GloryWall.category == category.id,
                                                      GloryWall.age == UTOPIA_AGE) \
                                               .order_by(GloryWall.value.desc()) \
                                               .limit(1).get()
            else:
                high_score = GloryWall.select() \
                                      .where(GloryWall.category == category.id,
                                             GloryWall.age == UTOPIA_AGE) \
                                      .order_by(GloryWall.value.asc()) \
                                      .limit(1).get()
        except GloryWall.DoesNotExist:
            high_score = None

        # A player only qualifies for top score if they beat the existing top score that was not their own,
        # or there was no existing top score in that category.
        if high_score and high_score.user != user_profile and \
           ((category.compare_greater and result['value'] > high_score.value) or
               (not category.compare_greater and result['value'] < high_score.value)):
                print("Existing high score exceeded")
                update_glory_wall(user_glory_wall, result)
                top_score.append({'old_score': high_score, 'current_high_score': user_glory_wall})
        elif high_score.user == user_profile and new_entry:
            print("New entry achieved top score")
            old_top_score = GloryWall.select() \
                                     .where(GloryWall.category == category.id,
                                            GloryWall.age == UTOPIA_AGE,
                                            GloryWall.user != user_profile) \
                                     .order_by(GloryWall.value.asc()) \
                                     .limit(1)
            old_top_score = old_top_score.get() if len(old_top_score) == 1 else None
            top_score.append({'old_score': old_top_score, 'current_high_score': user_glory_wall})
        elif high_score is None:
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
    """Update an existing glorywall entry with the new value, summary text and timestamp."""
    glory_wall.value = result['value']
    glory_wall.full_summary_text = result['summary_text']
    glory_wall.timestamp = datetime.datetime.now()
    glory_wall.save()


def send_response(glory_walls, user_profile):
    """Compile and send a response to the original sender in slack with a summary of the result of their submission."""
    response = ["Thanks @%s!" % user_profile.name]

    top_score = glory_walls["top_score"]
    if len(top_score) > 0:
        response.append("You have achieved the top score in the following categories:\n")
        for score in top_score:
            current_high_score = score['current_high_score']
            response.append(" - %s, with a score of %d" % (current_high_score.category.display_name, current_high_score.value))
            old_score = score.get('old_score', None)
            if old_score:
                if old_score.user == user_profile:
                    response.append("beating your previous score of %s\n" % str(old_score.value))
                else:
                    response.append("beating the previous score of %s held by @%s\n" % (str(old_score.value), old_score.user.name))
            else:
                response.append('\n')
        response.append("\n\n")

    own_score = glory_walls["own_score"]
    if len(own_score) > 0:
        response.append("You have beaten your own score in the following categories:\n")
        for score in own_score:
            response.append(" - %s, with a score of %d\n" % (score.category.display_name, score.value))
        response.append("\n\n")

    new_score = glory_walls["new_score"]
    if len(new_score) > 0:
        if len(new_score) == 1:
            plural_this = "this category"
        else:
            plural_this = "these categories"
        response.append("You did not beat the top score, but you have no scores in %s, so I've added the following to the glory wall for you:\n" % plural_this)
        for score in new_score:
            response.append(" - %s, with a score of %d\n" % (score.category.display_name, score.value))

    if len(response) == 1:
        response.append("Unfortunately, this post did not exceed either your own existing scores, nor any of the top scores.")
    else:
        response.append("You can view the glory wall in all its wally gloriousness here: %s" % WIKI_URL)

    constants.slack.chat.post_message(OUTPUT_CHANNEL, " ".join(response), link_names=True, as_user=True)


if __name__ == "__main__":
    constants.connect()
    on_close()
