begin;

drop table if exists csgo.demo_primary;

create table csgo.demo_primary (
	map_id			text,
	round			int,
	t_team			text,
	ct_team			text,
	ct_econ_adv		int,
	winner			int
);

truncate table csgo.demo_primary;

copy csgo.demo_primary from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_primary.csv' with delimiter as ',' csv quote as '"';

commit;
