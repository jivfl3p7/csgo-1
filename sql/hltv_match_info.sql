begin;

drop table if exists csgo.hltv_match_info;

create table csgo.hltv_match_info (
	event_href	text,
	match_href	text,
	demo_href	text,
	datetime_utc	timestamp,
	team1_name	text,
	team1_href	text,
	team2_name	text,
	team2_href	text
);

truncate table csgo.hltv_match_info;

copy csgo.hltv_match_info from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_match_info.csv' with delimiter as ',' csv quote as '"';

commit;
