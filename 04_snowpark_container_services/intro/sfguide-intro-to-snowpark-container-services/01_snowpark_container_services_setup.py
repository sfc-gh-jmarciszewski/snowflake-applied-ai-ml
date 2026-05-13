#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from snowflake.core import Root
from snowflake.core.compute_pool import ComputePool
from snowflake.core.image_repository import ImageRepository

from snowflake.core.grant import (
    Grant,
    Grantees,
    Privileges,
    Securables,
)

from snowflake.connector import connect

load_dotenv()

connection_acct_admin = connect(
    connection_name=os.environ["SNOWFLAKE_CONNECTION_NAME"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
)

try:
    root = Root(connection_acct_admin)

    connection_acct_admin.cursor().execute(f"""CREATE OR REPLACE NETWORK RULE {os.environ["NETWORK_RULE_NAME"]}
        TYPE = 'HOST_PORT'
        MODE = 'EGRESS'
        VALUE_LIST= ('0.0.0.0:443', '0.0.0.0:80');""")

    connection_acct_admin.cursor().execute(f"""CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION {os.environ["EAI_NAME"]}
        ALLOWED_NETWORK_RULES = ({os.environ["NETWORK_RULE_NAME"]})
        ENABLED = true;""")

    root.grants.grant(Grant(
        grantee=Grantees.role(os.environ["SNOWFLAKE_ROLE_USER"]),
        securable=Securables.integration(os.environ["EAI_NAME"]),
        privileges=[Privileges.usage]
    ))

    root.session.use_role(os.environ["SNOWFLAKE_ROLE_USER"])

    root.compute_pools.create(ComputePool(
      name=os.environ["COMPUTE_POOL_NAME"],
      min_nodes=1,
      max_nodes=1,
      instance_family=os.environ["COMPUTE_POOL_INSTANCE_FAMILY"],
    ))

    root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].image_repositories.create(ImageRepository(
      name=os.environ["IMAGE_REPO_NAME"],
    ))

    itr_data = root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].image_repositories.iter()
    for image_repo in itr_data:
        print(image_repo)
finally:
        connection_acct_admin.close()
