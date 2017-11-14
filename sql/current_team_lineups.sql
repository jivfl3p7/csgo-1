begin;

drop table if exists csgo.current_team_lineups;

create table csgo.current_team_lineups as (
	select distinct
		a.team_href
		,a.team_name
		,a.match_href
		,a.datetime_utc
		,a.lineup_id
		,sum(a.new_lineup) OVER (partition by a.team_href order by a.datetime_utc desc) as rk
	from (
		select distinct
			a.team_href
			,a.team_name
			,a.match_href
			,a.lineup_id
			,case
				when lead(a.team_href) over () != team_href then 0
				when lead(a.lineup_id) over () != lineup_id then 1
				else 0
			end as new_lineup
			,a.datetime_utc
		from (
			select distinct
				ml.team_href
				,tn.team_name
				,ml.match_href
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
			a.team_href
			,a.datetime_utc desc
			,a.lineup_id
		) as a
	order by
		a.team_href
		,a.datetime_utc desc
		,a.lineup_id
);

commit;