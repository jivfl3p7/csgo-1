begin;

drop table if exists csgo.hltv_team_ranks;

create table csgo.hltv_team_ranks (
	date_		date,
	rank		float,
	team_name	text,
	team_href	text,
	points		float
);

truncate table csgo.hltv_team_ranks;

copy csgo.hltv_team_ranks from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_team_ranks.csv' with delimiter as ',' csv quote as '"';

commit;
