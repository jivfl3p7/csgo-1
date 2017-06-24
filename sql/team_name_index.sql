begin;

drop table if exists csgo.team_name_index;

create table csgo.team_name_index (
	hltv_team_id	text,
	hltv_team_name	text,
	demo_team_name	text,
	fuzzy_score	int
);

truncate table csgo.team_name_index;

copy csgo.team_name_index from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\team_name_index.csv' with delimiter as ',' csv quote as '"';

update csgo.team_name_index set hltv_team_id = substring(hltv_team_id from '[0-9]{1,}(?=\/)');

alter table csgo.team_name_index alter column hltv_team_id type int using (hltv_team_id::int);

commit;