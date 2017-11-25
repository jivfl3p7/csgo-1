begin;

drop table if exists hltv.vetos;

create table hltv.vetos (
	match_href	text,
	step		float,
	team_href	text,
	action_		text,
	map_name	text
);

truncate table hltv.vetos;

\set full_path '\'' :init_path '\\hltv_vetos.csv\''
copy hltv.vetos from :full_path with delimiter as ',' csv quote as '"';

commit;
