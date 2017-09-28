begin;

drop table if exists csgo.hltv_map_results;

create table csgo.hltv_map_results (
	match_href	text,
	map_num		float,
	map_name	text,
	team1_href	text,
	team1_rounds	float,
	team2_href	text,
	team2_rounds	float,
	result		float,
	abs_result	float
);

truncate table csgo.hltv_map_results;

copy csgo.hltv_map_results from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_map_results.csv' with delimiter as ',' csv quote as '"';

commit;
