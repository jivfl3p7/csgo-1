begin;

create temp table player_placings as (
	select
		*,
		case
			when lag(player_href) over (order by map_name, player_href, event_end_date) = player_href
				and lag(map_name) over (order by map_name, player_href, event_end_date) = map_name
				then lag(num_events) over (order by map_name, player_href, event_end_date)
			else null
		end as prev_num_events,
		case
			when lag(player_href) over (order by map_name, player_href, event_end_date) = player_href
				and lag(map_name) over (order by map_name, player_href, event_end_date) = map_name
				then lag(points) over (order by map_name, player_href, event_end_date)
			else null
		end as prev_points
	from (
		select
			main.event_href,
			ep.event_end_date,
			main.team_href,
			p.player_href,
			main.map_name,
			case
				when lag(p.player_href, 9) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 9) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 10
				when lag(p.player_href, 8) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 8) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 9
				when lag(p.player_href, 7) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 7) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 8
				when lag(p.player_href, 6) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 6) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 7
				when lag(p.player_href, 5) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 5) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 6
				when lag(p.player_href, 4) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 4) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 5
				when lag(p.player_href, 3) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 3) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 4
				when lag(p.player_href, 2) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 2) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 3
				when lag(p.player_href) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then 2
				else 1
			end as num_events,
			case
				when lag(p.player_href, 9) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 9) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 9) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 8) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 7) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 6) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/10
				when lag(p.player_href, 8) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 8) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 8) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 7) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 6) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/9
				when lag(p.player_href, 7) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 7) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 7) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 6) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/8
				when lag(p.player_href, 6) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 6) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 6) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/7
				when lag(p.player_href, 5) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 5) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/6
				when lag(p.player_href, 4) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 4) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 4) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/5
				when lag(p.player_href, 3) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 3) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 3) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/4
				when lag(p.player_href, 2) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name, 2) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5, 2) over (order by main.map_name, p.player_href, ep.event_end_date) +
						lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/3
				when lag(p.player_href) over (order by main.map_name, p.player_href, ep.event_end_date) = p.player_href
					and lag(main.map_name) over (order by main.map_name, p.player_href, ep.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*ep.event_points/5) over (order by main.map_name, p.player_href, ep.event_end_date) +
						main.map_round_share/t.total_round_share*ep.event_points/5
					)/2
				else main.map_round_share/t.total_round_share*ep.event_points/5
			end as points
		from (
			select distinct
				mi.event_href,
				mr.team_href,
				mr.map_name,
				sum(mr.round_share) as map_round_share
			from (
					select distinct
						match_href,
						map_name,
						team1_href as team_href,
						case
							when result != 0.5 then team1_rounds/(team1_rounds + team2_rounds)
							else result
						end as round_share
					from csgo.hltv_map_results
				union all
					select distinct
						match_href,
						map_name,
						team2_href as team_href,
						case
							when result != 0.5 then team2_rounds/(team1_rounds + team2_rounds)
							else result
						end as round_share
					from csgo.hltv_map_results
				) as mr
				left join csgo.hltv_match_info as mi
					on mr.match_href = mi.match_href
				
			group by
				mi.event_href,
				mr.team_href,
				mr.map_name
			order by
				mi.event_href,
				mr.team_href,
				map_name
			) as main
			left join (
				select distinct
					mi.event_href,
					mr.team_href,
					sum(mr.round_share) as total_round_share
				from (
						select distinct
							match_href,
							team1_href as team_href,
							case
								when result != 0.5 then team1_rounds/(team1_rounds + team2_rounds)
								else result
							end as round_share
						from csgo.hltv_map_results
					union all
						select distinct
							match_href,
							team2_href as team_href,
							case
								when result != 0.5 then team2_rounds/(team1_rounds + team2_rounds)
								else result
							end as round_share
						from csgo.hltv_map_results
					) as mr
					left join csgo.hltv_match_info as mi
						on mr.match_href = mi.match_href
					
				group by
					mi.event_href,
					mr.team_href
				order by
					mi.event_href,
					mr.team_href
				) as t
				on
					main.event_href = t.event_href
					and main.team_href = t.team_href
			left join (
				select distinct
					event_href,
					team_href,
					player_href
				from csgo.hltv_match_stats
				) as p
				on
					main.event_href = p.event_href
					and main.team_href = p.team_href
			left join (
				select
					main.event_href,
					main.event_end_date,
					team_href,
					(num_teams + 1 - place)/num_teams*event_hltv_points as event_points
				from csgo.hltv_team_places as main
					left join (
						select distinct
							event_href,
							count(distinct team_href) as num_teams,
							sum(team_hltv_points) as event_hltv_points
						from csgo.hltv_team_places
						group by event_href
						) as ae
						on main.event_href = ae.event_href
				order by
					event_end_date,
					(num_teams + 1 - place)/num_teams*event_hltv_points desc
				) as ep
				on
					main.event_href = ep.event_href
					and main.team_href = ep.team_href
			order by main.map_name, p.player_href, ep.event_end_date
		) as a
	order by map_name, player_href, event_end_date
);

create temp table player_winnings as (
	select
		*,
		case
			when lag(player_href) over (order by map_name, player_href, event_end_date) = player_href
				and lag(map_name) over (order by map_name, player_href, event_end_date) = map_name
				then lag(num_events) over (order by map_name, player_href, event_end_date)
			else null
		end as prev_num_events,
		case
			when lag(player_href) over (order by map_name, player_href, event_end_date) = player_href
				and lag(map_name) over (order by map_name, player_href, event_end_date) = map_name
				then lag(winnings) over (order by map_name, player_href, event_end_date)
			else null
		end as prev_winnings
	from (
		select
			main.event_href,
			tp.event_end_date,
			main.team_href,
			p.player_href,
			main.map_name,
			case
				when lag(p.player_href, 9) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 9) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 10
				when lag(p.player_href, 8) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 8) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 9
				when lag(p.player_href, 7) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 7) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 8
				when lag(p.player_href, 6) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 6) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 7
				when lag(p.player_href, 5) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 5) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 6
				when lag(p.player_href, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 5
				when lag(p.player_href, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 4
				when lag(p.player_href, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 3
				when lag(p.player_href) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then 2
				else 1
			end as num_events,
			case
				when lag(p.player_href, 9) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 9) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 9) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 8) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 7) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 6) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/10
				when lag(p.player_href, 8) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 8) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 8) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 7) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 6) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/9
				when lag(p.player_href, 7) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 7) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 7) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 6) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/8
				when lag(p.player_href, 6) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 6) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 6) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/7
				when lag(p.player_href, 5) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 5) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/6
				when lag(p.player_href, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/5
				when lag(p.player_href, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/4
				when lag(p.player_href, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/3
				when lag(p.player_href) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag(main.map_round_share/t.total_round_share*tp.winnings/5) over (order by main.map_name, p.player_href, tp.event_end_date) +
						main.map_round_share/t.total_round_share*tp.winnings/5
					)/2
				else main.map_round_share/t.total_round_share*tp.winnings/5
			end as winnings
		from (
			select distinct
				mi.event_href,
				mr.team_href,
				mr.map_name,
				sum(mr.round_share) as map_round_share
			from (
					select distinct
						match_href,
						map_name,
						team1_href as team_href,
						case
							when result != 0.5 then team1_rounds/(team1_rounds + team2_rounds)
							else result
						end as round_share
					from csgo.hltv_map_results
				union all
					select distinct
						match_href,
						map_name,
						team2_href as team_href,
						case
							when result != 0.5 then team2_rounds/(team1_rounds + team2_rounds)
							else result
						end as round_share
					from csgo.hltv_map_results
				) as mr
				left join csgo.hltv_match_info as mi
					on mr.match_href = mi.match_href
				
			group by
				mi.event_href,
				mr.team_href,
				mr.map_name
			order by
				mi.event_href,
				mr.team_href,
				map_name
			) as main
			left join (
				select distinct
					mi.event_href,
					mr.team_href,
					sum(mr.round_share) as total_round_share
				from (
						select distinct
							match_href,
							team1_href as team_href,
							case
								when result != 0.5 then team1_rounds/(team1_rounds + team2_rounds)
								else result
							end as round_share
						from csgo.hltv_map_results
					union all
						select distinct
							match_href,
							team2_href as team_href,
							case
								when result != 0.5 then team2_rounds/(team1_rounds + team2_rounds)
								else result
							end as round_share
						from csgo.hltv_map_results
					) as mr
					left join csgo.hltv_match_info as mi
						on mr.match_href = mi.match_href
					
				group by
					mi.event_href,
					mr.team_href
				order by
					mi.event_href,
					mr.team_href
				) as t
				on
					main.event_href = t.event_href
					and main.team_href = t.team_href
			left join (
				select distinct
					event_href,
					team_href,
					player_href
				from csgo.hltv_match_stats
				) as p
				on
					main.event_href = p.event_href
					and main.team_href = p.team_href
			left join csgo.hltv_team_places as tp
				on 
					main.event_href = tp.event_href
					and main.team_href = tp.team_href
			where tp.winnings is not null
			order by main.map_name, p.player_href, tp.event_end_date
		) as a
	order by map_name, player_href, event_end_date
);

create temp table lineup_stats as (
	select
		p.event_href,
		p.event_end_date,
		p.team_href,
		p.player_href,
		p.map_name,
		p.prev_num_events as pt_prev_events,
		p.prev_points,
		w.prev_num_events as win_prev_events,
		w.prev_winnings
	from player_placings as p
		left join player_winnings as w
			on
				p.event_href = w.event_href
				and p.event_href = w.event_href
				and p.team_href = w.team_href
				and p.player_href = w.player_href
				and p.map_name = w.map_name
	order by
		p.map_name, p.player_href, p.event_end_date
);


drop table if exists csgo.lineup_init_stats;

create table csgo.lineup_init_stats as (
	SELECT
		main.event_href,
		main.match_href,
		main.map_name,
		main.team_href,
		player1||player2||player3||player4||player5 as lineup_id,
		win_prev_events,
		prev_winnings,
		pt_prev_events,
		prev_points
	FROM (
		SELECT
			s.event_href,
			s.match_href,
			s.map_name,
			m.datetime_utc,
			s.team_href,
			s.player_href as player1,
			case
				when lead(s.match_href) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.match_href
					and lead(s.map_name) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.map_name
					and lead(s.team_href) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href) over (order by s.team_href, s.match_href, s.map_name, s.player_href)
				else null
			end as player2,
			case
				when lead(s.match_href,2) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.match_href
					and lead(s.map_name,2) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.map_name
					and lead(s.team_href,2) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,2) over (order by s.team_href, s.match_href, s.map_name, s.player_href)
				else null
			end as player3,
			case
				when lead(s.match_href,3) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.match_href
					and lead(s.map_name,3) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.map_name
					and lead(s.team_href,3) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,3) over (order by s.team_href, s.match_href, s.map_name, s.player_href)
				else null
			end as player4,
			case
				when lead(s.match_href,4) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.match_href
					and lead(s.map_name,4) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.map_name
					and lead(s.team_href,4) over (order by s.event_href, s.match_href, s.map_name, s.team_href, s.player_href) = s.team_href
					then lead(s.player_href,4) over (order by s.team_href, s.match_href, s.map_name, s.player_href)
				else null
			end as player5
		FROM (
			SELECT DISTINCT
				event_href,
				match_href,
				map_name,
				team_href,
				player_href
			FROM csgo.hltv_match_stats
			ORDER BY team_href, match_href, map_name, player_href
			) as s
			LEFT JOIN csgo.hltv_match_info as m
				on s.match_href = m.match_href
		) as main
			LEFT JOIN (
				select distinct
					event_href,
					match_href,
					map_name,
					team_href,
					sum(win_prev_events) as win_prev_events,
					sum(prev_winnings) as prev_winnings,
					sum(pt_prev_events) as pt_prev_events,
					sum(prev_points) as prev_points
				from (
					select distinct
						m.event_href,
						m.match_href,
						m.map_name,
						m.team_href,
						m.player_href,
						case
							when ls.win_prev_events is null
								then 0
							else ls.win_prev_events
						end as win_prev_events,
						case
							when ls.prev_winnings is null
								then 0
							else ls.prev_winnings
						end as prev_winnings,
						case
							when ls.pt_prev_events is null
								then 0
							else ls.pt_prev_events
						end as pt_prev_events,
						case
							when ls.prev_points is null
								then 0
							else ls.prev_points
						end as prev_points
					from csgo.hltv_match_stats as m
						left join lineup_stats as ls
							on m.event_href = ls.event_href
							and m.map_name = ls.map_name
							and m.player_href = ls.player_href
					) as a
				group by
					event_href,
					match_href,
					map_name,
					team_href
				) as ls
					on main.match_href = ls.match_href
						and main.map_name = ls.map_name
						and main.team_href = ls.team_href
	WHERE player5 is not null
	ORDER BY team_href, datetime_utc
);

commit;