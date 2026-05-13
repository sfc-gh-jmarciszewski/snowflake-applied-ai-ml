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

    root.compute_pools[os.environ["COMPUTE_POOL_NAME"]].delete()
    root.databases[os.environ["SNOWFLAKE_DATABASE"]].delete()
    root.warehouses[os.environ["SNOWFLAKE_WAREHOUSE"]].delete()

    connection_acct_admin = connect(
        connection_name=os.environ["SNOWFLAKE_CONNECTION_NAME"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        role=os.environ["SNOWFLAKE_ROLE_ADMIN"],
    )

    root = Root(connection_acct_admin)

    try:
        root.roles[os.environ["SNOWFLAKE_ROLE_USER"]].delete()
    finally:
        connection_acct_admin.close()

finally:
    connection_container_user_role.close()
