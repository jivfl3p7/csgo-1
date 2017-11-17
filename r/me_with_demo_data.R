library(RPostgreSQL)
library(lme4)
library(plyr)
library(dplyr)
library(sm)
library(stringr)
library(ggplot2)
library(ggrepel)
library(ggjoy)

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
  ,tl2.team_name as t_team
  ,tl.lineup_id as t_lineup
  ,case
    when tl3.team_href is null then 0
    else 1
  end as t_active
  ,dr.ct_href
  ,ctl2.team_name as ct_team
  ,ctl.lineup_id as ct_lineup
  ,case
    when ctl3.team_href is null then 0
    else 1
  end as ct_active
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
    on tl.lineup_id = tl3.lineup
  left join csgo.match_lineups as ctl
    on
    dr.match_href = ctl.match_href
    and dr.ct_href = ctl.team_href
  left join csgo.current_team_lineups as ctl2
    on
    ctl.lineup_id = ctl2.lineup_id
    and ctl.match_href = ctl2.match_href
  left join csgo.hltv_active_teams as ctl3
    on ctl.lineup_id = ctl3.lineup
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

active_teams = unique(c(round_data[round_data$t_active == 1,'t_lineup'],round_data[round_data$ct_active == 1,'ct_lineup']))
unique(round_data[round_data$t_lineup == '/player/2023/FalleN/player/8564/fer/player/9216/coldzera/player/9217/TACO/player/9219/felps',c('t_team','t_active')])
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

rounds = list(c(1,16),c(2,17),c(c(3:15),c(18:30)))
round_types = c('pistol', 'rd2', 'main')
formula = ct_win ~ (1|ct_lineup) + (1|t_lineup) + (1|ct_econ_group)

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

head(team_str)

ov_str = team_str[team_str$round_type == 'all',!(colnames(team_str) %in% c('map_name','round_type'))]
ov_str$ov_int = ((ov_str$ct_int - mean(ov_str$ct_int))*ov_str$ct_rounds - (ov_str$t_int - mean(ov_str$t_int))*ov_str$t_rounds)/(ov_str$ct_rounds + ov_str$t_rounds)
ov_str$ov_var = ((ov_str$ct_var*ov_str$ct_rounds) + (ov_str$t_var*ov_str$t_rounds))/(ov_str$ct_rounds + ov_str$t_rounds)
ov_str$ov_rds = ov_str$ct_rounds + ov_str$t_rounds

current_ranks = merge(ov_str[(ov_str$ov_rds >= 200) & (ov_str$lineup %in% active_teams),],unique(round_data[round_data$t_active == 1,c('t_lineup','t_team')]), by.x = 'lineup', by.y = 't_lineup', all.x = T)
colnames(current_ranks)[11] = 'team'
                        
dbWriteTable(con, c('csgo', 'team_rankings'), current_ranks[order(-current_ranks$ov_int),], row.names = F, overwrite = T)

top_25 = head(current_ranks[order(-current_ranks$ov_int),c('team', 'lineup', 'ov_int', 'ov_var','ov_rds')],25)

# joy_viz_df = data.frame()
# for (i in c(1:nrow(top_25))){
#   rvals = rnorm(10000,mean = top_25[i,'ov_int'], sd = top_25[i,'ov_var'])
#   temp_df = data.frame(team = rep(top_25[i,'team'],10000), ov_int = top_25[i,'ov_int'], rval = rvals)
#   joy_viz_df = rbind(joy_viz_df, temp_df)
# }
# 
# ggplot(joy_viz_df, aes(x = rval, y = reorder(team,ov_int), fill = team)) +
#   geom_joy(scale = 2, rel_min_height = 0.01) +
#   theme_joy() +
#   scale_fill_manual(values=rep(c('gray', 'lightblue'), nrow(joy_viz_df)/2)) +
#   scale_y_discrete(expand = c(0.01, 0)) +
#   scale_x_continuous(expand = c(0, 0)) +
#   theme(legend.position = "None",
#         axis.ticks.x = element_blank(),
#         axis.ticks.y = element_blank(),
#         axis.text.y = element_blank(),
#         panel.grid.minor.x = element_blank(),
#         panel.grid.major.y = element_blank(),
#         panel.grid.minor.y = element_blank(),
#         panel.background = element_rect(fill = NA)) +
#   labs(x="team strength" ,y="") +
#   geom_text_repel(
#     data = top_25,
#     aes(x = ov_int, y = reorder(team,ov_int), label = str_sub(team, end = -3)),
#     size = 3,
#     nudge_x = -0.2,
#     nudge_y = 0.4,
#     segment.color = NA
#   )























ypos = c((nrow(top_25) - 1):0)
xmin25 = top_25$ov_int - sqrt(top_25$ov_var)
xmax25 = top_25$ov_int + sqrt(top_25$ov_var)
line_segments = aes(y = ypos, yend = ypos, x = xmin25, xend = xmax25)

ggplot(top_25, aes(x = ov_int, y = ypos, fill = team)) +
  geom_segment(data = top_25, line_segments, color = 'black') +
  geom_point(aes(x = ov_int, y = ypos, color = 'red'), size = 2) +
  xlim(min(xmin25) - 0.02,max(xmax25)) +
  theme(legend.position = "None",
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        axis.text.y = element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.major.y = element_blank(),
        panel.grid.minor.y = element_blank(),
        panel.background = element_rect(fill = NA)) +
  labs(x="team strength" ,y="") +
  geom_text_repel(
    data = top_25,
    aes(x = xmin25, y = ypos, label = team),
    size = 3,
    nudge_x = -0.01,
    segment.color = NA
  )