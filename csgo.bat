echo off

if "%computername%"=="MITCHELL-LAPTOP" (
	set init_path=C:\Users\wesso\Documents\GitHub\csgo\csv
	set ana_path=C:\Users\wesso
) else (
	set init_path=C:\Users\wessonmo\Documents\GitHub\csgo\csv
	set ana_path=C:
)

::%ana_path%\Anaconda2\python.exe -W ignore %~dp0\python\hltv_scrape.py
::%ana_path%\Anaconda2\python.exe -W ignore %~dp0\python\rar_to_csv.py

for /f %%a in ('psql -U postgres -c "select 1 as result from pg_database where datname='esports'" -t') do set /a check=%%a

if not defined check (createdb -U postgres esports)

psql -U postgres -d esports -qc "drop schema if exists csgo cascade; create schema csgo;"

psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_team_ranks.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_events.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_team_places.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_match_info.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_map_results.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_round_results.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_player_stats.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_vetos.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/hltv_active_teams.sql
psql -U postgres -d esports -qf sql/match_lineups.sql
psql -U postgres -d esports -qf sql/current_team_lineups.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/demo_info.sql
psql -U postgres -d esports -v init_path=%init_path% -qf sql/demo_rounds.sql

::placeholder for R script(s)

pause