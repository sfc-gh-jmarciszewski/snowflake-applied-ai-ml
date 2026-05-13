#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from snowflake.core import Root
from snowflake.core._common import CreateMode
from snowflake.core.warehouse import Warehouse
from snowflake.core.stage import (
    Stage,
    StageEncryption,
    StageDirectoryTable,
)

from snowflake.core.grant import (
    Grant,
    Grantees,
    Privileges,
    Securables,
)


from snowflake.core.role import Role
from snowflake.core.database import Database

from snowflake.connector import connect

load_dotenv()

connection_acct_admin = connect(
    connection_name=os.environ["SNOWFLAKE_CONNECTION_NAME"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    role=os.environ["SNOWFLAKE_ROLE_ADMIN"],
)

try:
    root = Root(connection_acct_admin)

    root.roles.create(Role(
        name=os.environ["SNOWFLAKE_ROLE_USER"],
        comment='My role to use container',
    ))

    root.grants.grant(Grant(
        grantee=Grantees.role(os.environ["SNOWFLAKE_ROLE_USER"]),
        securable=Securables.current_account,
        privileges=[Privileges.create_database,
                    Privileges.create_warehouse,
                    Privileges.create_compute_pool,
                    Privileges.create_integration,
                    Privileges.monitor_usage,
                    Privileges.bind_service_endpoint
                    ],
    ))

    root.grants.grant(Grant(
        grantee=Grantees.role(os.environ["SNOWFLAKE_ROLE_USER"]),
        securable=Securables.database('snowflake'),
        privileges=[Privileges.imported_privileges
                    ],
    ))

    root.grants.grant(Grant(
        grantee=Grantees.role(os.environ["SNOWFLAKE_ROLE_ADMIN"]),
        securable=Securables.role(os.environ["SNOWFLAKE_ROLE_USER"])
    ))

    root.session.use_role(os.environ["SNOWFLAKE_ROLE_USER"])

    root.databases.create(Database(
        name=os.environ["SNOWFLAKE_DATABASE"],
        comment="This is a Container Quick Start Guide database"
    ), mode=CreateMode.or_replace)

    root.warehouses.create(Warehouse(
        name=os.environ["SNOWFLAKE_WAREHOUSE"],
        warehouse_size="XSMALL",
        auto_suspend=120,
        auto_resume="true",
        comment="This is a Container Quick Start Guide warehouse"
    ), mode=CreateMode.or_replace)

    root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].stages.create(
        Stage(
            name=os.environ["STAGE_SPECS"],
            encryption=StageEncryption(type="SNOWFLAKE_SSE")
    ))

    root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].stages.create(
        Stage(
            name=os.environ["STAGE_VOLUMES"],
            encryption=StageEncryption(type="SNOWFLAKE_SSE"),
            directory_table=StageDirectoryTable(enable=True)
    ))

finally:
    connection_acct_admin.close()
