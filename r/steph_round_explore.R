# sink("diagnostics/steph.txt")

library(RPostgreSQL)
library(dplyr)
library(PlayerRatings)
library(ggplot2)
library(caret)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

round_query <- dbSendQuery(con, "
select distinct
  mi.event_href
  ,mi.datetime_utc
  ,mro.match_href
  --,mro.map_num
  ,mro.map_name
  --,mro.half
  --,mro.pseudo_rd
  ,mro.team1_href
  ,l1.lineup_id as team1_lineup
  ,mro.team1_side
  ,mro.team2_href
  ,l2.lineup_id as team2_lineup
  ,mro.team2_side
  ,mro.result as round_result
  ,mre.result as map_result
from csgo.hltv_map_rounds as mro
  left join csgo.hltv_match_info as mi
    on mro.match_href = mi.match_href
  left join csgo.lineups as l1
    on
      mro.match_href = l1.match_href
      and mro.team1_href = l1.team_href
  left join csgo.lineups as l2
    on
      mro.match_href = l2.match_href
      and mro.team2_href = l2.team_href
  left join csgo.hltv_map_results as mre
    on mro.match_href = mre.match_href
where mro.map_name != 'Season'
order by
  mi.datetime_utc
  --,mro.map_num
  --,mro.half
  --,mro.pseudo_rd
;")

round_data <- fetch(round_query,n=-1)

attach(round_data)

round_data$team1_lineup_side = paste(round_data$team1_lineup, round_data$team1_side, sep = '/')
round_data$team2_lineup_side = paste(round_data$team2_lineup, round_data$team2_side, sep = '/')