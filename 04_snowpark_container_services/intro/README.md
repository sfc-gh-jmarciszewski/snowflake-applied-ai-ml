# Intro to Snowpark Container Services

## Source

Blog post [Intro to Snowpark Container Services](https://www.snowflake.com/en/developers/guides/intro-to-snowpark-container-services/)

Repo: https://github.com/Snowflake-Labs/sfguide-intro-to-snowpark-container-services


## Setup


### clone repo (first time only)

navigate to correct directory 

```bash
cd 04_snowpark-container-services/intro 
```

clone repo

```bash
git clone https://github.com/Snowflake-Labs/sfguide-intro-to-snowpark-container-services.git
```

manual steps:

* removed .git directory 
* moved all sql files to seperate directory to focus on python
* misc updates to steps to use environment variables and snow cli

### setup Python environment

```bash
cd sfguide-intro-to-snowpark-container-services
```

```bash
uv sync
```

This will create a `.venv` using the `pyproject.toml` and install all dependencies (including `python-dotenv`, `snowflake`, `docker`, etc.).

### activate python environment

```bash
source .venv/bin/activate
```

### Setup env vars

Copy the example and edit with your values:

```bash
cp .env.example .env
```

Edit `.env` to set your Snowflake connection name, account registry, local docker prefix, etc.

Then source it for shell commands:

```bash
source .env
```

This provides the following variables for both Python scripts (via `python-dotenv`) and shell commands:

| Variable | Purpose |
|----------|---------|
| `SNOWFLAKE_CONNECTION_NAME` | Named connection from `~/.snowflake/connections.toml` |
| `SNOWFLAKE_DATABASE` | Target database |
| `SNOWFLAKE_SCHEMA` | Target schema |
| `SNOWFLAKE_WAREHOUSE` | Warehouse |
| `SNOWFLAKE_ROLE_ADMIN` | Admin role (e.g. `ACCOUNTADMIN`) |
| `SNOWFLAKE_ROLE_USER` | User role for SPCS operations |
| `COMPUTE_POOL_NAME` | Compute pool name |
| `IMAGE_REPO_NAME` | Image repository name |
| `SNOWFLAKE_ACCOUNT_REGISTRY` | Registry hostname |
| `LOCAL_REPO_PREFIX` | Your local docker image prefix |
| `IMAGE_TAG` | Image tag (e.g. `dev`) |
| `JUPYTER_IMAGE_NAME` / `CONVERT_IMAGE_NAME` | Image names per service |
| `JUPYTER_SPEC_FILE` / `CONVERT_SPEC_FILE` | YAML spec filenames |

Derived variables (set after sourcing `.env`):

```bash
export IMAGE_URL_BASE="${SNOWFLAKE_ACCOUNT_REGISTRY}/${SNOWFLAKE_DATABASE}/${SNOWFLAKE_SCHEMA}/${IMAGE_REPO_NAME}"
export JUPYTER_IMAGE_URL="${IMAGE_URL_BASE}/${JUPYTER_IMAGE_NAME}:${IMAGE_TAG}"
export CONVERT_IMAGE_URL="${IMAGE_URL_BASE}/${CONVERT_IMAGE_NAME}:${IMAGE_TAG}"

echo "IMAGE_URL_BASE:     " $IMAGE_URL_BASE
echo "JUPYTER_IMAGE_URL:  " $JUPYTER_IMAGE_URL
echo "CONVERT_IMAGE_URL:  " $CONVERT_IMAGE_URL
```

### setup Snowflake - 00_setup.py

Run `00_setup.py` to setup role, database, warehouse, and stages:

```bash
python 00_setup.py
```

### setup SPCS - 01_snowpark_container_services_setup.py

Creates compute pool, image repository, network rule, and external access integration:

```bash
python 01_snowpark_container_services_setup.py 
```

### snowCLI - authenticate to image registry

```bash
snow spcs image-registry login --connection $SNOWFLAKE_CONNECTION_NAME
```

## Build and run jupyter service 

navigate to the directory of the dockerfile 

```bash
cd src/jupyter-snowpark
```

Build image:

```bash
docker build --platform=linux/amd64 -t $LOCAL_REPO_PREFIX/$JUPYTER_IMAGE_NAME:latest .
```

```bash
docker image list
```

Test running container locally:

```bash
docker run -d -p $JUPYTER_PORT:$JUPYTER_PORT --name $JUPYTER_IMAGE_NAME $LOCAL_REPO_PREFIX/$JUPYTER_IMAGE_NAME:latest
```

Open up a browser and navigate to localhost:8888/lab to validate service working.

Once validated, stop the container:

```bash
docker stop $JUPYTER_IMAGE_NAME
```


### Push Image

Reauthenticate if needed:

```bash
snow spcs image-registry login --connection $SNOWFLAKE_CONNECTION_NAME
```

Tag image:

```bash
docker tag "$LOCAL_REPO_PREFIX/$JUPYTER_IMAGE_NAME:latest" $JUPYTER_IMAGE_URL
```

verify tagging

```bash
docker image list
```

push image 

```bash
docker push $JUPYTER_IMAGE_URL
```

```bash
snow spcs image-repository list-images $SNOWFLAKE_DATABASE.$SNOWFLAKE_SCHEMA.$IMAGE_REPO_NAME
```

### Configure and push Spec YML

The YAML spec files in `src/` use `__IMAGE_URL_BASE__` and `__IMAGE_TAG__` placeholders that get resolved by `08_stage_files.py` at upload time.

Upload rendered specs to stage:

```bash
cd ../../
python 08_stage_files.py
```

#### validate upload 

```bash
snow stage list-files @"${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.SPECS" --role $SNOWFLAKE_ROLE_USER
```

### Create and test service 

```bash
python 02_jupyter_service.py
```

sample result:

```txt
PENDING

name='jupyter-snowpark' port=8888 port_range=None protocol='HTTP' is_public=True ingress_url='Endpoints provisioning in progress... check back in a few minutes'

```

```bash
snow spcs service list-endpoints $SNOWFLAKE_DATABASE.$SNOWFLAKE_SCHEMA.$JUPYTER_SERVICE_NAME --role $SNOWFLAKE_ROLE_USER
```

Now open the ingress_url in your browser and login with your snowflake credentials. You should see a JupyterLab environment home screen. 



## Temperature Conversion REST API

```bash
cd src/convert-api
```

### build image

```bash
docker build --platform=linux/amd64 -t $LOCAL_REPO_PREFIX/$CONVERT_IMAGE_NAME:latest .
```

### validate and test locally


```bash
docker image list
```

run container 

```bash
docker run -d -p $CONVERT_PORT:$CONVERT_PORT --name $CONVERT_IMAGE_NAME $LOCAL_REPO_PREFIX/$CONVERT_IMAGE_NAME:latest
```

send API request

```bash
curl -X POST -H "Content-Type: application/json" -d '{"data": [[0, 12],[1,19],[2,18],[3,23]]}' http://localhost:$CONVERT_PORT/convert
```

tag image 

```bash
docker tag $LOCAL_REPO_PREFIX/$CONVERT_IMAGE_NAME:latest $CONVERT_IMAGE_URL
```

validate tag

```bash
docker image list
```

confirm and/or re-login to spcs 

```bash
snow spcs image-registry login --connection $SNOWFLAKE_CONNECTION_NAME
```

push image to registry

```bash
docker push $CONVERT_IMAGE_URL
```

```bash
snow spcs image-repository list-images $SNOWFLAKE_DATABASE.$SNOWFLAKE_SCHEMA.$IMAGE_REPO_NAME
```


### upload yaml 

Already handled by `08_stage_files.py` above (uploads both specs). If you need to re-upload just the convert-api spec:

```bash
cd ../../
python 08_stage_files.py
```

#### validate upload 

```bash
snow stage list-files @"${SNOWFLAKE_DATABASE}.${SNOWFLAKE_SCHEMA}.SPECS" --role $SNOWFLAKE_ROLE_USER
```


### Create and Test the Service Function

run [03_rest_service.py](sfguide-intro-to-snowpark-container-services/03_rest_service.py)


```bash
cd ../../
python 03_rest_service.py
```

sample response

```txt
RUNNING
 * Serving Flask app 'convert-app.py' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:9090
 * Running on http://10.244.1.204:9090
Press CTRL+C to quit

(53.6,)
2023-03-21 London 15 59
2023-07-13 Manchester 20 68
2023-05-09 Liverpool 17 63
2023-09-17 Cambridge 19 66
2023-11-02 Oxford 13 55
2023-01-25 Birmingham 11 52
2023-08-30 Newcastle 21 70
2023-06-15 Bristol 16 61
2023-04-07 Leeds 18 64
2023-10-23 Southampton 12 54
```

check status:

```bash
snow spcs service list-endpoints $SNOWFLAKE_DATABASE.$SNOWFLAKE_SCHEMA.$CONVERT_SERVICE_NAME --role $SNOWFLAKE_ROLE_USER
```


### Suspending / pausing 

To pause compute temporarily, run: 

```bash
python 05_stop_snowpark_container_services_and_suspend_compute_pool.py
```

Or via CLI:

```bash
snow spcs compute-pool stop-all $COMPUTE_POOL_NAME --role $SNOWFLAKE_ROLE_USER
snow spcs compute-pool suspend $COMPUTE_POOL_NAME --role $SNOWFLAKE_ROLE_USER
```

This is if you no longer need the services and compute pool up and running, we can stop the services and suspend the compute pool so that we don't incur any cost (Snowpark Container Services bill credits/second based on the compute pool's uptime, similar to Virtual Warehouse billing):


To resume, run the below. Services on the pool will automatically restart once the pool is active again.

```bash
snow spcs compute-pool resume $COMPUTE_POOL_NAME --role $SNOWFLAKE_ROLE_USER
```

### Cleanup (DANGER AREA)

Run the following to delete / teardown all objects created.

```bash
## python 04_teardown.py
```
