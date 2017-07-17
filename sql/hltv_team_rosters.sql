begin;

drop table if exists csgo.hltv_team_rosters;

create table csgo.hltv_team_rosters as (
	select distinct
		event_href	text,
		team_href	text,
		player_href	text,
	from csgo.hltv_match_stats
);

truncate table csgo.hltv_team_rosters;

commit;
