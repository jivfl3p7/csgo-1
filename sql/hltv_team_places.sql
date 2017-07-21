begin;

drop table if exists csgo.hltv_team_places;

create table csgo.hltv_team_places (
	event_href	text,
	event_end_date	date,
	team_href	text,
	team_hltv_points float,
	place		float,
	winnings 	float
);

truncate table csgo.hltv_team_places;

copy csgo.hltv_team_places from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_team_places.csv' with delimiter as ',' csv quote as '"';

commit;
