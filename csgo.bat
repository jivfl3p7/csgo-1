echo off

C:\Anaconda2\python.exe -W ignore %~dp0\python\scrape\hltv_scrape_teamrank.py
C:\Anaconda2\python.exe -W ignore %~dp0\python\scrape\hltv_scrape_event.py
C:\Anaconda2\python.exe -W ignore %~dp0\python\scrape\hltv_scrape_match.py
C:\Anaconda2\python.exe -W ignore %~dp0\python\scrape\hltv_scrape_demo.py

::C:\Anaconda2\python.exe -W ignore %~dp0\python\parse\rar_to_demo.py
::C:\Anaconda2\python.exe -W ignore %~dp0\python\parse\demo_to_json.py
::C:\Anaconda2\python.exe -W ignore %~dp0\python\parse\json_to_csv.py

::C:\Anaconda2\python.exe -W ignore %~dp0\python\other\team_name_match.py

for /f %%a in ('psql -U postgres -c "select 1 as result from pg_database where datname='esports'" -t') do set /a check=%%a

if not defined check (createdb -U postgres esports)

psql -U postgres -d esports -qc "drop schema if exists csgo cascade; create schema csgo;"

psql -U postgres -d esports -qf sql/hltv_team_ranks.sql
psql -U postgres -d esports -qf sql/hltv_events.sql
psql -U postgres -d esports -qf sql/hltv_match_info.sql
psql -U postgres -d esports -qf sql/hltv_map_results.sql
psql -U postgres -d esports -qf sql/hltv_vetos.sql
::psql -U postgres -d esports -qf sql/demo_info.sql
::psql -U postgres -d esports -qf sql/demo_players.sql
::psql -U postgres -d esports -qf sql/demo_knife.sql
::psql -U postgres -d esports -qf sql/demo_pistol.sql
::psql -U postgres -d esports -qf sql/demo_primary.sql
::psql -U postgres -d esports -qf sql/team_name_match.sql

::placeholder for R script(s)

pause