begin;

drop table if exists csgo.hltv_player_stats;

create table csgo.hltv_player_stats (
	match_href	text,
	map_name	text,
	team_href	text,
	player_href	text,
	player_name	text,
	kd		float
);

truncate table csgo.hltv_player_stats;

copy csgo.hltv_player_stats from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_player_stats.csv' with delimiter as ',' csv quote as '"';

update csgo.hltv_player_stats set player_href = (case when player_href is null then replace(player_name, '%', '') else replace(player_href, '%', '') end);

commit;