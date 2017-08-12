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
  ,rr.match_href
  ,rr.map_num
  ,rr.map_name
  ,rr.pseudo_rd
  ,rr.team1_href
  ,l1.lineup_id as team1_lineup
  ,rr.team1_side
  ,tr1.rank as team1_rank
  ,rr.team2_href
  ,l2.lineup_id as team2_lineup
  ,rr.team2_side
  ,tr2.rank as team2_rank
  ,rr.result as round_result
  ,mre.result as map_result
from csgo.hltv_round_results as rr
  left join csgo.hltv_match_info as mi
    on rr.match_href = mi.match_href
  left join csgo.hltv_events as e
    on mi.event_href = e.event_href
  left join csgo.hltv_team_ranks as tr1
    on
      e.hltv_rank_dt = tr1.date_
      and rr.team1_href = tr1.team_href
  left join csgo.hltv_team_ranks as tr2
    on
      e.hltv_rank_dt = tr2.date_
      and rr.team2_href = tr2.team_href
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
--where rr.map_name = 'Mirage'
order by
  mi.datetime_utc
  ,rr.match_href
  ,rr.map_num
  ,rr.pseudo_rd
;")

round_data = fetch(round_query,n=-1)

# round_data$ct_team = ifelse(round_data$team1_side == 'ct', round_data$team1_lineup, round_data$team2_lineup)
# round_data$t_team = ifelse(round_data$team1_side == 't', round_data$team1_lineup,round_data$team2_lineup)
round_data$ct_win = ifelse(round_data$team1_side == 'ct', round_data$round_result, ifelse(round_data$round_result == 1,0,1))

round_data$ct_team = ifelse(round_data$team1_side == 'ct', paste(round_data$team1_lineup, round_data$season, sep = '_'),
                            paste(round_data$team2_lineup, round_data$season, sep = '_'))
round_data$t_team = ifelse(round_data$team1_side == 't', paste(round_data$team1_lineup, round_data$season, sep = '_'),
                           paste(round_data$team2_lineup, round_data$season, sep = '_'))

attach(round_data)

ct_win = as.factor(ct_win)
season = as.factor(season)
ct_team = as.factor(ct_team)
t_team = as.factor(t_team)
match_href = as.factor(match_href)
event_href = as.factor(event_href)

full_formula = ct_win ~ (1|ct_team) + (1|t_team) + (1|match_href) + (1|event_href)
abg_formula = ct_win ~ (1|ct_team) + (1|t_team)

map_side_est = data.frame()
for (map in unique(round_data$map_name)){
  model = glmer(full_formula, data = round_data[round_data$map_name == map,], family = binomial, verbose = 2)
  ct_val = 3
  
  relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
  
  if (max(abs(relgrad)) > 0.001){
    model = glmer(abg_formula, data = round_data[round_data$map_name == map,], family = binomial, verbose = 2)
    relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
    ct_val = 1
  }
  
  if (max(abs(relgrad)) < 0.001){
    eff <- ranef(model, condVar=TRUE)
    
    t = eff$t_team
    t$map_name = map
    t$side = 't'
    t$team = rownames(t)
    t$var = sqrt(attr(eff[[2]], "postVar")[1, 1, ])
    t = merge(t, data.frame(table(round_data$t_team[round_data$map_name == map])), by.x = 'team', by.y = 'Var1', all.x = T)
    colnames(t)[c(2,6)] <- c("int","rounds")
    t$int_std = scale(-1*t$int, center = T, scale = T)
    
    ct = eff$ct_team
    ct$map_name = map
    ct$side = 'ct'
    ct$team = rownames(ct)
    ct$var = sqrt(attr(eff[[ct_val]], "postVar")[1, 1, ])
    ct = merge(ct, data.frame(table(round_data$ct_team[round_data$map_name == map])), by.x = 'team', by.y = 'Var1', all.x = T)
    colnames(ct)[c(2,6)] <- c("int","rounds")
    ct$int_std = scale(ct$int, center = T, scale = T)
    
    map_side_est = rbind(map_side_est,rbind(ct,t))
  }
  
}

# map_side_est %>% group_by(team, map_name) %>% summarise(rounds = sum(rounds))


team_agg = ddply(map_side_est,c("team","map_name"),function(X) data.frame(int_std=weighted.mean(X$int_std, X$rounds), rounds=sum(X$rounds)))
head(team_agg[order(team_agg$int_std, decreasing = T),])

team_agg2 = ddply(team_agg,"team",function(X) data.frame(int_std=weighted.mean(X$int_std, X$rounds), rounds=sum(X$rounds)))
team_agg2 = team_agg2[team_agg2$rounds > 500,]
head(team_agg2[order(team_agg2$int_std, decreasing = T),],20)



team_agg[team_agg$team == '/player/2023/FalleN/player/557/fnx/player/8564/fer/player/9216/coldzera/player/9217/TACO_2016',]

map_side_est[map_side_est$team == '/player/10004/enanoks/player/10554/nmt/player/322/FlipiN/player/4373/EasTor/player/9328/Blastinho_2016',]