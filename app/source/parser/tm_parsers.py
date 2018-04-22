from helpers import parse_common_pattern
from patterns import *


##### THIEF OPS #####


def rob_the_granaries(summary_text):
    return parse_common_pattern(summary_text, rob_the_graneries_re, "bushels")


def rob_the_vault(summary_text):
    return parse_common_pattern(summary_text, rob_the_vault_re, "gold")


def rob_the_towers(summary_text):
    return parse_common_pattern(summary_text, rob_the_towers_re, "runes")


def kidnap(summary_text):
    return parse_common_pattern(summary_text, kidnap_re, "peasants")


def arson(summary_text):
    return parse_common_pattern(summary_text, arson_re, "buildings")


def night_strike(summary_text):
    return parse_common_pattern(summary_text, night_strike_kills_re, "night_strike_kills")


def steal_horses(summary_text):
    return parse_common_pattern(summary_text, steal_horses_re, "horses")


def free_prisoners(summary_text):
    return parse_common_pattern(summary_text, free_prisoners_re, "prisoners")


def assassinate_wizards(summary_text):
    return parse_common_pattern(summary_text, assassinate_wizards_re, "wizards")


def propaganda(summary_text):
    return parse_common_pattern(summary_text, propaganda_re, "converts")


##### MAGE SPELLS #####


def tornado(summary_text):
    return parse_common_pattern(summary_text, tornado_re, "buildings")


def fools_gold(summary_text):
    return parse_common_pattern(summary_text, fools_gold_re, "gold")


def fireball(summary_text):
    return parse_common_pattern(summary_text, fireball_re, "peasants")


def lightning(summary_text):
    return parse_common_pattern(summary_text, lightning_re, "runes")


def nightmare(summary_text):
    return parse_common_pattern(summary_text, nightmare_re, "troops")


tm_categories = {
    'rob_the_granaries': rob_the_granaries,
    'rob_the_vault': rob_the_vault,
    'rob_the_towers': rob_the_towers,
    'kidnap': kidnap,
    'arson': arson,
    'night_strike': night_strike,
    'steal_horses': steal_horses,
    'free_prisoners': free_prisoners,
    'assassinate_wizards': assassinate_wizards,
    'propaganda': propaganda,
    'tornado': tornado,
    'fools_gold': fools_gold,
    'fireball': fireball,
    'lightning': lightning,
    'nightmare': nightmare,
}
