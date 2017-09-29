begin;

drop table if exists csgo.demo_rounds;

create table csgo.demo_rounds (
	match_href		text,
	map_num			float,
	phase			text,
	round			float,
	t_team			text,
	ct_team			text,
	ct_econ_adv		float,
	winner			float
);

truncate table csgo.demo_rounds;

copy csgo.demo_rounds from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_rounds.csv' with delimiter as ',' csv quote as '"';

commit;
