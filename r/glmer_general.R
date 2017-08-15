library(RPostgreSQL)
library(lme4)
library(arm)
library(plyr)
library(dplyr)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='esports')

round_data_query <- dbSendQuery(con, "
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
    left join csgo.match_lineups as l1
      on
        rr.match_href = l1.match_href
        and rr.team1_href = l1.team_href
    left join csgo.match_lineups as l2
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

round_data = fetch(round_data_query,n=-1)

round_data$ct_win = ifelse(round_data$team1_side == 'ct', round_data$round_result, ifelse(round_data$round_result == 1,0,1))

round_data$ct_team = ifelse(round_data$team1_side == 'ct', paste(round_data$team1_lineup, round_data$season, sep = '_'),
                            paste(round_data$team2_lineup, round_data$season, sep = '_'))
round_data$t_team = ifelse(round_data$team1_side == 't', paste(round_data$team1_lineup, round_data$season, sep = '_'),
                           paste(round_data$team2_lineup, round_data$season, sep = '_'))

attach(round_data)

ct_win = as.factor(ct_win)
season = as.factor(season)
map_name = as.factor(map_name)
season = as.factor(season)
ct_team = as.factor(ct_team)
t_team = as.factor(t_team)
match_href = as.factor(match_href)
event_href = as.factor(event_href)

formula = ct_win ~ map_name + (1|ct_team) + (1|t_team) + (1|match_href) + (1|event_href)

model = glmer(formula, data = round_data, family = binomial, verbose = 2)

relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
print(max(abs(relgrad)))

# summary(model)
map_effects = data.frame(variable = rownames(coef(summary(model))), coef(summary(model)), row.names = NULL)


eff <- ranef(model, condVar=TRUE)

team_str = data.frame(lineup = row.names(eff$t_team),
                      ct_int = eff$ct_team$`(Intercept)`,
                      ct_var = sqrt(attr(eff[[3]], "postVar")[1, 1, ]),
                      t_int = eff$t_team$`(Intercept)`,
                      t_var = sqrt(attr(eff[[2]], "postVar")[1, 1, ]))
team_str = merge(team_str, data.frame(table(round_data$ct_team)), by.x = 'lineup', by.y = 'Var1', all.x = T) %>% rename(ct_rounds = Freq)
team_str = merge(team_str, data.frame(table(round_data$t_team)), by.x = 'lineup', by.y = 'Var1', all.x = T) %>% rename(t_rounds = Freq)
team_str$ov_int = (team_str$ct_int*team_str$ct_rounds - team_str$t_int*team_str$t_rounds)/(team_str$ct_rounds + team_str$t_rounds)
team_str$ov_var = (team_str$ct_var*team_str$ct_rounds + team_str$t_var*team_str$t_rounds)/(team_str$ct_rounds + team_str$t_rounds)
team_str$season = as.numeric(lapply(as.vector(team_str$lineup), function(x) substr(x, nchar(x) - 4 + 1, nchar(x))))
team_str$lineup = as.character(lapply(as.vector(team_str$lineup), function(x) substr(x, 1, nchar(x) - 5)))
team_str$maps = round((team_str$ct_rounds + team_str$t_rounds)/25.5,1)
team_str = merge(team_str, dbReadTable(con, c("csgo","current_team_lineups")), by.x = 'lineup', by.y = 'lineup_id', all.x = T)

head(subset(team_str[order(team_str$ov_int, decreasing = T),], (season == 2017) & (!is.na(team_name)) & (maps > 20),
            select = c(lineup,team_name,ov_int,ov_var,maps)),50)