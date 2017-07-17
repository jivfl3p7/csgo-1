begin;

drop table if exists csgo.hltv_match_stats;

create table csgo.hltv_match_stats (
	event_href	text,
	match_href	text,
	map_name	text,
	team_href	text,
	player_href	text,
	player_name	text,
	kd		float
);

truncate table csgo.hltv_match_stats;

copy csgo.hltv_match_stats from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_match_stats.csv' with delimiter as ',' csv quote as '"';

commit;
