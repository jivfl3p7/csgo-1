begin;

drop table if exists csgo.hltv_match_info;

create table csgo.hltv_match_info (
	event_href	text,
	match_href	text,
	demo_href	text,
	datetime_utc	timestamp,
	team1_name	text,
	team1_id	text,
	team2_name	text,
	team2_id	text
);

truncate table csgo.hltv_match_info;

copy csgo.hltv_match_info from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_match_info.csv' with delimiter as ',' csv quote as '"';
/*
update csgo.hltv_match_info
set
	event_id = substring(event_id from '[0-9]{1,}(?=\/)'),
	match_id = substring(match_id from '[0-9]{1,}(?=\/)'),
	demo_id = substring(demo_id from '[0-9]{1,}'),
	team1_id = substring(team1_id from '[0-9]{1,}(?=\/)'),
	team2_id = substring(team2_id from '[0-9]{1,}(?=\/)')
;


alter table csgo.hltv_match_info
	alter column event_id type int using (event_id::int),
	alter column match_id type int using (match_id::int),
	alter column demo_id type int using (demo_id::int),
	alter column team1_id type int using (team1_id::int),
	alter column team2_id type int using (team2_id::int)
;
*/
commit;
