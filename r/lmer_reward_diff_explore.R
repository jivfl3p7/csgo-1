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

# active_teams = unique(c(round_data[!is.na(round_data$t_team),'t_lineup'],round_data[!is.na(round_data$ct_team),'ct_lineup']))

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

lmer.function <- function(formula, temp_data, map, round_type, win, plnt){
  model = lmer(formula, data = temp_data, verbose = 0)
  
  relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
  if (max(abs(relgrad)) > 0.0003){
    print('##### converge issue #####')
    model = lmer(formula, data = temp_data, verbose = 0)
    
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
  fix = fixef(model)
  
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
  comb$dep_var = 'ct_reward_diff'
  
  int_val = data.frame(variable = rownames(coef(summary(model))), coef(summary(model)), row.names = NULL)
  int_val$map_name = map
  int_val$round_type = round_type
  int_val$dep_var = 'ct_reward_diff'
  
  if ('pick' %in% names(eff)){
    pick = eff$pick
    pick$map_name = map
    pick$round_type = round_type
    pick$var = sqrt(attr(eff$pick, "postVar")[1, 1, ])
    pick$dep_var = 'ct_reward_diff'
    
    rtn_list = list(comb,pick,int_val)
  } else {
    rtn_list = list(comb,data.frame(),int_val)
  }
  
  if ('ct_econ_group' %in% names(eff)){
    ct_econ = eff$ct_econ_group
    ct_econ$map_name = map
    ct_econ$round_type = round_type
    ct_econ$var = sqrt(attr(eff$ct_econ_group, "postVar")[1, 1, ])
    ct_econ$dep_var = 'ct_reward_diff'
    
    rtn_list[[4]] = ct_econ
  } else {
    rtn_list[[4]] = data.frame()
  }
  
  if ('map_name:rd_type' %in% names(eff)){
    mprt = eff$`map_name:rd_type`
    mprt$map_name = map
    mprt$round_type = round_type
    mprt$var = sqrt(attr(eff$`map_name:rd_type`, "postVar")[1, 1, ])
    mprt$dep_var = 'ct_reward_diff'
    
    rtn_list[[5]] = mprt
  } else {
    rtn_list[[5]] = data.frame()
  }
  
  rtn_list[[6]] = data.frame()
  
  names(rtn_list) = c('team_eff','pick_eff','int_eff','econ_eff','mprt_eff','mod_fail')
  
  return(rtn_list)
}

formula = ct_reward_diff ~ (1|t_lineup) + (1|ct_lineup) + (1|ct_econ_group)
for (win in c(0,1)){
  for (plnt in c(0,1)){
    for (i in c(1,2,0)){
      if (i == 1){
        round_type = 'pistol'
        formula = ct_reward_diff ~ (1|t_lineup) + (1|ct_lineup) + map_name
        temp_data = round_data[(plant == 1) & (ct_win == 1) & (rd_type == i),]
      } else if (i == 2) {
        round_type = 'rd2'
        formula = ct_reward_diff ~ (1|t_lineup) + (1|ct_lineup) + ct_econ_group + map_name
        temp_data = round_data[(plant == 1) & (ct_win == 1) & (rd_type == i),]
      } else {
        round_type = 'main'
        formula = ct_reward_diff ~ (1|t_lineup) + (1|ct_lineup) + ct_econ_group
        for (map in unique(round_data$map_name)){
          temp_data = round_data[(plant == plnt) & (ct_win == win) & (rd_type == i) & (map_name == map),]
        }
      }
    }
  }
}

model = lmer(formula, data = temp_data, verbose = 0)
summary(model)

r = residuals(model)
mse = mean(r^2)

ranef(model)$'plant:ct_win'

# Jackknife - 4500 data points 1000 times

subs=4500
iter=1000

# Vector of results

pvals=rep(NA, iter)

# Sample p-values

for(i in 1:iter){
  samp=sample(1:length(r),4500)
  p.i=sf.test(r[samp])$p.value
  pvals[i]=p.i
}

# Sampled p-value statistics

mean(pvals)
median(pvals)
sd(pvals)

# Graph p-values

# jpeg("diagnostics/shapiro-francia.jpg")
hist(pvals,xlim=c(0,1))
abline(v=0.05,lty='dashed',lwd=2,col='red')
quantile(pvals,prob=seq(0,1,0.05))

# Examine residuals

jpeg("diagnostics/fitted_vs_residuals.jpg")
plot(f,r)
jpeg("diagnostics/q-q_plot.jpg")
qqnorm(r,main="Q-Q plot for residuals")




eff = ranef(model, condVar = T)
anova(model)
display(model)