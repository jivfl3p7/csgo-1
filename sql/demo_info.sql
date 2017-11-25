begin;

drop table if exists demo.info;

create table demo.info (
	match_href	text,
	map_num		float,
	map_id		text,
	map_name	text,
	map_hash	float,
	error		text
);

truncate table demo.info;

\set full_path '\'' :init_path '\\demo_info.csv\''
copy demo.info from :full_path with delimiter as ',' csv quote as '"';

commit;
