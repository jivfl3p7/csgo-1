# sink("diagnostics/steph.txt")

library('RPostgreSQL')
library('dplyr')
library('PlayerRatings')

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

query <- dbSendQuery(con, "
  SELECT DISTINCT
    left(m.datetime_utc::varchar,4)::int as year,
    m.event_href,
    r.match_href,
    CASE
      WHEN date_part('dow', m.datetime_utc) > 1 THEN date_part('week', m.datetime_utc)
      ELSE date_part('week', m.datetime_utc) - 1
    END AS week,
    r.map_name,
    r.team1_href,
    m.team1_name,
    r.team2_href,
    m.team2_name,
    --v.team_name as team_map_pick,
    CASE
      WHEN v.team_name IS NULL THEN 0
      WHEN lower(v.team_name) = lower(m.team1_name) THEN 1
      WHEN lower(v.team_name) = lower(m.team2_name) THEN -1
      ELSE 999
    END AS map_pick,
    r.result,
    r.abs_result
  FROM csgo.hltv_map_results as r
    LEFT JOIN csgo.hltv_match_info as m
      ON r.match_href = m.match_href
    LEFT JOIN csgo.hltv_vetos as v
      ON r.match_href = v.match_href
      AND left(lower(r.map_name),4) = left(lower(v.map),4)
  --LIMIT 100
  ;")

all_data <- fetch(query,n=-1)

attach(all_data)

head(all_data)


# map_data = all_data[(all_data$year == 2017) & (all_data$map_name == 'Cache'),]
# 
# train = map_data[map_data$week < 18,c('week','team1_href','team2_href','result')]
# test = map_data[map_data$week == 18,c('week','team1_href','team2_href','result')]
# train_adv = map_data$map_pick[map_data$week < 18]
# test_adv = map_data$map_pick[map_data$week == 18]
# 
# robj <- steph(train, gamma = train_adv)
# 
# pvals <- predict(robj, test, tng = 3, gamma = test_adv)
# 
# test$result
# pvals

ratings = data.frame()
logloss_calc = data.frame()
for (yr in unique(all_data$year)){
  for (map_nm in unique(all_data$map_name[all_data$year == yr])){
    for (wk in sort(unique(all_data$week[(all_data$year == yr) & (all_data$map_name == map_nm)]))[-1]){
      map_data = all_data[(all_data$year == yr) & (all_data$map_name == map_nm) & (all_data$week <= wk),]
      
      train = map_data[map_data$week < wk,c('week','team1_href','team2_href','result')]
      train_adv = map_data$map_pick[map_data$week < wk]
      test = map_data[map_data$week == wk,c('week','team1_href','team2_href','result')]
      test_adv = map_data$map_pick[map_data$week == wk]
      
      robj <- steph(train, gamma = train_adv)
      robj$ratings$season = yr
      robj$ratings$week = wk
      robj$ratings$map_name = map_nm
      
      pvals <- predict(robj, test, tng = 5, gamma = test_adv)
      
      if (sum(!is.na(pvals)) > 0){
        results = test[which(!is.na(pvals)),]
        results$pvals = pvals[which(!is.na(pvals))]
        results$season = yr
        results$map_name = map_nm
        logloss_calc <- rbind(logloss_calc,results)
      }
      
      ratings <- rbind(ratings,robj$ratings[robj$ratings$Games >= 5,])
    }
  }
}



test = logloss_calc[(logloss_calc$season == 2017) & (logloss_calc$map_name == 'Mirage'),]
test$logloss = -1*(test$result*log(test$pvals) + (1 - test$result)*log(1 - test$pvals))
test$agg_ll = cummean(test$logloss)



(data$win*log(w)+(1-data$win)*log(1-w))

ratings[(ratings$season == 2017) & (ratings$map_name == 'Mirage'),]




names(ratings)[names(ratings) == 'Player'] <- 'team_href'


dbWriteTable(con,c('csgo','steph_ratings'),ratings, row.names = F, overwrite = T)