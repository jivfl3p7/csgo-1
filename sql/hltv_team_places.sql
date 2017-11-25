begin;

drop table if exists hltv.team_places;

create table hltv.team_places (
	event_href	text,
	team_href	text,
	place		float,
	winnings 	float
);

truncate table hltv.team_places;

\set full_path '\'' :init_path '\\hltv_team_places.csv\''
copy hltv.team_places from :full_path with delimiter as ',' csv quote as '"';

commit;
