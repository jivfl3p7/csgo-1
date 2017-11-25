library(RPostgreSQL)
library(ggplot2)
library(ggrepel)
# library(ggjoy)

drv <- dbDriver('PostgreSQL')

con <- dbConnect(drv, user='postgres', password='', host='localhost', port=5432, dbname='csgo')

rank_query <- dbSendQuery(con, "select * from glmer.team_ranking where ov_rds > 200;")

rank_data = fetch(rank_query,n=-1)

top_25 = rank_data[order(-rank_data$ov_int),c('team', 'lineup', 'ov_int', 'ov_var','ov_rds')]

# joy_viz_df = data.frame()
# for (i in c(1:nrow(top_25))){
#   rvals = rnorm(1000,mean = top_25[i,'ov_int'], sd = sqrt(top_25[i,'ov_var']))
#   temp_df = data.frame(team = rep(top_25[i,'team'],1000), ov_int = rep(top_25[i,'ov_int'],1000), rval = rvals)
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
#     data = unique(joy_viz_df[,c('team','ov_int')]),
#     aes(x = ov_int, y = reorder(team,ov_int), label = team),
#     size = 3,
#     nudge_x = 0,
#     nudge_y = 0.4,
#     segment.color = NA
#   )

ypos = c((nrow(top_25) - 1):0)
xmin25 = top_25$ov_int - top_25$ov_var
xmax25 = top_25$ov_int + top_25$ov_var
line_segments = aes(y = ypos, yend = ypos, x = xmin25, xend = xmax25)

plot = ggplot(top_25, aes(x = ov_int, y = ypos, fill = team)) +
  # geom_vline(xintercept = 0, color = "gray", size = 0.5) +
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
    segment.color = NA,
    direction = 'x'
  )

png(filename = 'png/rankings.png', bg = 'transparent', units = 'px', width = 861, height = 546)
plot(plot)
dev.off()