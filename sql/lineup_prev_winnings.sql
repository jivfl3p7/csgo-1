begin;

drop table if exists csgo.lineup_prev_winnings;

create table csgo.lineup_prev_winnings as (
	SELECT
		main.event_href,
		main.match_href,
		main.team_href,
		player1||player2||player3||player4||player5 as lineup_id,
		prev_winnings
	FROM (
		SELECT
			s.event_href,
			s.match_href,
			m.datetime_utc,
			s.team_href,
			s.player_href as player1,
			case
				when lead(s.match_href) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player2,
			case
				when lead(s.match_href,2) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,2) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,2) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player3,
			case
				when lead(s.match_href,3) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,3) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,3) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player4,
			case
				when lead(s.match_href,4) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.match_href
					and lead(s.team_href,4) over (order by s.event_href, s.match_href, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,4) over (order by s.team_href, s.match_href, s.player_href)
				else null
			end as player5
		FROM (
			SELECT DISTINCT
				event_href,
				match_href,
				team_href,
				player_href
			FROM csgo.hltv_match_stats
			ORDER BY team_href, match_href, player_href
			) as s
			LEFT JOIN csgo.hltv_match_info as m
				on s.match_href = m.match_href
		) as main
			LEFT JOIN (
				select distinct
					event_href,
					match_href,
					team_href,
					sum(prev_winnings) as prev_winnings
				from (
					select distinct
						m.event_href,
						m.match_href,
						m.team_href,
						m.player_href,
						case
							when pw.prev_winnings is null
								then 0
							else pw.prev_winnings
						end as prev_winnings
					from csgo.hltv_match_stats as m
						left join csgo.player_winnings as pw
							on m.event_href = pw.event_href
							and m.player_href = pw.player_href
					) as a
				group by 
					event_href,
					match_href,
					team_href
				) as lw
					on main.match_href = lw.match_href
						and main.team_href = lw.team_href
	WHERE player5 is not null
	ORDER BY team_href, datetime_utc
);

commit;
