# sink("diagnostics/steph.txt")

library("RPostgreSQL")
library("dplyr")
library("PlayerRatings")

drv <- dbDriver("PostgreSQL")

con <- dbConnect(drv, user="postgres", password="", host="localhost", port=5432, dbname="esports2")

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
  LIMIT 100
  ;")

test <- fetch(query,n=-1)

attach(test)



head(test)

for (map_nm in map_name){
  x = data.frame(test[,c("")])
}

# head(map_data)
# write.csv(map_data, file = 'map_data.csv', row.names = T)