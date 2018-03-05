"""
Author: Paul Richter, 2018.

Handles parsing of summary messages, returns python values.
"""

from word2number import w2n
import re


acres_re = re.compile("Your army has taken (?P<acres>(\d,?)+) acre")


def most_acres(summary_text):
    """Extract number of acres taken in a trad march."""
    acres = None
    result = acres_re.search(summary_text)
    if result:
        acres = int(result.group('acres').replace(",", ""))
    return acres


kills_re = re.compile("We killed about (?P<kills>(\d,?)+) enemy troops.\s?(We also imprisoned (?P<prisoners>\d+))?")


def most_kills(summary_text):
    """Extract number of kills made in an attack."""
    kills = None
    result = kills_re.search(summary_text)
    if result:
        kills = int(result.group('kills').replace(",", ""))
        if result.group('prisoners'):
            kills += int(result.group('prisoners').replace(",", ""))
    return kills


losses_text_re = re.compile(r"We lost (.*) in this battle")
loss_amount_re = re.compile(r"((\d,?)+)\s[A-Za-z]*((,|\sand)\s)?")


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


gold_re = re.compile(r"(?P<gold>(\d,?)+) gold coins")


def most_gold(summary_text):
    """Extract amount of gold plundered."""
    gold = None
    result = gold_re.search(summary_text)
    if result:
        gold = int(result.group('gold').replace(",", ""))
    return gold


food_re = re.compile(r"(?P<food>(\d,?)+) bushels")


def most_food(summary_text):
    """Extract number of bushels plundered."""
    food = None
    result = food_re.search(summary_text)
    if result:
        food = int(result.group('food').replace(",", ""))
    return food


runes_re = re.compile(r"(?P<runes>(\d,?)+) runes")


def most_runes(summary_text):
    """Extract number of runes plundered."""
    runes = None
    result = runes_re.search(summary_text)
    if result:
        runes = int(result.group('runes').replace(",", ""))
    return runes


scientists_re = re.compile(r"Your army abducted (?P<scientists>[A-Za-z]+) scientists")


def most_scientists(summary_text):
    """Extract number of scientists abducted."""
    scientists = None
    result = scientists_re.search(summary_text)
    if result:
        scientists = w2n.word_to_num(result.group('scientists'))
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


def parse(summary_text):
    """Main parsing entry point - attempt to parse as much information as possible, scanning multiple times."""
    # We will attempt to identify the type of summary text by passing it through various parsers
    # Whichever one retrieves something will determine the message type.
    results = parse_attack_messages(summary_text)
    if not results:
        pass  # move on to another category
    print("This is what I found: %s" % str(results))
    return results


def parse_attack_messages(summary_text):
    """Attempt to parse attack-oriented information such as kills, acres, losses, etc."""
    results = []
    acres = attack_categories['most_acres'](summary_text)
    if acres is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_acres', 'value': acres}
        results.append(result)

    kills = attack_categories['most_kills'](summary_text)
    if kills is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_kills', 'value': kills}
        results.append(result)

    losses = attack_categories['fewest_losses'](summary_text)
    if losses is not None:
        result = {'summary_text': summary_text, 'category_name': 'fewest_losses', 'value': losses}
        results.append(result)

    gold = attack_categories['most_gold'](summary_text)
    if gold is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_gold', 'value': gold}
        results.append(result)

    food = attack_categories['most_food'](summary_text)
    if food is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_food', 'value': food}
        results.append(result)

    runes = attack_categories['most_runes'](summary_text)
    if runes is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_runes', 'value': runes}
        results.append(result)

    scientists = attack_categories['most_scientists'](summary_text)
    if scientists is not None:
        result = {'summary_text': summary_text, 'category_name': 'most_scientists', 'value': scientists}
        results.append(result)

    if len(results) > 0:
        return results
    else:
        return None
