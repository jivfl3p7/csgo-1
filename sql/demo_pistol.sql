begin;

drop table if exists csgo.demo_pistol;

create table csgo.demo_pistol (
	map_id		text,
	round		int,
	t_team		text,
	ct_team		text,
	winner		int
		
);

truncate table csgo.demo_pistol;

copy csgo.demo_pistol from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_pistol.csv' with delimiter as ',' csv quote as '"';

commit;
