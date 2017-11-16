library(RPostgreSQL)
library(lme4)
library(plyr)
library(dplyr)
library(sm)
library(stringr)

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
  ,tl3.active as t_active
  ,dr.ct_href
  ,ctl2.team_name||'_'||(ctl2.rk)::text as ct_team
  ,ctl.lineup_id as ct_lineup
  ,ctl3.active as ct_active
  ,dr.ct_econ_adv as ct_econ_adv
  ,dr.ct_reward_diff
  ,dr.defuse as defuse_kits
  ,dr.plant
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
  left join csgo.hltv_active_teams as tl3
    on tl.team_href = tl3.team_href    
  left join csgo.match_lineups as ctl
    on
    dr.match_href = ctl.match_href
    and dr.ct_href = ctl.team_href
  left join csgo.current_team_lineups as ctl2
    on
    ctl.lineup_id = ctl2.lineup_id
    and ctl.match_href = ctl2.match_href
  left join csgo.hltv_active_teams as ctl3
    on ctl.team_href = ctl3.team_href
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

round_data$map_name = ifelse((round_data$map_name == 'de_inferno') & (round_data$datetime_utc <= '2016-08-28 14:30:00'),'de_inferno_o',round_data$map_name)
round_data$ct_win = ifelse(round_data$winner == 3,1,0)
round_data$ct_econ_group = ifelse(round(round_data$ct_econ_adv/5000) <= -4, -4, ifelse(round(round_data$ct_econ_adv/5000) >= 4, 4,round(round_data$ct_econ_adv/5000)))
round_data$rd_type = ifelse(round_data$round %in% c(1,2), round_data$round, 0)

active_teams = unique(c(str_sub(round_data[round_data$t_active == 1,'t_team'], end = -3),str_sub(round_data[round_data$ct_active == 1,'ct_team'], end = -3)))

attach(round_data)

ct_win = as.factor(ct_win)
season = as.factor(season)
ct_team = as.factor(ct_team)
t_team = as.factor(t_team)
match_href = as.factor(match_href)
event_href = as.factor(event_href)
ct_econ_group = as.factor(ct_econ_group)
map_name = as.factor(map_name)
rd_type = as.factor(rd_type)

rounds = list(c(1,16),c(2,17),c(c(3:15),c(18:30)))
round_types = c('pistol', 'rd2', 'main')
formula = ct_win ~ (1|ct_team) + (1|t_team) + (1|ct_econ_group)

glmer.function <- function(formula, temp_data, map, round_type){
  model = glmer(formula, data = temp_data, family = binomial, verbose = 0)
  
  relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
  if (max(abs(relgrad)) > 0.001){
    print('##### converge issue #####')
  }
  
  print(summary(model))
  eff <- ranef(model, condVar = T)
  
  t = eff$t_team
  t$team = rownames(t)
  t$var = sqrt(attr(eff$t_team, "postVar")[1, 1, ])
  t = merge(t, data.frame(table(temp_data$t_team)), by.x = 'team', by.y = 'Var1', all.x = T)
  colnames(t)[c(2:4)] <- c("t_int","t_var","t_rounds")
  
  ct = eff$ct_team
  ct$team = rownames(ct)
  ct$var = sqrt(attr(eff$ct_team, "postVar")[1, 1, ])
  ct = merge(ct, data.frame(table(temp_data$ct_team)), by.x = 'team', by.y = 'Var1', all.x = T)
  colnames(ct)[c(2:4)] <- c("ct_int","ct_var","ct_rounds")
  
  comb = merge(ct, t, by = 'team', all.x = T)
  comb$map_name = map
  comb$round_type = round_type
  
  int_val = data.frame(variable = rownames(coef(summary(model))), coef(summary(model)), row.names = NULL)
  int_val$map_name = map
  int_val$round_type = round_type
  
  return(list(comb,int_val))
}

team_str = data.frame()
fix_eff = data.frame()

for (map in c('all','knife',unique(round_data$map_name))){
  
  if (map == 'all'){
    temp_data = round_data[round != -1,]
    rtrn = glmer.function(update(formula, ~ . + (1|map_name:rd_type)), temp_data, NA, map)
    team_str = rbind(team_str,rtrn[[1]])
    fix_eff = rbind(fix_eff,rtrn[[2]])
  } else if (map == 'knife'){
    temp_data = round_data[round == -1,]
    rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group)), temp_data, NA, map)
    team_str = rbind(team_str,rtrn[[1]])
    fix_eff = rbind(fix_eff,rtrn[[2]])
  } else {
    for (i in c(1:3)){
      print(c(map, i))
      temp_data = round_data[(map_name == map) & (round %in% rounds[[i]]),]
      if (i == 1){
        rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group)), temp_data, map, round_types[i])
      } else {
        rtrn = glmer.function(formula, temp_data, map, round_types[i])
      }
      team_str = rbind(team_str,rtrn[[1]])
      fix_eff = rbind(fix_eff,rtrn[[2]])
    }
  }
}


team_str$ct_str = 


current_ct = team_str[(team_str$side == 'ct') & (team_str$round_type == 'all') & (str_sub(team_str$team, start = -2) == '_0') & (str_sub(team_str$team, end = -3) %in% active_teams),]
# current_ct$str = current_ct$int - current_ct$var
current_t = team_str[(team_str$side == 't') & (team_str$round_type == 'all') & (str_sub(team_str$team, start = -2) == '_0') & (str_sub(team_str$team, end = -3) %in% active_teams),]
# current_t$str = current_t$int + current_t$var

# head(current_ct[order(-current_ct$str),],25)
head(current_ct[order(-current_ct$int),],25)
# head(current_t[order(current_t$str),],25)
head(current_t[order(current_t$int),],25)


hist(team_str[team_str$side == 't','int'])
hist(team_str[team_str$side == 'ct','int'])



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
    
    
    t = eff$t_team
    t$map_name = map
    t$side = 't'
    t$team = rownames(t)
    t$var = sqrt(attr(eff[[2]], "postVar")[1, 1, ])
    t = merge(t, data.frame(table(round_data$t_team[round_data$map_name == map])), by.x = 'team', by.y = 'Var1', all.x = T)
    colnames(t)[c(2,6)] <- c("int","rounds")
    t$int = -1*t$int
    t$int_good = t$int + t$var
    t$int_bad = t$int - t$var
    
    ct = eff$ct_team
    ct$map_name = map
    ct$side = 'ct'
    ct$team = rownames(ct)
    ct$var = sqrt(attr(eff[[ct_val]], "postVar")[1, 1, ])
    ct = merge(ct, data.frame(table(round_data$ct_team[round_data$map_name == map])), by.x = 'team', by.y = 'Var1', all.x = T)
    colnames(ct)[c(2,6)] <- c("int","rounds")
    ct$int_good = ct$int + ct$var
    ct$int_bad = ct$int - ct$var
    
    map_side_est = rbind(map_side_est,rbind(ct,t))
  }
  
}