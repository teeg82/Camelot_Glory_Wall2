CREATE TABLE IF NOT EXISTS camelot_users
(
    id  serial primary key,
    name VARCHAR(30) not null,
    slack_id VARCHAR(20) not null
);

CREATE TABLE IF NOT EXISTS camelot_categories
(
    id serial primary key,
    name VARCHAR(15) not null, # internal name
    display_name VARCHAR(255) not null,
    description text,
    compare_greater boolean # if true, the winning value must be greater than the current. Otherwise comparison must be lesser than.
);

CREATE TABLE IF NOT EXISTS camelot_glory_walls
(
    id serial primary key,
    full_summary_text text not null,
    category integer references camelot_categories(id),
    user_id integer references camelot_users(id),
    value integer,
    timestamp integer
);
