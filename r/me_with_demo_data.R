library(RPostgreSQL)
library(lme4)
library(plyr)
library(dplyr)
library(sm)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

round_query <- dbSendQuery(con, "
select distinct
  left(mi.datetime_utc::varchar,4)::int as season
  ,mi.datetime_utc
  ,mi.event_href
  ,dr.match_href
  ,dr.map_num
  ,di.map_name
  ,dr.round
  ,dr.t_href
  ,tl2.team_name||'_'||(tl2.rk)::text as t_team
  ,tl.lineup_id as t_lineup
  ,dr.ct_href
  ,ctl2.team_name||'_'||(ctl2.rk)::text as ct_team
  ,ctl.lineup_id as ct_lineup
  ,dr.ct_econ_adv as ct_econ_adv
  ,dr.ct_reward_diff
  ,dr.winner as winner
from csgo.demo_rounds as dr
  left join csgo.demo_info as di
    on
      dr.match_href = di.match_href
      and dr.map_num = di.map_num
  left join csgo.hltv_match_info as mi
    on dr.match_href = mi.match_href
  left join csgo.hltv_events as e
    on mi.event_href = e.event_href
  left join csgo.match_lineups as tl
    on
      dr.match_href = tl.match_href
      and dr.t_href = tl.team_href
  left join csgo.current_team_lineups as tl2
    on
      tl.lineup_id = tl2.lineup_id
      and tl.match_href = tl2.match_href
  left join csgo.match_lineups as ctl
    on
      dr.match_href = ctl.match_href
      and dr.ct_href = ctl.team_href
  left join csgo.current_team_lineups as ctl2
    on
      ctl.lineup_id = ctl2.lineup_id
      and ctl.match_href = ctl2.match_href
where 
  di.map_name is not null
  and dr.round <= 30
order by
  mi.datetime_utc
  ,dr.match_href
  ,dr.map_num
  ,dr.round
--limit 100                           
;")

round_data = fetch(round_query,n=-1)

ignore_rds = c(1,2,3,4,14,15)
ignore_list = c(-1, ignore_rds, ignore_rds + 15)
econ_by_rd = round_data[!(round_data$round %in% ignore_list),c('round','ct_econ_adv')]

phase_round = factor(ifelse(econ_by_rd$round > 15, econ_by_rd$round - 15, econ_by_rd$round))

sm.density.compare(econ_by_rd$ct_econ_adv,phase_round, xlab="ct econ adv")

colfill<-c(2:(2+length(levels(phase_round)))) 
legend(0.75*par('usr')[2],0.95*par('usr')[4], levels(phase_round), fill=colfill)



plot(density(round_data[!is.na(round_data$ct_reward_diff),'ct_reward_diff']))

unique(round_data$ct_reward_diff)

nrow()

nrow(round_data[which((round_data$ct_econ_adv > 29000) | (round_data$ct_econ_adv < -29000)),])
nrow(round_data[round_data$round != -1,])

unique(round_data[(round_data$ct_econ_adv > 29000) | (round_data$ct_econ_adv < -29000),'match_href'])

round_data[is.na(round_data$match_href),]

hist(sample(round_data[(round_data$round %in% c(2,17)),'ct_econ_adv'],4000))

