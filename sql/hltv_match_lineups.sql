begin;

drop table if exists hltv.match_lineups;

create table hltv.match_lineups (
	match_href	text,
	team_href	text,
	lineup		text
);

truncate table hltv.match_lineups;

\set full_path '\'' :init_path '\\hltv_match_lineups.csv\''
copy hltv.match_lineups from :full_path with delimiter as ',' csv quote as '"';

commit;