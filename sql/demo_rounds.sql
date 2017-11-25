begin;

drop table if exists demo.rounds;

create table demo.rounds (
	match_href		text,
	map_num			float,
	phase			text,
	round			float,
	t_href			text,
	ct_href			text,
	ct_econ_adv		float,
	ct_reward_diff		float,
	defuse			float,
	plant			float,
	winner			float
);

truncate table demo.rounds;

\set full_path '\'' :init_path '\\demo_rounds.csv\''
copy demo.rounds from :full_path with delimiter as ',' csv quote as '"';

commit;
