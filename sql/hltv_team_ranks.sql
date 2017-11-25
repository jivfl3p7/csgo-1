begin;

drop table if exists hltv.team_ranks;

create table hltv.team_ranks (
	date_		date,
	rank		float,
	team_name	text,
	team_href	text,
	points		float
);

truncate table hltv.team_ranks;

\set full_path '\'' :init_path '\\hltv_team_ranks.csv\''
copy hltv.team_ranks from :full_path with delimiter as ',' csv quote as '"';

commit;
