begin;

drop table if exists csgo.hltv_events;

create table csgo.hltv_events (
	event_href	text,
	event_name	text,
	event_end_date	date,
	event_type	text,
	matches		float,
	hltv_rank_dt	date
);

truncate table csgo.hltv_events;

\set full_path '\'' :init_path '\\hltv_events.csv\''
copy csgo.hltv_events from :full_path with delimiter as ',' csv quote as '"';

commit;
