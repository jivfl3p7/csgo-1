begin;

drop table if exists csgo.hltv_player_winnings;

create table csgo.hltv_player_winnings as (
	select
		*,
		case
			when lag(player_href) over (order by player_href, event_end_date) = player_href
				then lag(winnings) over (order by player_href, event_end_date)
			else null
		end as prev_winnings
	from (
		select
			t.event_href,
			t.event_end_date,
			t.team_href,
			p.player_href,
			case
				when lag(p.player_href, 4) over (order by p.player_href, t.event_end_date) = p.player_href
					then (lag(t.winnings/5, 4) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5, 3) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5, 2) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5) over (order by p.player_href, t.event_end_date) +
						t.winnings/5
					)/5
				when lag(p.player_href, 3) over (order by p.player_href, t.event_end_date) = p.player_href
					then (lag(t.winnings/5, 3) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5, 2) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5) over (order by p.player_href, t.event_end_date) +
						t.winnings/5
					)/4
				when lag(p.player_href, 2) over (order by p.player_href, t.event_end_date) = p.player_href
					then (lag(t.winnings/5, 2) over (order by p.player_href, t.event_end_date) +
						lag(t.winnings/5) over (order by p.player_href, t.event_end_date) +
						t.winnings/5
					)/3
				when lag(p.player_href) over (order by p.player_href, t.event_end_date) = p.player_href
					then (lag(t.winnings/5) over (order by p.player_href, t.event_end_date) +
						t.winnings/5
					)/2
				else t.winnings/5
			end as winnings
			--rank() over (partition by p.player_href order by t.event_end_date asc) as recent
		from csgo.hltv_team_places as t
			left join (
				select distinct
					event_href,
					team_href,
					player_href
				from csgo.hltv_match_stats
				) as p
				on t.event_href = p.event_href
					and t.team_href = p.team_href
		where winnings != 0
		order by player_href, event_end_date
	) as a
);

commit;
