begin;

drop table if exists csgo.hltv_events;

create table csgo.hltv_events (
	event_href	text,
	event_name	text,
	event_end_date	date,
	prize_money	int,
	event_type	text
);

truncate table csgo.hltv_events;

copy csgo.hltv_events from 'C:\Users\wessonmo\Documents\GitHub\csgo\csv\hltv_events.csv' with delimiter as ',' csv quote as '"';

--alter table csgo.hltv_events add column event_id int;

--update csgo.hltv_events set event_id = substring(event_url from '[0-9]{1,}(?=\/)')::int;

commit;
