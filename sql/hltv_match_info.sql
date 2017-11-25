begin;

drop table if exists hltv.match_info;

create table hltv.match_info (
	event_href	text,
	match_href	text,
	demo_href	text,
	datetime_utc	timestamp,
	team1_name	text,
	team1_href	text,
	team2_name	text,
	team2_href	text
);

truncate table hltv.match_info;

\set full_path '\'' :init_path '\\hltv_match_info.csv\''
copy hltv.match_info from :full_path with delimiter as ',' csv quote as '"';

commit;
