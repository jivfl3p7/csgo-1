begin;

drop table if exists csgo.demo_knife;

create table csgo.demo_knife (
	map_id		text,
	t_team		text,
	ct_team		text,
	winner		int
);

truncate table csgo.demo_knife;

copy csgo.demo_knife from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\demo_knife.csv' with delimiter as ',' csv quote as '"';

commit;