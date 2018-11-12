import re

rob_the_graneries_re = re.compile(r"Our thieves have returned with (?P<bushels>(?:\d,?)+) bushels")
rob_the_vault_re = re.compile(r"Our thieves have returned with (?P<gold>(?:\d,?)+) gold coins")
rob_the_towers_re = re.compile(r"Our thieves were able to steal (?P<runes>(?:\d,?)+) runes")
kidnap_re = re.compile(r"Our thieves kidnapped many people, but only were able to return with (?P<peasants>(?:\d,?)+) of them")
arson_re = re.compile(r"Our thieves burned down (?P<buildings>(?:\d,?)+)")
night_strike_kills_re = re.compile(r"assassinated (?P<night_strike_kills>(?:\d,?)+) enemy troops")
steal_horses_re = re.compile(r"Our thieves were able to release (?P<all_horses>(?:\d,?)+) horses but could only bring back (?P<horses>(\d,?)+) of them")
free_prisoners_re = re.compile(r"Our thieves freed (?P<prisoners>(?:\d,?)+) prisoner(?:s?) from enemy dungeons")
assassinate_wizards_re = re.compile(r"Our thieves assassinated (?P<wizards>(?:\d,?)+) wizard(?:s?)")

propaganda_re = re.compile(r"We have converted (?P<converts>(?:\d,?)+) (?P<remainder>.*)")
# We have converted X [wizards, thieves, soldiers] from the enemy to our guild.
# We have converted X [of the enemy's specialist troops, (elite unit name) from the enemy] to our army.

tornado_re = re.compile(r"laying waste to (?P<buildings>(?:\d,?)+) acres of buildings")
fools_gold_re = re.compile(r"(?P<gold>(?:\d,?)+) gold coins have been turned into worthless lead")
fireball_re = re.compile(r"A fireball burns through the skies of (?:.*). (?P<peasants>(?:\d,?)+) peasants are killed")
lightning_re = re.compile(r"Lightning strikes the Towers in (?:.*) and incinerates (?P<runes>(?:\d,?)+) runes")
nightmare_re = re.compile(r"During the night, (?P<troops>(?:\d,?)+) of the men in the armies")
land_lust_re = re.compile(r"given us another (?P<acres>(?:\d,?)+) acres of land")
tree_of_gold_re = re.compile(r"(?P<gold>(?:\d,?)+) gold coins have fallen from the trees")

books_re = re.compile(r"army looted (?P<books>(?:\d,?)+) books")
massacre_re = re.compile(r"massacred (?P<massacre>(?:\d,?)+) peasants")
acres_re = re.compile(r"Your army has taken (?P<acres>(?:\d,?)+) acre")
kills_re = re.compile(r"We killed about (?P<kills>(?:\d,?)+) enemy troops.\s?(?:We also imprisoned (?P<prisoners>(?:\d,?)+))?")
losses_text_re = re.compile(r"We lost (.*) in this battle")
loss_amount_re = re.compile(r"((?:\d,?)+)\s[A-Za-z]*(?:(?:,|\sand)\s)?")
gold_re = re.compile(r"(?P<gold>(?:\d,?)+) gold coins")
food_re = re.compile(r"(?P<food>(?:\d,?)+) bushels")
runes_re = re.compile(r"(?P<runes>(?:\d,?)+) runes")
scientists_re = re.compile(r"Your army abducted (?P<scientists>[A-Za-z]+) scientists")
attack_message_re = re.compile(r"(Your forces arrive)")
