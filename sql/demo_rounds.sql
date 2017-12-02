begin;

drop table if exists demo.rounds;

create table demo.rounds (
    round_start			float,
    winner				float,
    reason				float,
    score_ct			float,
    score_t				float,
    round_decision		float,
    round_end			float,
    plant				float,
    round				float,
    phase				text,
    first_blood			float,
    ct_href				text,
    t_href				text,
    ct_win_streak		float,
    t_equip				float,
    ct_equip			float,
    ct_start_money		float,
    ct_end_money		float,
    t_start_money		float,
    t_end_money			float,
    t_start_t1_primary	float,
    t_end_t1_primary	float,
    t_start_t2_primary	float,
    t_end_t2_primary	float,
    t_start_secondary	float,
    t_end_secondary		float,
    t_start_chest		float,
    t_end_chest			float,
    t_start_helmet		float,
    t_end_helmet		float,
    t_start_flash		float,
    t_end_flash			float,
    t_start_smoke		float,
    t_end_smoke			float,
    t_start_inc			float,
    t_end_inc			float,
    t_start_he			float,
    t_end_he			float,
    t_start_decoy		float,
    t_end_decoy			float,
    t_start_kit			float,
    t_end_kit			float,
    ct_start_t1_primary	float,
    ct_end_t1_primary	float,
    ct_start_t2_primary	float,
    ct_end_t2_primary	float,
    ct_start_secondary	float,
    ct_end_secondary	float,
    ct_start_chest		float,
    ct_end_chest		float,
    ct_start_helmet		float,
    ct_end_helmet		float,
    ct_start_flash		float,
    ct_end_flash		float,
    ct_start_smoke		float,
    ct_end_smoke		float,
    ct_start_inc		float,
    ct_end_inc			float,
    ct_start_he			float,
    ct_end_he			float,
    ct_start_decoy		float,
    ct_end_decoy		float,
    ct_start_kit		float,
    ct_end_kit			float,
    match_href			text,
    map_num				float

);

truncate table demo.rounds;

\set full_path '\'' :init_path '\\demo_rounds.csv\''
copy demo.rounds from :full_path with delimiter as ',' csv quote as '"';

commit;


