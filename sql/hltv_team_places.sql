begin;

drop table if exists csgo.hltv_team_places;

create table csgo.hltv_team_places (
	event_href	text,
	team_href	text,
	place		float,
	winnings 	float
);

truncate table csgo.hltv_team_places;

\set full_path '\'' :init_path '\\hltv_team_places.csv\''
copy csgo.hltv_team_places from :full_path with delimiter as ',' csv quote as '"';

commit;
