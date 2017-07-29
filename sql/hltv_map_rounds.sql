begin;

drop table if exists csgo.hltv_map_rounds;

create table csgo.hltv_map_rounds (
	match_href	text,
	map_name	text,
	team1_side	text,
	team2_side	text,
	result		float
);

truncate table csgo.hltv_map_rounds;

copy csgo.hltv_map_rounds from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_map_rounds.csv' with delimiter as ',' csv quote as '"';

commit;
