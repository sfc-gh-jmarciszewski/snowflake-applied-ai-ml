#!/usr/bin/env python3
import os

from dotenv import load_dotenv

from snowflake.core import Root
from snowflake.core._common import CreateMode
from snowflake.core.service import Service, ServiceSpecStageFile
from snowflake.core.table import Table, TableColumn
from snowflake.core.function import FunctionArgument, ServiceFunction

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

    db = root.databases[os.environ["SNOWFLAKE_DATABASE"]]
    schema = db.schemas[os.environ["SNOWFLAKE_SCHEMA"]]

    s = (
        schema.services.create(
            Service(
                name=os.environ["CONVERT_SERVICE_NAME"],
                compute_pool=os.environ["COMPUTE_POOL_NAME"],
                spec=ServiceSpecStageFile(stage=os.environ["STAGE_SPECS"], spec_file=os.environ["CONVERT_SPEC_FILE"]),
                external_access_integrations=[os.environ["EAI_NAME"]],
            ),
            mode=CreateMode.if_not_exists,
        )
    )

    containers = s.get_containers()
    for container in containers:
        print(container.service_status)

    logs = s.get_service_logs("0", "convert-api", 10)
    print(logs)

    schema.tables.create(
        Table(
            name="WEATHER",
            columns=[
                TableColumn(name="DATE", datatype="DATE"),
                TableColumn(name="LOCATION", datatype="VARCHAR"),
                TableColumn(name="TEMP_C", datatype="NUMBER"),
                TableColumn(name="TEMP_F", datatype="NUMBER"),
            ],
        ),
        mode=CreateMode.or_replace,
    )

    schema.functions.create(
        ServiceFunction(
            name="convert_udf",
            arguments=[FunctionArgument(name="input", datatype="REAL")],
            returns="REAL",
            service=os.environ["CONVERT_SERVICE_NAME"].upper(),
            endpoint="convert-api",
            path="/convert",
            max_batch_rows=5,
        ),
        mode=CreateMode.or_replace,
    )

    connection_container_user_role.cursor().execute("""INSERT INTO weather (DATE, LOCATION, TEMP_C, TEMP_F)
                        VALUES 
                            ('2023-03-21', 'London', 15, NULL),
                            ('2023-07-13', 'Manchester', 20, NULL),
                            ('2023-05-09', 'Liverpool', 17, NULL),
                            ('2023-09-17', 'Cambridge', 19, NULL),
                            ('2023-11-02', 'Oxford', 13, NULL),
                            ('2023-01-25', 'Birmingham', 11, NULL),
                            ('2023-08-30', 'Newcastle', 21, NULL),
                            ('2023-06-15', 'Bristol', 16, NULL),
                            ('2023-04-07', 'Leeds', 18, NULL),
                            ('2023-10-23', 'Southampton', 12, NULL);""")

    for col1 in connection_container_user_role.cursor().execute(
        "SELECT convert_udf(12) as conversion_result;"
    ):
        print("{0}".format(col1))

    connection_container_user_role.cursor().execute("""UPDATE WEATHER
                    SET TEMP_F = convert_udf(TEMP_C);""")

    for col1, col2, col3, col4 in connection_container_user_role.cursor().execute(
        "SELECT * FROM WEATHER;"
    ):
        print("{0} {1} {2} {3}".format(col1, col2, col3, col4))

finally:
    connection_container_user_role.close()
