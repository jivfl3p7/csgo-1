begin;

drop table if exists csgo.hltv_event_team_places;

create table csgo.hltv_event_team_places (
	event_href	text,
	event_end_date	date,
	team_href	text,
	place		int,
	winnings 	int
);

truncate table csgo.hltv_event_team_places;

copy csgo.hltv_event_team_places from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_event_team_places.csv' with delimiter as ',' csv quote as '"';

commit;
