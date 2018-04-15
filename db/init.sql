CREATE TABLE IF NOT EXISTS camelot_users
(
    id  serial primary key,
    name VARCHAR(30) not null,
    slack_id VARCHAR(20) not null,
    is_bot boolean,
    is_deleted boolean
);

CREATE INDEX IF NOT EXISTS camelot_users_slack_id_idx ON camelot_users (slack_id);

CREATE TABLE IF NOT EXISTS camelot_categories
(
    id serial primary key,
    name VARCHAR(50) not null, -- internal name
    display_name VARCHAR(255) not null,
    description text,
    compare_greater boolean -- if true, the winning value must be greater than the current. Otherwise comparison must be lesser than.
);

CREATE INDEX IF NOT EXISTS camelot_categories_name_idx ON camelot_categories (name);

CREATE TABLE IF NOT EXISTS camelot_glory_walls
(
    id serial primary key,
    full_summary_text text not null,
    category_id integer references camelot_categories(id),
    user_id integer references camelot_users(id),
    value integer,
    timestamp timestamp
);

CREATE INDEX IF NOT EXISTS camelot_glory_walls_user_id_category_idx ON camelot_glory_walls (user_id, category_id);


INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_acres', 'Most Acres Gained in a Traditional March', 'Acre gains from a single traditional march', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_acres');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_kills', 'Most Troops Killed in an Attack', 'Enemy Troop kills INCLUDING imprisonments', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_kills');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'fewest_losses', 'Fewest Troop Losses in an Attack', 'Your troop losses EXCLUDING horses (only trainables like ospecs, elites, and soldiers)', false
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'fewest_losses');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_gold', 'Most Gold Stolen in a Plunder Attack', 'Largest amount of gold taken during a single plunder attack', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_gold');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_food', 'Most Food Stolen in a Plunder Attack', 'Largest amount of food taken in a single plunder attack', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_food');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_runes', 'Most Runes Stolen in a Plunder Attack', 'Largest amount of runes taken in a single plunder attack', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_runes');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_scientists', 'Most Scientists Nabbed in an Abduct Attack', 'Most number of scientists taken in a single abduct attack', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_scientists');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_night_strike_kills', 'Most troops assassinated in a single night strike operation', 'Most number of troops assassinated in a single night strike operation', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_night_strike_kills');

INSERT INTO camelot_categories
    (name, display_name, description, compare_greater)
SELECT 'most_buildings_destroyed_in_tornado', 'Most Buildings Destroyed in Tornado', 'Most number of buildings destroyed in a single tornado spell', true
WHERE NOT EXISTS (SELECT 1 FROM camelot_categories WHERE name = 'most_buildings_destroyed_in_tornado');
