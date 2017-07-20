begin;

drop table if exists csgo.player_winnings;

create table csgo.player_winnings as (
	select
		*,
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
				when lag(p.player_href, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 4) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 4) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int) over (order by main.map_name, p.player_href, tp.event_end_date) +
						(main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int
					)/5
				when lag(p.player_href, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 3) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 3) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int) over (order by main.map_name, p.player_href, tp.event_end_date) +
						(main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int
					)/4
				when lag(p.player_href, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name, 2) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int, 2) over (order by main.map_name, p.player_href, tp.event_end_date) +
						lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int) over (order by main.map_name, p.player_href, tp.event_end_date) +
						(main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int
					)/3
				when lag(p.player_href) over (order by main.map_name, p.player_href, tp.event_end_date) = p.player_href
					and lag(main.map_name) over (order by main.map_name, p.player_href, tp.event_end_date) = main.map_name
					then (lag((main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int) over (order by main.map_name, p.player_href, tp.event_end_date) +
						(main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int
					)/2
				else (main.map_round_share::float/t.total_round_share::float*tp.winnings/5::float)::int
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
							when result != 0.5 then team1_rounds::float/(team1_rounds::float + team2_rounds::float)
							else result::float
						end as round_share
					from csgo.hltv_map_results
				union all
					select distinct
						match_href,
						map_name,
						team2_href as team_href,
						case
							when result != 0.5 then team2_rounds::float/(team1_rounds::float + team2_rounds::float)
							else result::float
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
								when result != 0.5 then team1_rounds::float/(team1_rounds::float + team2_rounds::float)
								else result::float
							end as round_share
						from csgo.hltv_map_results
					union all
						select distinct
							match_href,
							team2_href as team_href,
							case
								when result != 0.5 then team2_rounds::float/(team1_rounds::float + team2_rounds::float)
								else result::float
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

commit;