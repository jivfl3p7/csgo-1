begin;

drop table if exists hltv.active_teams;

create table hltv.active_teams (
	team_href	text,
	team_name	text,
	lineup		text
);

truncate table hltv.active_teams;

\set full_path '\'' :init_path '\\hltv_active_teams.csv\''
copy hltv.active_teams from :full_path with delimiter as ',' csv quote as '"';

commit;
