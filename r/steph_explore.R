# sink("diagnostics/steph.txt")

library(RPostgreSQL)
library(dplyr)
library(PlayerRatings)
library(ggplot2)
library(caret)


drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

query <- dbSendQuery(con, "
  select distinct
    left(m.datetime_utc::varchar,4)::int as year,
    date_part('doy', m.datetime_utc) as round,
    m.datetime_utc,
    m.event_href,
    r.match_href,
    r.map_name,
    r.team1_href,
    ls1.lineup_id as lineup1_id,
    ls1.win_prev_events as lineup1_win_prev_events, 
    ls1.prev_winnings as lineup1_prev_winnings,
    ls1.pt_prev_events as lineup1_pt_prev_events,
    ls1.prev_points as lineup1_prev_points,
    r.team2_href,
    ls2.lineup_id as lineup2_id,
    ls2.win_prev_events as lineup2_win_prev_events, 
    ls2.prev_winnings as lineup2_prev_winnings,
    ls2.pt_prev_events as lineup2_pt_prev_events,
    ls2.prev_points as lineup2_prev_points,
    r.result,
    r.abs_result
  from csgo.hltv_map_results as r
    left join csgo.hltv_match_info as m
      on r.match_href = m.match_href
    left join csgo.lineup_init_stats as ls1
      on r.match_href = ls1.match_href
      and r.map_name = ls1.map_name
      and r.team1_href = ls1.team_href
    left join csgo.lineup_init_stats as ls2
      on r.match_href = ls2.match_href
      and r.map_name = ls2.map_name
      and r.team2_href = ls2.team_href
  where r.map_name != 'Season'
  order by m.datetime_utc
  ;")

all_data <- fetch(query,n=-1)

attach(all_data)

all_data <- all_data[order(all_data$datetime_utc),]
# head(all_data)
# 
# head(all_data[is.na(all_data)])
# head(which(is.na(all_data), arr.ind=TRUE)) check for missing


ratings = data.frame()
init_data = data.frame()
for (season in sort(unique(all_data$year))){
  for (map in unique(all_data$map_name[all_data$year == season])){
    for (day in sort(unique(all_data$round[(all_data$year == season) & (all_data$map_name == map)]))[-1]){
      sub_data = all_data[(all_data$map_name == map) & (all_data$year == season) & (all_data$round < day),]
      
      sobj <- steph(sub_data[,c('round','lineup1_id','lineup2_id','result')])
      sobj$ratings$year = season
      sobj$ratings$map_name = map
      
      if (day == max(all_data$round[(all_data$map_name == map) & (all_data$year == season)])){
        sobj$ratings$round = (day + 1)
      } else {
        next_rd = min(all_data$round[(all_data$map_name == map) & (all_data$year == season) & (all_data$round > day)])
        sobj$ratings$round = next_rd
        matches = all_data[(all_data$map_name == map) & (all_data$year == season) & (all_data$round == next_rd),c('year','round','lineup1_id','lineup1_win_prev_events','lineup1_prev_winnings','lineup1_pt_prev_events','lineup1_prev_points','lineup2_id','lineup2_win_prev_events','lineup2_prev_winnings','lineup2_pt_prev_events','lineup2_prev_points','result')]
        matches = merge(matches, sobj$ratings[,c('year','round','map_name','Player','Rating','Deviation')], by.x = c('year','round','lineup1_id'), by.y = c('year','round','Player'), all.x = T)
        matches = merge(matches, sobj$ratings[,c('year','round','map_name','Player','Rating','Deviation')], by.x = c('year','round','lineup2_id'), by.y = c('year','round','Player'), all.x = T)
      }

      init_data = rbind(init_data,matches)
    }
  }
}

init_data1 = init_data[!is.na(init_data$Rating.x),c('year','round','map_name.x','lineup1_id','lineup1_win_prev_events','lineup1_prev_winnings','lineup1_pt_prev_events','lineup1_prev_points', 'Rating.x','Deviation.x')] %>% rename(lineup_id = lineup1_id, lineup_win_prev_events = lineup1_win_prev_events, lineup_prev_winnings = lineup1_prev_winnings, lineup_pt_prev_events = lineup1_pt_prev_events, lineup_prev_points = lineup1_prev_points, map_name = map_name.x, Rating = Rating.x, Deviation = Deviation.x)
init_data2 = init_data[!is.na(init_data$Rating.y),c('year','round','map_name.y','lineup2_id','lineup2_win_prev_events','lineup2_prev_winnings','lineup2_pt_prev_events','lineup2_prev_points', 'Rating.y','Deviation.y')] %>% rename(lineup_id = lineup2_id, lineup_win_prev_events = lineup2_win_prev_events, lineup_prev_winnings = lineup2_prev_winnings, lineup_pt_prev_events = lineup2_pt_prev_events, lineup_prev_points = lineup2_prev_points, map_name = map_name.y, Rating = Rating.y, Deviation = Deviation.y)

init_data_comb = rbind(init_data1,init_data2)

data = init_data_comb[init_data_comb$year > 2015,]

set.seed(157)
inTrain <- createDataPartition(y = data$Rating, p = .65, list = F)
training <- data[ inTrain,]
testing <- data[-inTrain,]

my_control <- trainControl(
  method = "boot632",
  number = 25,
  savePredictions = "final",
  index = createResample(training$Rating, 25)
)

rat.fit = train(x = training[,-c(1:2,4,9:10)], y = training[,'Rating'], method = 'lmStepAIC', trControl = my_control)

inTrain <- createDataPartition(y = data$Deviation, p = .65, list = F)
training <- data[ inTrain,]
testing <- data[-inTrain,]

my_control <- trainControl(
  method = "boot632",
  number = 25,
  savePredictions = "final",
  index = createResample(training$Deviation, 25)
)
dev.fit = train(x = training[,-c(1:2,4,9:10)], y = training[,'Deviation'], method = 'lmStepAIC', trControl = my_control)

# init_data_comb$pred_Rat = predict(rat.fit$finalModel, newdata = init_data_comb)
# init_data_comb$pred_Dev = predict(dev.fit$finalModel, newdata = init_data_comb)


steph_arch = data.frame()
for (season in sort(unique(all_data$year))[-1]){
  for (map in unique(data$map_name[data$year == season])){
    if (exists("steph_status") == T){
      rm(steph_status)
    }
    for (day in sort(unique(all_data$round[(all_data$year == season) & (all_data$map_name == map)]))[-1]){
      sub_data = all_data[(all_data$map_name == map) & (all_data$year == season) & (all_data$round == day),]
      
      if (exists('l1') == T){
        rm(l1)
      }
      
      if (exists('l2') == T){
        rm(l2)
      }
      
      if (exists('new_lineups') == T){
        rm(new_lineups)
      }
      
      if (exists('steph_status') == T){
        for (lineup1 in unique(sub_data$lineup1_id)){
          if (!(lineup1 %in% unique(steph_status$Player))){
            l1 = sub_data[!(sub_data$lineup1_id %in% unique(steph_status$Player)),c('year','round','map_name','lineup1_id','lineup1_win_prev_events','lineup1_prev_winnings','lineup1_pt_prev_events','lineup1_prev_points')] %>% rename(lineup_id = lineup1_id, lineup_win_prev_events = lineup1_win_prev_events, lineup_prev_winnings = lineup1_prev_winnings, lineup_pt_prev_events = lineup1_pt_prev_events, lineup_prev_points = lineup1_prev_points)
            l1$Rating = predict(rat.fit, newdata = l1)
            l1$Deviation = predict(dev.fit, newdata = l1)
            new_lineups = l1[,c('year','round','map_name','lineup_id','Rating','Deviation')]
          }
          break
        }
        
        for (lineup2 in unique(sub_data$lineup2_id)){
          if (!(lineup2 %in% unique(steph_status$Player))){
            l2 = sub_data[!(sub_data$lineup2_id %in% unique(steph_status$Player)),c('year','round','map_name','lineup2_id','lineup2_win_prev_events','lineup2_prev_winnings','lineup2_pt_prev_events','lineup2_prev_points')] %>% rename(lineup_id = lineup2_id, lineup_win_prev_events = lineup2_win_prev_events, lineup_prev_winnings = lineup2_prev_winnings, lineup_pt_prev_events = lineup2_pt_prev_events, lineup_prev_points = lineup2_prev_points)
            l2$Rating = predict(rat.fit, newdata = l2)
            l2$Deviation = predict(dev.fit, newdata = l2)
            l2 = l2[,c('year','round','map_name','lineup_id','Rating','Deviation')]
            if (exists('new_lineups') == T){
              new_lineups = rbind(new_lineups,l2)
            } else {
              new_lineups = l2[,c('year','round','map_name','lineup_id','Rating','Deviation')]
            }
          }
          break
        }
      } else {
        l1 = sub_data[,c('year','round','map_name','lineup1_id','lineup1_win_prev_events','lineup1_prev_winnings','lineup1_pt_prev_events','lineup1_prev_points')] %>% rename(lineup_id = lineup1_id, lineup_win_prev_events = lineup1_win_prev_events, lineup_prev_winnings = lineup1_prev_winnings, lineup_pt_prev_events = lineup1_pt_prev_events, lineup_prev_points = lineup1_prev_points)
        l2 = sub_data[,c('year','round','map_name','lineup2_id','lineup2_win_prev_events','lineup2_prev_winnings','lineup2_pt_prev_events','lineup2_prev_points')] %>% rename(lineup_id = lineup2_id, lineup_win_prev_events = lineup2_win_prev_events, lineup_prev_winnings = lineup2_prev_winnings, lineup_pt_prev_events = lineup2_pt_prev_events, lineup_prev_points = lineup2_prev_points)
        new_lineups = rbind(l1,l2)
        new_lineups$Rating = predict(rat.fit, newdata = new_lineups)
        new_lineups$Deviation = predict(dev.fit, newdata = new_lineups)
        new_lineups = new_lineups[,c('year','round','map_name','lineup_id','Rating','Deviation')]
      }
      
      if (exists('new_lineups') == T){
        new_lineups = new_lineups %>% rename(Player = lineup_id)
        new_lineups$Games = 0
        new_lineups$Win = 0
        new_lineups$Draw = 0
        new_lineups$Loss = 0
        new_lineups$Lag = 0
        if (exists('steph_status') == T){
          steph_status = rbind(steph_status, new_lineups)
        } else {
          steph_status = new_lineups
        }
      }
      
      sobj <- steph(x = sub_data[,c('round','lineup1_id','lineup2_id','result')], status = steph_status)
      sobj$ratings$year = season
      sobj$ratings$map_name = map
      
      if (day == max(all_data$round[(all_data$map_name == map) & (all_data$year == season)])){
        sobj$ratings$round = (day + 1)
      } else {
        sobj$ratings$round = min(all_data$round[(all_data$map_name == map) & (all_data$year == season) & (all_data$round > day)])
      }
      
      steph_status = sobj$ratings
      
      if (exists('steph_arch') == T){
        steph_arch = rbind(steph_arch,steph_status)
      } else {
        steph_arch = steph_status
      }
    }
  }
}

steph_arch[(steph_arch$map_name == 'Cache') & (steph_arch$year == 2017) & (steph_arch$round == max(steph_arch$round[(steph_arch$map_name == 'Cache') & (steph_arch$year == 2017)])),]



head(all_data)
head(data)
head(steph_arch)

eval = merge(all_data[,c('year','round','map_name','lineup1_id','lineup2_id','abs_result')], data[,c('year','round','map_name','lineup_id','Rating')], by.x = c('year','round','map_name','lineup1_id'), by.y = c('year','round','map_name','lineup_id')) %>% rename(Rating1_old = Rating)
eval = merge(eval, data[,c('year','round','map_name','lineup_id','Rating')], by.x = c('year','round','map_name','lineup2_id'), by.y = c('year','round','map_name','lineup_id')) %>% rename(Rating2_old = Rating)

eval = merge(eval, steph_arch[,c('year','round','map_name','Player','Rating')], by.x = c('year','round','map_name','lineup1_id'), by.y = c('year','round','map_name','Player')) %>% rename(Rating1_new = Rating)
eval = merge(eval, steph_arch[,c('year','round','map_name','Player','Rating')], by.x = c('year','round','map_name','lineup2_id'), by.y = c('year','round','map_name','Player')) %>% rename(Rating2_new = Rating)

eval$old_pred = ifelse(eval$Rating1_old > eval$Rating2_old, 1, 0)
eval$old_corr = ifelse(eval$old_pred == eval$abs_result, 1, 0)

eval$new_pred = ifelse(eval$Rating1_new > eval$Rating2_new, 1, 0)
eval$new_corr = ifelse(eval$new_pred == eval$abs_result, 1, 0)

sum(eval$old_pred)/nrow(eval)
sum(eval$new_pred)/nrow(eval)



ratings = data.frame()
logloss_calc = data.frame()
for (yr in unique(all_data$year)){
  for (wk in sort(unique(all_data$week[all_data$year == yr]))[-1]){
    sub_data = all_data[(all_data$year == yr) & (all_data$week <= wk),]
    
    train = sub_data[sub_data$week < wk,c('week','team1_href','team2_href','result')]
    train_adv = sub_data$map_pick[sub_data$week < wk]
    test = sub_data[sub_data$week == wk,c('week','team1_href','team2_href','result')]
    test_adv = sub_data$map_pick[sub_data$week == wk]
    
    robj <- steph(train, gamma = train_adv)
    robj$ratings$season = yr
    robj$ratings$week = wk
    
    pvals <- predict(robj, test, tng = 5, gamma = test_adv)
    
    if (sum(!is.na(pvals)) > 0){
      results = test[which(!is.na(pvals)),]
      results$pvals = pvals[which(!is.na(pvals))]
      results$season = yr
      logloss_calc <- rbind(logloss_calc,results)
    }
    
    ratings <- rbind(ratings,robj$ratings[robj$ratings$Games >= 5,])
  }
}

ratings[(ratings$season == 2017) & (ratings$week == max(ratings$week[ratings$season == 2017])),]



ratings = data.frame()
logloss_calc = data.frame()
for (yr in unique(all_data$year)){
  for (map_nm in unique(all_data$map_name[all_data$year == yr])){
    for (wk in sort(unique(all_data$week[(all_data$year == yr) & (all_data$map_name == map_nm)]))[-1]){
      sub_data = all_data[(all_data$year == yr) & (all_data$map_name == map_nm) & (all_data$week <= wk),]
      
      train = sub_data[sub_data$week < wk,c('week','team1_href','team2_href','result')]
      train_adv = sub_data$map_pick[sub_data$week < wk]
      test = sub_data[sub_data$week == wk,c('week','team1_href','team2_href','result')]
      test_adv = sub_data$map_pick[sub_data$week == wk]
      
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