import re


"""
Your forces arrive at PacMan (6:19). A tough battle took place, but we have managed a victory! Your army has taken 69 acres! 39 acres of buildings survived and can be refitted to fit our needs. We also gained 98 specialist training credits. Taking full control of your new land will take 12.00 days, and will be available on May 14 of YR0. 311 peasants settled on your new lands.
We lost 55 Warriors, 3 Berserkers and 58 horses in this battle.
We killed about 32 enemy troops. We also imprisoned 60 additional troops in our Dungeons.
Our forces will be available again in 12.00 days (on May 14 of YR0).
"""
acres_re = re.compile("Your army has taken (?P<acres>\d+) acre")
def most_acres(summary_text):
    acres = None
    result = acres_re.search(summary_text)
    if result:
        acres = int(result.group('acres'))
    return acres


kills_re = re.compile("We killed about (?P<kills>\d+) enemy troops. (We also imprisoned (?P<prisoners>\d+))?")
def most_kills(summary_text):
    kills = None
    result = kills_re.search(summary_text)
    if result:
        kills = int(result.group('kills'))
        if result.group('prisoners'):
            kills += int(result.group('prisoners'))
    return kills


losses_text_re = re.compile(r"We lost (.*) in this battle")
loss_amount_re = re.compile(r"(\d+)\s[A-Za-z]*((,|\sand)\s)?")
def fewest_losses(summary_text):
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
                    loss_amount = int(losses_result.group(1))
                    losses += loss_amount
                # Strip off what we found so far and allow the next loop to parse the next loss type
                losses_text = losses_text.replace(losses_result.group(), "")
            else:
                # We should never reach this point, but just to ensure that we don't inadvertently cause
                # an infinite loop, lets just get the hell out of here and move on. Sure the numbers
                # will probably be screwed up but that's better than running around in circles forever.
                break

    return losses


attack_categories = {
    'most_acres': most_acres,
    'most_kills': most_kills,
    'fewest_losses': fewest_losses,
}


def parse(summary_text):
    # We will attempt to identify the type of summary text by passing it through various parsers
    # Whichever one retrieves something will determine the message type.
    results = parse_attack_messages(summary_text)
    if not results:
        pass # move on to another category
    print("This is what I found: %s" % str(results))
    return results


def parse_attack_messages(summary_text):
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

    if len(results) > 0:
        return results
    else:
        return None
