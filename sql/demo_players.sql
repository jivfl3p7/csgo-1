begin;

drop table if exists csgo.demo_players;

create table csgo.demo_players (
	map_id		text,
	steam_id	text,
	player_name	text,
	player_team	text
);

truncate table csgo.demo_players;

copy csgo.demo_players from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_players.csv' with delimiter as ',' csv quote as '"';

commit;
