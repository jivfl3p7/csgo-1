begin;

drop table if exists csgo.hltv_team_ranks;

create table csgo.hltv_team_ranks (
	date_		date,
	rank		integer,
	team_name	text,
	team_id		text,
	points		integer
);

truncate table csgo.hltv_team_ranks;

copy csgo.hltv_team_ranks from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_team_ranks.csv' with delimiter as ',' csv quote as '"';

update csgo.hltv_team_ranks set team_id = substring(team_id from '[0-9]{1,}(?=\/)');

alter table csgo.hltv_team_ranks alter column team_id type int using (team_id::int);

commit;
