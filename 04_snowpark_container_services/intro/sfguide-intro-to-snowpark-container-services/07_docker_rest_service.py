#!/usr/bin/env python3
import os
import re
import docker

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

    repos = root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].image_repositories
    repo = repos[os.environ["IMAGE_REPO_NAME"]].fetch()

    pattern = r'^[^/]+'
    repository_url = repo.repository_url
    match = re.match(pattern, repository_url)
    registry_hostname = match.group(0)

    client = docker.from_env()

    local_tag = f"{os.environ['LOCAL_REPO_PREFIX']}/{os.environ['CONVERT_IMAGE_NAME']}:latest"
    remote_tag = f"{repository_url}/{os.environ['CONVERT_IMAGE_NAME']}:{os.environ['IMAGE_TAG']}"

    client.images.build(path='src/convert-api', platform='linux/amd64', tag=local_tag)
    client.images.list()

    container = client.containers.run(image=local_tag, detach=True, ports={int(os.environ['CONVERT_PORT']): int(os.environ['CONVERT_PORT'])})

    os.system(f"""curl -X POST \
                -H "Content-Type: application/json" \
                -d '{{"data": [[0, 12],[1,19],[2,18],[3,23]]}}' \
                http://localhost:{os.environ['CONVERT_PORT']}/convert""")

    image = next(i for i in client.images.list() if local_tag in i.tags)
    image.tag(f"{repository_url}/{os.environ['CONVERT_IMAGE_NAME']}", os.environ['IMAGE_TAG'])

    client.api.push(remote_tag)

    images = root.databases[os.environ["SNOWFLAKE_DATABASE"]].schemas[os.environ["SNOWFLAKE_SCHEMA"]].image_repositories[os.environ["IMAGE_REPO_NAME"]].list_images_in_repository()
    for img in images:
        print(img)

    container.stop()

finally:
    connection_container_user_role.close()
