begin;

drop table if exists csgo.demo_info;

create table csgo.demo_info (
	match_href	text,
	map_num		float,
	map_id		text,
	map_name	text,
	map_hash	float,
	error		text
);

truncate table csgo.demo_info;

\set full_path '\'' :init_path '\\demo_info.csv\''
copy csgo.demo_info from :full_path with delimiter as ',' csv quote as '"';

commit;
