begin;

drop table if exists csgo.demo_primary;

create table csgo.demo_primary (
	map_id			text,
	round			int,
	t_team			text,
	ct_team			text,
	winner			bytea,
	ct_econ_result		int,
	ct_econ_equip		int,
	t_upg_pistol		int,
	ct_upg_pistol		int,
	t_grenade		int,
	ct_grenade		int,
	t_armor			int,
	ct_armor		int,
	t_t1_rifle		int,
	t_t2_rifle		int,
	t_other_primary		int,
	ct_t1_rifle		int,
	ct_t2_rifle		int,
	ct_other_primary	int
);

truncate table csgo.demo_primary;

copy csgo.demo_primary from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_primary.csv' with delimiter as ',' csv quote as '"';

commit;
