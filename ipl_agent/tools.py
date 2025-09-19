import duckdb

from contextlib import contextmanager
from typing import Any, List

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import BaseTool

from ipl_agent.config import Config
from ipl_agent.logging import log, log_pannel


def get_available_tools() -> List[BaseTool]:
    return [sample_table, execute_sql]


def call_tool(tool_call: ToolCall) -> Any:
    tools_by_name = {tool.name: tool for tool in get_available_tools()}
    tool = tools_by_name[tool_call["name"]]
    response = tool.invoke(tool_call["args"])
    return ToolMessage(content=response, tool_call_id=tool_call["id"])



@contextmanager
def with_sql_cursor(readonly=True):
    conn = duckdb.connect(Config.Path.DATABASE_PATH)
    cur = conn.cursor()

    try:
        yield cur
        if not readonly:
            conn.commit()
    except Exception:
        if not readonly:
            conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@tool(parse_docstring=True)
def list_tables(reasoning: str) -> str:
    """
    Lists all user-created tables for IPL Data Analysis.

    Args:
        reasoning: Detailed Explanation of why you need to see all tables (realted to user's query)

    Returns:
        string representation of a list containing all the table names
    """
    log_pannel(
        title="List Tables Tool",
        content=f"Reasoning : {reasoning}"
    )

    try:
        with with_sql_cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' and table_name not like 'stg_%' and table_name not like 'raw%'"
                )
            tables = [row[0] for row in cursor.fetchall()]
            return str(tables)
    except Exception as e:
        log(f"[red]Error lising tables: {str(e)}[/red]")
        return f"Error listing tables: {str(e)}"
    

@tool(parse_docstring=True)
def sample_table(reasoning: str, table_name: str, row_sample_size: int) -> str:
    """
    Retrives a small sample of rows to understand the data structure and contents of a specific table

    Args:
        reasoning: Detailed Explanation of why you need to see all tables (realted to user's query)
        table_name: Exact name of table to sample (case sensitive, no quotes needed)
        row_sample_size: Number of row to retrive (recomended 3-5 rows for readability)

    Returns:
        String with one row per line, showing all columns for each row as tuples
    """

    log_pannel(
        title="Sample Table Tool",
        content=f"Table: {table_name} \n Rows: {row_sample_size} \n Reasoning : {reasoning}"
    )

    try:
        with with_sql_cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {row_sample_size}")
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error sample table: {str(e)}[/red]")
        return f"Error sample table: {str(e)}"


@tool(parse_docstring=True)
def describe_table(reasoning: str, table_name: str) -> str:
    """
    Retrives detailed schema information about the table.

    Args:
        reasoning: Detailed Explanation of why you need to see all tables (realted to user's query)
        table_name: Exact name of table to get the schema information (case sensitive, no quotes needed)

    Returns:
        String containing table schema information
    """

    log_pannel(
        title="Describe Table Tool",
        content=f"Table: {table_name} \n Reasoning : {reasoning}"
    )

    try:
        with with_sql_cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error describe table: {str(e)}[/red]")
        return f"Error describe table: {str(e)}"



@tool(parse_docstring=True)
def execute_sql(reasoning: str, sql_query: str) -> str:
    """
    Executes SQL query and return the result

    Args:
        reasoning: Detailed Explanation of why you need to see all tables (realted to user's query)
        sql_query: Complete Properly formatted, duck db supported SQL query

    Returns:
        String with query result, one row per line as tuples
    """

    log_pannel(
        title="Execute SQL Tool",
        content=f"Query: {sql_query} \n Reasoning : {reasoning}"
    )

    try:
        with with_sql_cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error execute sql: {str(e)}[/red]")
        return f"Error execute sql: {str(e)}"


