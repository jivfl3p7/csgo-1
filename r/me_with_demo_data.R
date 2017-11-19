library(RPostgreSQL)
library(lme4)

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
  ,case
  when v.team_href = dr.t_href then -1
  when v.team_href = dr.ct_href then 1
  when v.action_ = 'remain' then 0
  else 999
  end as pick
  ,dr.round
  ,dr.t_href
  ,tl2.team_name as t_team
  ,tl.lineup as t_lineup
  ,dr.ct_href
  ,ctl2.team_name as ct_team
  ,ctl.lineup as ct_lineup
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
  left join csgo.hltv_match_lineups as tl
    on
      dr.match_href = tl.match_href
      and dr.t_href = tl.team_href
  left join csgo.hltv_active_teams as tl2
    on tl.lineup = tl2.lineup
  left join csgo.hltv_match_lineups as ctl
    on
      dr.match_href = ctl.match_href
      and dr.ct_href = ctl.team_href
  left join csgo.hltv_active_teams as ctl2
    on ctl.lineup = ctl2.lineup
  left join csgo.hltv_vetos as v
    on
      dr.match_href = v.match_href
      and di.map_name = v.map_name
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

active_teams = unique(c(round_data[!is.na(round_data$t_team),'t_lineup'],round_data[!is.na(round_data$ct_team),'ct_lineup']))

attach(round_data)

ct_win = as.factor(ct_win)
season = as.factor(season)
ct_lineup = as.factor(ct_lineup)
t_lineup = as.factor(t_lineup)
match_href = as.factor(match_href)
event_href = as.factor(event_href)
ct_econ_group = as.factor(ct_econ_group)
map_name = as.factor(map_name)
rd_type = as.factor(rd_type)
pick = as.factor(pick)

rounds = list(c(1,16),c(2,17),c(c(3:15),c(18:30)))
round_types = c('pistol', 'rd2', 'main')
formula = ct_win ~ (1|ct_lineup) + (1|t_lineup) + (1|ct_econ_group) + (1|pick)

glmer.function <- function(formula, temp_data, map, round_type){
  model = glmer(formula, data = temp_data, family = binomial, verbose = 0)

  relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
  if (max(abs(relgrad)) > 0.001){
    print('##### converge issue #####')
  }

  print(summary(model))
  eff <- ranef(model, condVar = T)

  t = eff$t_lineup
  t$lineup = rownames(t)
  t$var = sqrt(attr(eff$t_lineup, "postVar")[1, 1, ])
  t = merge(t, data.frame(table(temp_data$t_lineup)), by.x = 'lineup', by.y = 'Var1', all.x = T)
  colnames(t)[c(2:4)] <- c("t_int","t_var","t_rounds")

  ct = eff$ct_lineup
  ct$lineup = rownames(ct)
  ct$var = sqrt(attr(eff$ct_lineup, "postVar")[1, 1, ])
  ct = merge(ct, data.frame(table(temp_data$ct_lineup)), by.x = 'lineup', by.y = 'Var1', all.x = T)
  colnames(ct)[c(2:4)] <- c("ct_int","ct_var","ct_rounds")

  comb = merge(ct, t, by = 'lineup', all.x = T)
  comb$map_name = map
  comb$round_type = round_type
  
  int_val = data.frame(variable = rownames(coef(summary(model))), coef(summary(model)), row.names = NULL)
  int_val$map_name = map
  int_val$round_type = round_type
  
  if ('pick' %in% names(eff)){
    pick = eff$pick
    pick$map_name = map
    pick$round_type = round_type
    pick$var = sqrt(attr(eff$pick, "postVar")[1, 1, ])
    
    rtn_list = list(comb,pick,int_val)
  } else {
    rtn_list = list(comb,int_val)
  }
  
  if ('ct_econ_group' %in% names(eff)){
    ct_econ = eff$ct_econ_group
    ct_econ$map_name = map
    ct_econ$round_type = round_type
    ct_econ$var = sqrt(attr(eff$ct_econ_group, "postVar")[1, 1, ])
    
    rtn_list[[length(rtn_list) + 1]] = ct_econ
  }
  
  if ('map_name:rd_type' %in% names(eff)){
    mprt = eff$`map_name:rd_type`
    mprt$map_name = map
    mprt$round_type = round_type
    mprt$var = sqrt(attr(eff$`map_name:rd_type`, "postVar")[1, 1, ])
    
    rtn_list[[length(rtn_list) + 1]] = mprt
  }

  return(rtn_list)
}

team_eff = data.frame()
pick_eff = data.frame()
int_eff = data.frame()
econ_eff = data.frame()
mprt_eff = data.frame()

for (map in c('all','knife',unique(round_data$map_name))){

  if (map == 'all'){
    temp_data = round_data[round != -1,]
    rtrn = glmer.function(update(formula, ~ . + (1|map_name:rd_type)), temp_data, NA, map)
    team_eff = rbind(team_eff,rtrn[[1]])
    pick_eff = rbind(pick_eff,rtrn[[2]])
    int_eff = rbind(int_eff,rtrn[[3]])
    econ_eff = rbind(econ_eff,rtrn[[4]])
    mprt_eff = rbind(mprt_eff,rtrn[[5]])
  } else if (map == 'knife'){
    temp_data = round_data[round == -1,]
    rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group) - (1|pick)), temp_data, NA, map)
    team_eff = rbind(team_eff,rtrn[[1]])
    int_eff = rbind(int_eff,rtrn[[2]])
  } else {
    for (i in c(1:3)){
      print(c(map, i))
      temp_data = round_data[(map_name == map) & (round %in% rounds[[i]]),]
      if (i == 1){
        rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group)), temp_data, map, round_types[i])
      } else {
        rtrn = glmer.function(formula, temp_data, map, round_types[i])
        econ_eff = rbind(econ_eff,rtrn[[4]])
      }
      team_eff = rbind(team_eff,rtrn[[1]])
      pick_eff = rbind(pick_eff,rtrn[[2]])
      int_eff = rbind(int_eff,rtrn[[3]])
    }
  }
}

dbWriteTable(con, c('csgo', 'glmer_team_eff'), team_eff, row.names = F, overwrite = T)
dbWriteTable(con, c('csgo', 'glmer_pick_eff'), pick_eff, row.names = F, overwrite = T)
dbWriteTable(con, c('csgo', 'glmer_int_eff'), int_eff, row.names = F, overwrite = T)
dbWriteTable(con, c('csgo', 'glmer_econ_eff'), econ_eff, row.names = F, overwrite = T)
dbWriteTable(con, c('csgo', 'glmer_mprt_eff'), mprt_eff, row.names = F, overwrite = T)


ov_str = team_eff[team_eff$round_type == 'all',!(colnames(team_eff) %in% c('map_name','round_type'))]
ov_str$ov_int = ((ov_str$ct_int - mean(ov_str$ct_int))*ov_str$ct_rounds - (ov_str$t_int - mean(ov_str$t_int))*ov_str$t_rounds)/(ov_str$ct_rounds + ov_str$t_rounds)
ov_str$ov_var = ((ov_str$ct_var*ov_str$ct_rounds) + (ov_str$t_var*ov_str$t_rounds))/(ov_str$ct_rounds + ov_str$t_rounds)
ov_str$ov_rds = ov_str$ct_rounds + ov_str$t_rounds

current_ranks = merge(ov_str[(ov_str$lineup %in% active_teams),],unique(round_data[!is.na(round_data$t_team),c('t_lineup','t_team')]), by.x = 'lineup', by.y = 't_lineup', all.x = T)
colnames(current_ranks)[11] = 'team'
                        
dbWriteTable(con, c('csgo', 'glmer_team_ranks'), current_ranks[order(-current_ranks$ov_int),], row.names = F, overwrite = T)