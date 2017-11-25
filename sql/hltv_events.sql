begin;

drop table if exists hltv.events;

create table hltv.events (
	event_href	text,
	event_name	text,
	event_end_date	date,
	event_type	text,
	matches		float,
	hltv_rank_dt	date
);

truncate table hltv.events;

\set full_path '\'' :init_path '\\hltv_events.csv\''
copy hltv.events from :full_path with delimiter as ',' csv quote as '"';

commit;
