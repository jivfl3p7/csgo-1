begin;

drop table if exists csgo.hltv_match_lineups;

create table csgo.hltv_match_lineups (
	match_href	text,
	team_href	text,
	lineup		text
);

truncate table csgo.hltv_match_lineups;

\set full_path '\'' :init_path '\\hltv_match_lineups.csv\''
copy csgo.hltv_match_lineups from :full_path with delimiter as ',' csv quote as '"';

commit;