begin;

drop table if exists csgo.current_team_lineups;

create table csgo.current_team_lineups as (
	select distinct on (a.lineup_id)
		a.team_href
		,a.team_name
		,a.lineup_id
		,a.datetime_utc as latest_match
	from (
		select distinct on (ml.team_href)
			ml.team_href
			,tn.team_name
			,ml.datetime_utc
			,ml.lineup_id
		from csgo.match_lineups as ml
			left join (
				select distinct *
				from (
					select distinct
						team1_href as team_href
						,team1_name as team_name
					from csgo.hltv_match_info
					union
					select distinct
						team2_href as team_href
						,team2_name as team_name
					from csgo.hltv_match_info
					) as a
				) as tn
				on ml.team_href = tn.team_href
		order by
			ml.team_href
			,ml.datetime_utc desc
		) as a
	order by
		a.lineup_id
		,a.datetime_utc desc
);

commit;