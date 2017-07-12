# sink("diagnostics/steph.txt")

library("RPostgreSQL")
library("dplyr")
library("PlayerRatings")

drv <- dbDriver("PostgreSQL")

con <- dbConnect(drv, user="postgres", password="", host="localhost", port=5432, dbname="esports")

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

ratings = data.frame()
for (yr in unique(all_data$year)){
  for (map_nm in unique(all_data$map_name[all_data$year == yr])){
    map_data = all_data[(all_data$year == yr) & (all_data$map_name == map_nm),]
    
    x = map_data[,c("week","team1_href","team2_href","result")]
    p1_map_pick = map_data$map_pick
    
    robj <- steph(x, gamma = p1_map_pick)
    robj$ratings$season = yr
    robj$ratings$week = max(map_data$week)
    robj$ratings$map_name = map_nm
    
    ratings <- rbind(ratings,robj$ratings)
  }  
}

names(ratings)[names(ratings) == "Player"] <- "team_href"


dbWriteTable(con,c("csgo","steph_ratings"),ratings, row.names = F, overwrite = T)