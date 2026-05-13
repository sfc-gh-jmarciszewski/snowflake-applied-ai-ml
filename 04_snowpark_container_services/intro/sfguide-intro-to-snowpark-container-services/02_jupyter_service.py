#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from snowflake.core import Root
from snowflake.core._common import CreateMode
from snowflake.core.service import Service, ServiceSpecStageFile

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

    s = (
        root.databases[os.environ["SNOWFLAKE_DATABASE"]]
        .schemas[os.environ["SNOWFLAKE_SCHEMA"]]
        .services.create(
            Service(
                name=os.environ["JUPYTER_SERVICE_NAME"],
                compute_pool=os.environ["COMPUTE_POOL_NAME"],
                spec=ServiceSpecStageFile(
                    stage=os.environ["STAGE_SPECS"], spec_file=os.environ["JUPYTER_SPEC_FILE"]
                ),
                external_access_integrations=[os.environ["EAI_NAME"]],
            ),
            mode=CreateMode.if_not_exists,
        )
    )

    containers = s.get_containers()
    for container in containers:
        print(container.service_status)

    logs = s.get_service_logs("0", "jupyter-snowpark", 10)
    print(logs)

    endpoints = s.get_endpoints()
    for endpoint in endpoints:
        print(endpoint)

    s.suspend()
    s.resume()

finally:
    connection_container_user_role.close()
