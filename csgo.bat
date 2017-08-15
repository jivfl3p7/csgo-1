echo off

C:\Anaconda2\python.exe -W ignore %~dp0\python\hltv_scrape.py
::C:\Anaconda2\python.exe -W ignore %~dp0\python\rar_to_csv.py
::C:\Anaconda2\python.exe -W ignore %~dp0\python\other\team_name_match.py

for /f %%a in ('psql -U postgres -c "select 1 as result from pg_database where datname='esports'" -t') do set /a check=%%a

if not defined check (createdb -U postgres esports)

psql -U postgres -d esports -qc "drop schema if exists csgo cascade; create schema csgo;"

psql -U postgres -d esports -qf sql/hltv_team_ranks.sql
psql -U postgres -d esports -qf sql/hltv_events.sql
psql -U postgres -d esports -qf sql/hltv_team_places.sql
psql -U postgres -d esports -qf sql/hltv_match_info.sql
psql -U postgres -d esports -qf sql/hltv_map_results.sql
psql -U postgres -d esports -qf sql/hltv_round_results.sql
psql -U postgres -d esports -qf sql/hltv_player_stats.sql
psql -U postgres -d esports -qf sql/hltv_vetos.sql
psql -U postgres -d esports -qf sql/match_lineups.sql
psql -U postgres -d esports -qf sql/current_team_lineups.sql
::psql -U postgres -d esports -qf sql/lineup_init_stats.sql
::psql -U postgres -d esports -qf sql/demo_info.sql
::psql -U postgres -d esports -qf sql/demo_players.sql
::psql -U postgres -d esports -qf sql/demo_knife.sql
::psql -U postgres -d esports -qf sql/demo_pistol.sql
::psql -U postgres -d esports -qf sql/demo_primary.sql
::psql -U postgres -d esports -qf sql/team_name_match.sql

::placeholder for R script(s)

pause