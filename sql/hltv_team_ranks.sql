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

\set full_path '\'' :init_path '\\hltv_team_ranks.csv\''
copy csgo.hltv_team_ranks from :full_path with delimiter as ',' csv quote as '"';

commit;
