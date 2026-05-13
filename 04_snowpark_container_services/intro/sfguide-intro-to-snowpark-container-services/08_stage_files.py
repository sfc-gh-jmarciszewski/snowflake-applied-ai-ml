#!/usr/bin/env python3
import os
import tempfile

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


def render_yaml(src_path):
    image_url_base = (
        f"{os.environ['SNOWFLAKE_ACCOUNT_REGISTRY']}"
        f"/{os.environ['SNOWFLAKE_DATABASE']}"
        f"/{os.environ['SNOWFLAKE_SCHEMA']}"
        f"/{os.environ['IMAGE_REPO_NAME']}"
    ).lower()

    with open(src_path, "r") as f:
        content = f.read()

    content = content.replace("__IMAGE_URL_BASE__", image_url_base)
    content = content.replace("__IMAGE_TAG__", os.environ["IMAGE_TAG"])
    return content


try:
    root = Root(connection_container_user_role)
    stage = root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].stages[os.environ["STAGE_SPECS"]]

    spec_files = [
        f"./src/jupyter-snowpark/{os.environ['JUPYTER_SPEC_FILE']}",
        f"./src/convert-api/{os.environ['CONVERT_SPEC_FILE']}",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        for spec_path in spec_files:
            rendered = render_yaml(spec_path)
            filename = os.path.basename(spec_path)
            tmp_path = os.path.join(tmp_dir, filename)

            with open(tmp_path, "w") as f:
                f.write(rendered)

            stage.upload_file(tmp_path, "/", auto_compress=False, overwrite=True)
            print(f"Uploaded {filename} (rendered)")

    stageFiles = stage.list_files()
    for stageFile in stageFiles:
        print(stageFile)

finally:
    connection_container_user_role.close()
