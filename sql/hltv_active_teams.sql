begin;

drop table if exists csgo.hltv_active_teams;

create table csgo.hltv_active_teams (
	team_href	text,
	lineup		text
);

truncate table csgo.hltv_active_teams;

\set full_path '\'' :init_path '\\hltv_active_teams.csv\''
copy csgo.hltv_active_teams from :full_path with delimiter as ',' csv quote as '"';

commit;
