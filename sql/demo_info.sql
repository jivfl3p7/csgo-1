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

copy csgo.demo_info from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_info.csv' with delimiter as ',' csv quote as '"';

commit;
