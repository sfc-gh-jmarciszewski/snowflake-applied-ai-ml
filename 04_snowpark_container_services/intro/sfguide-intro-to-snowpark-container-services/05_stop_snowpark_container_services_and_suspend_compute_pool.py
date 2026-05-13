#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from snowflake.core import Root
from snowflake.connector import connect

load_dotenv()

connection_container_user_role = connect(
    connection_name=os.environ["SNOWFLAKE_CONNECTION_NAME"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    role=os.environ["SNOWFLAKE_ROLE_USER"],
)

try:
    root = Root(connection_container_user_role)

    root.compute_pools[os.environ["COMPUTE_POOL_NAME"]].stop_all_services()
    root.compute_pools[os.environ["COMPUTE_POOL_NAME"]].suspend()

finally:
    connection_container_user_role.close()
