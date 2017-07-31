begin;

drop table if exists csgo.lineups;

create table csgo.lineups as (
	select
		match_href,
		team_href,
		player1||player2||player3||player4||player5 as lineup_id
	from (
		select
			s.match_href,
			s.team_href,
			s.player_href as player1,
			case
				when lead(s.match_href) over (order by s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href) over (order by s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player2,
			case
				when lead(s.match_href,2) over (order by s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,2) over (order by s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,2) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player3,
			case
				when lead(s.match_href,3) over (order by s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,3) over (order by s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,3) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player4,
			case
				when lead(s.match_href,4) over (order by s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,4) over (order by s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,4) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player5
		FROM (
			select distinct
				match_href,
				team_href,
				player_href
			from csgo.hltv_match_stats
			order by team_href, match_href, player_href
			) as s
			left join csgo.hltv_match_info as m
				on s.match_href = m.match_href
		) as a
	where player5 is not null
);

commit;