begin;

drop table if exists csgo.demo_rounds;

create table csgo.demo_primary (
	map_id			text,
	phase			text,
	round			int,
	t_team			text,
	ct_team			text,
	ct_econ_adv		int,
	winner			int
);

truncate table csgo.demo_rounds;

copy csgo.demo_rounds from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_rounds.csv' with delimiter as ',' csv quote as '"';

commit;
