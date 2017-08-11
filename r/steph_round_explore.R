# sink("diagnostics/steph.txt")

library(RPostgreSQL)
library(dplyr)
library(PlayerRatings)
library(ggplot2)
# library(caret)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

round_query <- dbSendQuery(con, "
select distinct
  left(mi.datetime_utc::varchar,4)::int as season
  ,mi.event_href
  ,mi.datetime_utc
  ,rr.match_href
  ,rr.map_num
  ,rr.map_name
  ,rr.pseudo_rd
  ,rank() over (
    partition by date_part('y', mi.datetime_utc)
    order by
      mi.datetime_utc
      ,rr.match_href
      ,rr.map_num
      ,rr.pseudo_rd
    ) as overall_round
  ,rank() over (
    partition by
      date_part('y', mi.datetime_utc)
      ,rr.map_name
    order by
      mi.datetime_utc
      ,rr.match_href
      ,rr.map_num
      ,rr.pseudo_rd
    ) as map_round
  ,overall_match
  ,map_match
  ,rr.team1_href
  ,l1.lineup_id as team1_lineup
  ,rr.team1_side
  ,rr.team2_href
  ,l2.lineup_id as team2_lineup
  ,rr.team2_side
  ,rr.result as round_result
  ,mre.result as map_result
from csgo.hltv_round_results as rr
  left join csgo.hltv_match_info as mi
    on rr.match_href = mi.match_href
  left join (
    select distinct
    mi.datetime_utc
    ,mr.match_href
    ,mr.map_num
    ,mr.map_name
    ,rank() over (
      partition by date_part('y', mi.datetime_utc)
      order by
        mi.datetime_utc
        ,mr.match_href
        ,mr.map_num
      ) as overall_match
    ,rank() over (
      partition by
        date_part('y', mi.datetime_utc)
        , map_name
      order by
        mi.datetime_utc
        ,mr.match_href
        ,mr.map_num
      ) as map_match
    from csgo.hltv_map_results as mr
    left join csgo.hltv_match_info as mi
    on mr.match_href = mi.match_href
    where mr.map_name != 'Season'
    order by
    mi.datetime_utc
    ,mr.match_href
    ,mr.map_num
    ) as mc
    on
      rr.match_href = mc.match_href
      and rr.map_num = mc.map_num
  left join csgo.lineups as l1
    on
      rr.match_href = l1.match_href
      and rr.team1_href = l1.team_href
  left join csgo.lineups as l2
    on
      rr.match_href = l2.match_href
      and rr.team2_href = l2.team_href
  left join csgo.hltv_map_results as mre
    on 
      rr.match_href = mre.match_href
      and rr.map_num = mre.map_num
where rr.map_name != 'Season'
order by
  mi.datetime_utc
  ,rr.match_href
  ,rr.map_num
  ,rr.pseudo_rd
;")

round_data <- fetch(round_query,n=-1)

map_data = unique(round_data[,!names(round_data) %in% c('pseudo_rd','round','map_round','team1_side','team2_side','round_result')])

round_data$team1_lineup_side = paste(round_data$team1_lineup, round_data$team1_side, sep = '/')
round_data$team2_lineup_side = paste(round_data$team2_lineup, round_data$team2_side, sep = '/')

min_matches = 50
min_games = 5


for (year in sort(unique(map_data$season))){
  
  # map
  for (match in sort(unique(map_data$overall_match[(map_data$season == year) & (map_data$overall_match >= min_matches)]))){
    sobj = steph(map_data[(map_data$season == year) & (map_data$overall_match < match),
                          c('round','team1_lineup','team2_lineup','map_result')])
    pval = predict(sobj, map_data[(map_data$season == year) & (map_data$overall_match == match),
                                  c('round','team1_lineup','team2_lineup')], tng = min_games)
    map_data$pred[(map_data$season == year) & (map_data$overall_match == match)] = pval
  }
  
  
  for (map in unique(map_data$map_name[map_data$season == year])){
    for (match in sort(unique(map_data$map_match[(map_data$season == year) & (map_data$map_name == map)
                                                 & (map_data$map_match >= min_rounds)]))){
      map_sobj = steph(map_data[(map_data$season == year) & (map_data$map_name == map) & (map_data$map_match < match),
                                c('map_match','team1_lineup','team2_lineup','map_result')])
      map_pval = predict(map_sobj, map_data[(map_data$season == year) & (map_data$map_name == map) & (map_data$map_match == match),
                                            c('map_match','team1_lineup','team2_lineup')], tng = min_games)
      map_data$pred_map[(map_data$season == year) & (map_data$map_name == map) & (map_data$map_match == match)] = map_pval
    }
  }
  
  
}


