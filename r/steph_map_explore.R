# sink("diagnostics/steph.txt")

library(RPostgreSQL)
library(dplyr)
library(PlayerRatings)
library(ggplot2)
library(zoo)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

map_query <- dbSendQuery(con, "
select distinct
  left(mi.datetime_utc::varchar,4)::int as season
	,mi.event_href
  ,mi.datetime_utc
  ,mr.match_href
  ,rank() over (partition by date_part('y', mi.datetime_utc), map_name order by mi.datetime_utc ,mr.match_href, mr.map_num) as map_round
  ,rank() over (partition by date_part('y', mi.datetime_utc) order by mi.datetime_utc ,mr.match_href, mr.map_num) as round
  ,mr.map_num
  ,mr.map_name
  ,mr.team1_href
  ,l1.lineup_id as team1_lineup
  ,mr.team2_href
  ,l2.lineup_id as team2_lineup
  ,mr.result as map_result
from csgo.hltv_map_results as mr
  left join csgo.hltv_match_info as mi
    on mr.match_href = mi.match_href
  left join csgo.lineups as l1
    on
      mr.match_href = l1.match_href
      and mr.team1_href = l1.team_href
  left join csgo.lineups as l2
    on
      mr.match_href = l2.match_href
      and mr.team2_href = l2.team_href
where mr.map_name != 'Season'
order by
  mi.datetime_utc
  ,mr.match_href
  ,mr.map_num
;")

map_data <- fetch(map_query,n=-1)

attach(map_data)

min_rounds = 50
min_games = 4

for (year in sort(unique(season))){
  for (match in sort(unique(round[(season == year) & (round >= min_rounds)]))){
    sobj = steph(map_data[(season == year) & (round < match),c('round','team1_lineup','team2_lineup','map_result')])
    pval = predict(sobj, map_data[(season == year) & (round == match),c('round','team1_lineup','team2_lineup')], tng = min_games)
    map_data$pred[(season == year) & (round == match)] = pval
  }
  for (map in unique(map_name[season == year])){
    for (match in sort(unique(map_round[(season == year) & (map_name == map) & (map_round >= min_rounds)]))){
      map_sobj = steph(map_data[(season == year) & (map_name == map) & (map_round < match),c('map_round','team1_lineup','team2_lineup','map_result')])
      map_pval = predict(map_sobj, map_data[(season == year) & (map_name == map) & (map_round == match),c('map_round','team1_lineup','team2_lineup')], tng = min_games)
      map_data$pred_map[(season == year) & (map_name == map) & (map_round == match)] = map_pval
    }
  }
}

map_data$logloss = -1*(map_result*log(map_data$pred) + (1 - map_result)*log(1 - map_data$pred))
# mean(map_data$logloss[!is.na(map_data$logloss)])
# 0.6877750
# 0.6814298 (separate rounds by map_num)

# mean(map_data$logloss[!is.na(map_data$logloss) & (map_data$season < 2017)])
# 0.6857275
# 0.6754574 (separate rounds by map_num)

# mean(map_data$logloss[!is.na(map_data$logloss) & (map_data$season == 2017)])
# 0.6912126
# 0.6915963 (separate rounds by map_num)

map_data$map_logloss = -1*(map_result*log(map_data$pred_map) + (1 - map_result)*log(1 - map_data$pred_map))
# mean(map_data$map_logloss[!is.na(map_data$map_logloss)])
# 0.7366806

# mean(map_data$map_logloss[!is.na(map_data$map_logloss) & (map_data$season < 2017)])
# 0.724874

# mean(map_data$map_logloss[!is.na(map_data$map_logloss) & (map_data$season == 2017)])
# 0.7510301


map_data$ideal_logloss = ifelse(map_data$map_logloss < map_data$logloss, map_data$map_logloss, ifelse(map_data$map_logloss > map_data$logloss, map_data$logloss, NA))
# mean(map_data$ideal_logloss[!is.na(map_data$ideal_logloss)])
# 0.5641692
# 0.5673787 (separate rounds by map_num)

# mean(map_data$ideal_logloss[!is.na(map_data$ideal_logloss) & (map_data$season < 2017)])
# 0.5532937
# 0.5582638 (separate rounds by map_num)

map_data$rate_type = ifelse(map_data$map_logloss < map_data$logloss, 1, ifelse(map_data$map_logloss > map_data$logloss, 0, NA))
# mean(map_data$rate_type[!is.na(map_data$rate_type)])




map_data$map_logloss_diff = map_data$map_logloss - map_data$logloss

aggregate(map_logloss_diff ~ season + map_name, data = map_data[!is.na(map_data$map_logloss_diff) & (map_data$season < 2017),], FUN = mean)
mean(map_data$map_logloss_diff[!is.na(map_data$map_logloss_diff) & (map_data$season < 2017)])

plot_data = map_data[!is.na(map_data$map_logloss),c('season','logloss','map_logloss')]
plot_data$x <- data.frame(plot_data$season,count=ave(plot_data$season==plot_data$season, plot_data$season, FUN=cumsum))[,2]
plot_data$roll10 = ave(plot_data$logloss, plot_data$season,FUN= function(x) rollmean(x, k=10, na.pad=T))
plot_data$map_roll10 = ave(plot_data$map_logloss, plot_data$season,FUN= function(x) rollmean(x, k=10, na.pad=T))


ggplot(plot_data, aes(x)) + geom_line(aes(y = roll10, colour = as.factor(season))) + ylim(0,1)
ggplot(plot_data, aes(x)) + geom_line(aes(y = map_roll10, colour = as.factor(season))) + ylim(0,1)




