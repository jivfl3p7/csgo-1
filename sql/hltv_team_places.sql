begin;

drop table if exists csgo.hltv_team_places;

create table csgo.hltv_team_places (
	event_href	text,
	team_href	text,
	place		float,
	winnings 	float
);

truncate table csgo.hltv_team_places;

copy csgo.hltv_team_places from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_team_places.csv' with delimiter as ',' csv quote as '"';

commit;
