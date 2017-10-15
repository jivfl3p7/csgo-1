begin;

drop table if exists csgo.hltv_vetos;

create table csgo.hltv_vetos (
	match_href	text,
	step		float,
	team_name	text,
	action_		text,
	map		text
);

truncate table csgo.hltv_vetos;

\set full_path '\'' :init_path '\\hltv_vetos.csv\''
copy csgo.hltv_vetos from :full_path with delimiter as ',' csv quote as '"';

commit;
