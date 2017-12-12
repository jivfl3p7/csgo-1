echo off

if "%computername%"=="MITCHELL-LAPTOP" (
	set init_path=C:\Users\wesso\Documents\GitHub\csgo\csv
	set ana_path=C:\Users\wesso
) else (
	set init_path=C:\Users\wessonmo\Documents\GitHub\csgo\csv
	set ana_path=C:
)

%ana_path%\Anaconda2\python.exe -W ignore %~dp0\python\hltv_scrape.py
%ana_path%\Anaconda2\python.exe -W ignore %~dp0\python\rar_to_csv.py

for /f %%a in ('psql -U postgres -c "select 1 as result from pg_database where datname='csgo'" -t') do set /a check=%%a

if not defined check (createdb -U postgres csgo)

psql -U postgres -d csgo -qc "drop schema if exists hltv cascade; create schema hltv;"

psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_team_ranks.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_events.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_team_places.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_match_info.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_map_results.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_round_results.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_player_stats.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_match_lineups.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_vetos.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/hltv_active_teams.sql

psql -U postgres -d csgo -qc "drop schema if exists demo cascade; create schema demo;"

psql -U postgres -d csgo -v init_path=%init_path% -qf sql/demo_info.sql
psql -U postgres -d csgo -v init_path=%init_path% -qf sql/demo_rounds.sql

psql -U postgres -d csgo -qc "drop schema if exists glmer cascade; create schema glmer;"

REM Rscript --silent r\me_with_demo_data.R
REM Rscript --silent r\team_str_plot.R

pause