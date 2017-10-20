begin;

drop table if exists csgo.demo_rounds;

create table csgo.demo_rounds (
	match_href		text,
	map_num			float,
	phase			text,
	round			float,
	t_href			text,
	ct_href			text,
	ct_econ_adv		float,
	ct_reward_diff		float,
	winner			float
);

truncate table csgo.demo_rounds;

\set full_path '\'' :init_path '\\demo_rounds.csv\''
copy csgo.demo_rounds from :full_path with delimiter as ',' csv quote as '"';

commit;
