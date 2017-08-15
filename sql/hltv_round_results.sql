begin;

drop table if exists csgo.hltv_round_results;

create table csgo.hltv_round_results(
	match_href	text,
	map_num		float,
	map_name	text,
	half		float,
	pseudo_rd	float,
	team1_href	text,
	team1_side	text,
	team2_href	text,
	team2_side	text,
	result		float
);

truncate table csgo.hltv_round_results;

copy csgo.hltv_round_results from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_round_results.csv' with delimiter as ',' csv quote as '"';

commit;