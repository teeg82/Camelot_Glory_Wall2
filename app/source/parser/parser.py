"""
Author: Paul Richter, 2018.

Handles parsing of summary messages, returns python values.
"""

from word2number import w2n
from patterns import *
from attack_parsers import attack_categories
from tm_parsers import tm_categories
from helpers import parse_common_pattern
import re


def parse_attack_messages(summary_text):
    """Attempt to parse attack-oriented information such as kills, acres, losses, etc."""
    results = []

    is_attack_message = attack_message_re.search(summary_text)
    # Reject this entirely if it does not look like an attack message.
    if(is_attack_message):
        for category, parser in attack_categories.iteritems():
            value = parser(summary_text)
            if value is not None:
                result = {'summary_text': summary_text, 'category_name': category, 'value': value}
                results.append(result)

    if len(results) > 0:
        return results
    else:
        return None


def parse_tm_messages(summary_text):
    """Attempt to parse thief-oriented information such as night strike kills, propaganda conversions, etc."""
    results = []

    for category, parser in tm_categories.iteritems():
        value = parser(summary_text)
        if value is not None:
            results.append({'summary_text': summary_text, 'category_name': category, 'value': value})

    if len(results) > 0:
        return results;
    else:
        return None


def parse(summary_text):
    """Main parsing entry point - attempt to parse as much information as possible, scanning multiple times."""
    # We will attempt to identify the type of summary text by passing it through various parsers
    # Whichever one retrieves something will determine the message type.
    results = parse_attack_messages(summary_text)
    if not results:
        results = parse_tm_messages(summary_text)
    print("This is what I found: %s" % str(results))
    return results
