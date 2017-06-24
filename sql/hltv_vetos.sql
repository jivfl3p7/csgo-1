begin;

drop table if exists csgo.hltv_vetos;

create table csgo.hltv_vetos (
	match_id	text,
	step		integer,
	team		text,
	action_		text,
	map		text
);

truncate table csgo.hltv_vetos;

copy csgo.hltv_vetos from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_vetos.csv' with delimiter as ',' csv quote as '"';

update csgo.hltv_vetos set match_id = substring(match_id from '[0-9]{1,}(?=\/)');

alter table csgo.hltv_vetos alter column match_id type int using (match_id::integer);

commit;
