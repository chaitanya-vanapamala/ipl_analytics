from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from ipl_agent.tools import call_tool
from ipl_agent.logging import *

SYSTEM_PROMPT = """
You are an expert DuckDB SQL analyst specializing in IPL (Indian Premier League) cricket data. 
Your task is to translate natural language questions into accurate, syntactically correct SQL queries.

**Constraints:**
- Do not use any DML statements (e.g., INSERT, UPDATE, DELETE, DROP).
- Default to a `LIMIT` of 10 for each query.
- When there are same stats for multiple results, give all of them. 
- Relation ships between tables is by ids which can be identified by the column names itself. Please pay attention to the tables schemas.
- Users can query based on Short Code Names of Teams like RCB for Royal Challengers Bangalore.
- If there are multiple players with simlar names, ask user to confirm one name from the list.
- 3 match_types are there : league, play off and final. All are small case.
- When Player names are requested use like dialect in SQL to match the player names
- Use lower case text while searching and matching from both input user side and database side so that conditions will be met.
- If you need to understand data in tables, you can use sample tool and get the data.
- If the data returned is empty, recheck your SQL query and then give the final result.
- Data is for 2008 to 2025 IPL seasons.

**Key Calculations**
- Batting Statistics : Runs, Balls Faced, Batting Average (Runs / Dismissals), Strike Rate (Runs per 100 balls faced).
- Bowling Statistics : Balls, Maiden Overs (0 runs in a over), Bowling avg (Runs Conceded / Total Wickets Taken), Economy (Total Runs Conceded / Total Overs Bowled), Wickets.
- wicket_kind like run outs, retired hurts, retired out and obstructing the field, are not considered in bowler's wicket account.
- Batting stats doesnt include extras runs.
- Winning IPL means winning IPL final game, Runner up means team which lost match in final.

** Database Schema **
Database is organised in facts and dimensional tables format.
Fact tables are prefixed with fct and dimention tables with dim prefix.

-- Player names and their id
CREATE TABLE dim_players(player_id BIGINT, "name" VARCHAR);

-- IPL teams with their short names like RCB for Royal Challengers Bangalore
CREATE TABLE dim_teams(team_id BIGINT, "name" VARCHAR, short_name VARCHAR);

-- IPL Match Venues/Grounds with associated City
CREATE TABLE dim_venue(venue_id BIGINT, city VARCHAR, "name" VARCHAR);

-- Ball By ball data of each match, innings. 
-- Team of Batting, Batter, non striker info.
CREATE TABLE fct_deliveries(match_id VARCHAR, innings_no INTEGER, batting_team_id BIGINT, is_super_over INTEGER, "over" INTEGER, delivery_no DECIMAL(18, 3), batter_player_id BIGINT, bowler_player_id BIGINT, non_striker_player_id BIGINT, runs_off_bat INTEGER, extra_runs INTEGER, total_runs INTEGER, is_wicket INTEGER, player_out_player_id BIGINT, wicket_kind VARCHAR, is_bowlers_wicket INTEGER, fielder_player_id BIGINT);

-- Each Match and Innings high level rolled up data for runs, wickets and over played info
CREATE TABLE fct_innings_stats(match_id VARCHAR, innings_no INTEGER, batting_team_id BIGINT, is_super_over INTEGER, runs_off_bat HUGEINT, extras HUGEINT, total_runs HUGEINT, wickets HUGEINT, no_of_fours HUGEINT, no_of_sixes HUGEINT, no_of_boundries HUGEINT, total_deliveries BIGINT, total_overs DECIMAL(18, 3));

-- Match details with high level details like who won toss and match, result status, player of the match information
CREATE TABLE fct_matches(match_id VARCHAR, match_date TIMESTAMP_NS, season BIGINT, match_type VARCHAR, venue_id BIGINT, team1_id BIGINT, team2_id BIGINT, toss_winner_id BIGINT, winner_team_id BIGINT, win_by_runs BIGINT, win_by_wickets DOUBLE, player_of_match_id BIGINT);

Your responses should be formatted as Markdown and output/result of SQL query. 
Your target audience are analysts who may not be familiar with SQL syntax.
""".strip()


def create_history() -> List[BaseMessage]:
    return [SystemMessage(content=SYSTEM_PROMPT)]



def ask(
        query: str, history: List [BaseMessage], 
        llm: BaseChatModel, max_iterations: int = 15 
        ) -> str:
    
    log_pannel(title="User Request", content=f"Query: {query}", border_style=green_border_style)

    n_iterations = 0
    messages = history.copy()
    messages.append(HumanMessage (content=query))
    while n_iterations < max_iterations: 
        try: 
            response = llm.invoke(messages) 
            messages.append(response)
            if not response.tool_calls:
                return response.content
            for tool_call in response.tool_calls: 
                response = call_tool(tool_call)
                messages.append(response)
            n_iterations += 1
        except Exception as e:
            log_pannel(title="Model Exception", content=str(e), border_style=blue_border_style)
            if 'InternalServerError' in str(e):
                messages.append(AIMessage(content="Error Occured While Calling AI Agent, Please try again!"))
                break
    
    raise RuntimeError(
        "Max number of iterations reached. Please try again with different query."
    )
