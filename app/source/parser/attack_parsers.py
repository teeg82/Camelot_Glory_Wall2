from helpers import parse_common_pattern
from patterns import *


def most_acres(summary_text):
    """Extract number of acres taken in a trad march."""
    return parse_common_pattern(summary_text, acres_re, "acres")


def most_kills(summary_text):
    """Extract number of kills made in an attack."""
    kills = None
    result = kills_re.search(summary_text)
    if result:
        kills = int(result.group('kills').replace(",", ""))
        if result.group('prisoners'):
            kills += int(result.group('prisoners').replace(",", ""))
    return kills


def fewest_losses(summary_text):
    """Extract number of losses suffered in an outbound attack."""
    losses = None
    result = losses_text_re.search(summary_text)
    if result:
        losses = 0
        losses_text = result.group(1)
        while len(losses_text) > 0:
            losses_result = loss_amount_re.search(losses_text)
            if losses_result:
                # We don't care about horses, since those are not trained soldiers
                if "horse" not in losses_result.group():
                    loss_amount = int(losses_result.group(1).replace(",", ""))
                    losses += loss_amount
                # Strip off what we found so far and allow the next loop to parse the next loss type
                losses_text = losses_text.replace(losses_result.group(), "")
            else:
                # We should never reach this point, but just to ensure that we don't inadvertently cause
                # an infinite loop, lets just get the hell out of here and move on. Sure the numbers
                # will probably be screwed up but that's better than running around in circles forever.
                break

    return losses


def most_gold(summary_text):
    """Extract amount of gold plundered."""
    return parse_common_pattern(summary_text, gold_re, "gold")


def most_food(summary_text):
    """Extract number of bushels plundered."""
    return parse_common_pattern(summary_text, food_re, "food")


def most_runes(summary_text):
    """Extract number of runes plundered."""
    return parse_common_pattern(summary_text, runes_re, "runes")


def most_scientists(summary_text):
    """Extract number of scientists abducted."""
    scientists = None
    result = scientists_re.search(summary_text)
    if result:
        scientists = w2n.word_to_num(result.group('scientists').encode('ascii', 'ignore'))
    return scientists


attack_categories = {
    'most_acres': most_acres,
    'most_kills': most_kills,
    'fewest_losses': fewest_losses,
    'most_gold': most_gold,
    'most_food': most_food,
    'most_runes': most_runes,
    'most_scientists': most_scientists,
}
