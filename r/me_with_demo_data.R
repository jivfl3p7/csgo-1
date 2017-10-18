library(RPostgreSQL)
library(lme4)
library(plyr)
library(dplyr)

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

hist(sample(round_data[(round_data$round %in% c(2,15)),'ct_econ_adv'],2500))
max(round_data[(round_data$round %in% c(2,15)),'ct_econ_adv'])

unique(round_data[is.na(round_data$ct_econ_adv) & (round_data$round != -1),'match_href'])

hist(sample(round_data[!(round_data$round %in% c(-1,1,2,15,16)),'ct_econ_adv'],10000))
hist(sample(round_data[!(round_data$round %in% c(-1,1,2,3,15,16,17)),'ct_econ_adv'],10000))
hist(sample(round_data[!(round_data$round %in% c(-1,1,2,3,4,15,16,17,18)),'ct_econ_adv'],10000))
