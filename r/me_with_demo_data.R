library(RPostgreSQL)
library(lme4)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='csgo')

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
from demo.rounds as dr
  left join demo.info as di
    on
      dr.match_href = di.match_href
      and dr.map_num = di.map_num
  left join hltv.match_info as mi
    on dr.match_href = mi.match_href
  left join hltv.events as e
    on mi.event_href = e.event_href
  left join hltv.match_lineups as tl
    on
      dr.match_href = tl.match_href
      and dr.t_href = tl.team_href
  left join hltv.active_teams as tl2
    on tl.lineup = tl2.lineup
  left join hltv.match_lineups as ctl
    on
      dr.match_href = ctl.match_href
      and dr.ct_href = ctl.team_href
  left join hltv.active_teams as ctl2
    on ctl.lineup = ctl2.lineup
  left join hltv.vetos as v
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
ct_lineup = as.factor(ct_lineup)
t_lineup = as.factor(t_lineup)
ct_econ_group = as.factor(ct_econ_group)
map_name = as.factor(map_name)
rd_type = as.factor(rd_type)
pick = as.factor(pick)
plant = as.factor(plant)

rounds = list(c(1,16),c(2,17),c(c(3:15),c(18:30)))
round_types = c('pistol', 'rd2', 'main')

glmer.function <- function(formula, temp_data, map, round_type, dep_var){
  model = glmer(formula, data = temp_data, family = binomial, verbose = 0)

  relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
  if (max(abs(relgrad)) > 0.0003){
    print('##### converge issue #####')
    model = glmer(update(formula, ~ . - (1|pick)), data = temp_data, family = binomial, verbose = 0)
    
    relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
    if (max(abs(relgrad)) > 0.0003){
      conv_err = data.frame(dep_var,map,round_type)
      names(conv_err) = c('dep_var','map_name','round_type')
      return(list(data.frame(),data.frame(),data.frame(),data.frame(),data.frame(),conv_err))
      stop(paste('Convergence failure:',dep_var,i,map))
    }
  }

  print(summary(model))
  eff = ranef(model, condVar = T)

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
  comb$dep_var = dep_var
  
  int_val = data.frame(variable = rownames(coef(summary(model))), coef(summary(model)), row.names = NULL)
  int_val$map_name = map
  int_val$round_type = round_type
  int_val$dep_var = dep_var
  
  if ('pick' %in% names(eff)){
    pick = eff$pick
    pick$map_name = map
    pick$round_type = round_type
    pick$var = sqrt(attr(eff$pick, "postVar")[1, 1, ])
    pick$dep_var = dep_var
    
    rtn_list = list(comb,pick,int_val)
  } else {
    rtn_list = list(comb,data.frame(),int_val)
  }
  
  if ('ct_econ_group' %in% names(eff)){
    ct_econ = eff$ct_econ_group
    ct_econ$map_name = map
    ct_econ$round_type = round_type
    ct_econ$var = sqrt(attr(eff$ct_econ_group, "postVar")[1, 1, ])
    ct_econ$dep_var = dep_var
    
    rtn_list[[4]] = ct_econ
  } else {
    rtn_list[[4]] = data.frame()
  }
  
  if ('map_name:rd_type' %in% names(eff)){
    mprt = eff$`map_name:rd_type`
    mprt$map_name = map
    mprt$round_type = round_type
    mprt$var = sqrt(attr(eff$`map_name:rd_type`, "postVar")[1, 1, ])
    mprt$dep_var = dep_var
    
    rtn_list[[5]] = mprt
  } else {
    rtn_list[[5]] = data.frame()
  }
  
  rtn_list[[6]] = data.frame()
  
  names(rtn_list) = c('team_eff','pick_eff','int_eff','econ_eff','mprt_eff','mod_fail')

  return(rtn_list)
}

team_eff = data.frame()
pick_eff = data.frame()
int_eff = data.frame()
econ_eff = data.frame()
mprt_eff = data.frame()
mod_fail = data.frame()

for (dep_var in c('ct_win','plant')){
  if (dep_var == 'ct_win'){
    formula = ct_win ~ (1|ct_lineup) + (1|t_lineup) + (1|ct_econ_group) + (1|pick)
  } else {
    formula = plant ~ (1|ct_lineup) + (1|t_lineup) + (1|ct_econ_group) + (1|pick)
  }
  
  for (map in c('all','knife',unique(round_data$map_name))){
    if ((map == 'all') & (dep_var == 'ct_win')){
      temp_data = round_data[round != -1,]
      rtrn = glmer.function(update(formula, ~ . + (1|map_name:rd_type)), temp_data, NA, map, dep_var)
      team_eff = rbind(team_eff,rtrn[[1]])
      pick_eff = rbind(pick_eff,rtrn[[2]])
      int_eff = rbind(int_eff,rtrn[[3]])
      econ_eff = rbind(econ_eff,rtrn[[4]])
      mprt_eff = rbind(mprt_eff,rtrn[[5]])
      mod_fail = rbind(mod_fail,rtrn[[6]])
    } else if ((map == 'knife') & (dep_var == 'ct_win')){
      temp_data = round_data[round == -1,]
      rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group) - (1|pick)), temp_data, NA, map, dep_var)
      team_eff = rbind(team_eff,rtrn[[1]])
      pick_eff = rbind(pick_eff,rtrn[[2]])
      int_eff = rbind(int_eff,rtrn[[3]])
      econ_eff = rbind(econ_eff,rtrn[[4]])
      mprt_eff = rbind(mprt_eff,rtrn[[5]])
      mod_fail = rbind(mod_fail,rtrn[[6]])
    } else if (!(map %in% c('all','knife'))){
      for (i in c(1:3)){
        print(c(dep_var,map, i))
        temp_data = round_data[(map_name == map) & (round %in% rounds[[i]]),]
        if (i == 1){
          rtrn = glmer.function(update(formula, ~ . - (1|ct_econ_group)), temp_data, map, round_types[i], dep_var)
        } else {
          rtrn = glmer.function(formula, temp_data, map, round_types[i], dep_var)
        }
        team_eff = rbind(team_eff,rtrn[[1]])
        pick_eff = rbind(pick_eff,rtrn[[2]])
        int_eff = rbind(int_eff,rtrn[[3]])
        econ_eff = rbind(econ_eff,rtrn[[4]])
        mprt_eff = rbind(mprt_eff,rtrn[[5]])
        mod_fail = rbind(mod_fail,rtrn[[6]])
      }
    }
  }
  
  dbWriteTable(con, c('glmer', paste0('team_eff','_',dep_var)), team_eff, row.names = F, overwrite = T)
  dbWriteTable(con, c('glmer', paste0('pick_eff','_',dep_var)), pick_eff, row.names = F, overwrite = T)
  dbWriteTable(con, c('glmer', paste0('int_eff','_',dep_var)), int_eff, row.names = F, overwrite = T)
  dbWriteTable(con, c('glmer', paste0('econ_eff','_',dep_var)), econ_eff, row.names = F, overwrite = T)
  dbWriteTable(con, c('glmer', paste0('mprt_eff','_',dep_var)), mprt_eff, row.names = F, overwrite = T)
  
  if (nrow(mod_fail) > 0){
    dbWriteTable(con, c('glmer', 'mod_fail'), mod_fail, row.names = F, overwrite = F, append = T)
  }
  
  if (dep_var == 'ct_win'){
    ov_str = team_eff[(team_eff$round_type == 'all') & (!is.na(team_eff$ct_int) & !is.na(team_eff$t_int)),!(colnames(team_eff) %in% c('map_name','round_type'))]
    ov_str$ov_int = ((ov_str$ct_int - mean(ov_str$ct_int))*ov_str$ct_rounds - (ov_str$t_int - mean(ov_str$t_int))*ov_str$t_rounds)/(ov_str$ct_rounds + ov_str$t_rounds)
    ov_str$ov_var = ((ov_str$ct_var*ov_str$ct_rounds) + (ov_str$t_var*ov_str$t_rounds))/(ov_str$ct_rounds + ov_str$t_rounds)
    ov_str$ov_rds = ov_str$ct_rounds + ov_str$t_rounds
    
    current_ranks = merge(ov_str[(ov_str$lineup %in% active_teams),],unique(round_data[!is.na(round_data$t_team),c('t_lineup','t_team')]), by.x = 'lineup', by.y = 't_lineup', all.x = T)
    colnames(current_ranks)[12] = 'team'
    
    dbWriteTable(con, c('glmer', 'team_ranking'), current_ranks[order(-current_ranks$ov_int),], row.names = F, overwrite = T)
  }
}