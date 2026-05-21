# 01 - End-to-End ML Workflow in Snowflake

## Source:

blog post: https://www.snowflake.com/en/developers/guides/end-to-end-ml-workflow

* repo linked at top of blog post: https://github.com/Snowflake-Labs/sfquickstarts/tree/master/site/sfguides/src/end-to-end-ml-workflow 
* rep linked in mid blog post and cloned for the tutorial https://github.com/Snowflake-Labs/sfguide-build-end-to-end-ml-workflow-in-snowflake


Contents 

* [src/01_train_deploy_monitor_ML_in_snowflake.ipynb](src/01_train_deploy_monitor_ML_in_snowflake.ipynb)


@TODO - clean this up 

## Setup: uv virtual env + Jupyter kernel

These steps create a `uv`-managed virtual environment, register it as a Jupyter kernel, and start a notebook server that VS Code or Cortex Code Desktop can attach to.

### 1. Create and activate the venv

```bash
cd 01_e2e_ml/
uv sync
source .venv/bin/activate
```


### 3. Register the venv as a named Jupyter kernel

This makes the kernel discoverable by any local Jupyter client (VS Code, Cortex Code Desktop, JupyterLab):

```bash
uv run python -m ipykernel install \
  --user \
  --name e2e-ml \
  --display-name "Python (e2e-ml)"
```

Verify:

```bash
uv run jupyter kernelspec list
```

### 4a. Option A — Connect VS Code / Cortex Code directly (no server needed)

After step 3, the kernel `Python (e2e-ml)` shows up in the kernel picker:

* **VS Code**: open the `.ipynb`, click the kernel selector (top-right) → "Select Another Kernel" → "Jupyter Kernel" → `Python (e2e-ml)`.
* **Cortex Code Desktop**: open the notebook, use `notebook_get_kernel_status` / kernel picker, choose `Python (e2e-ml)`.

### 4b. Option B — Run a Jupyter server and connect to it remotely

Useful if you want a long-lived server, port forwarding, or to share state across clients.

Start the server from inside `01_e2e_ml/`:

```bash
uv run jupyter lab \
  --no-browser \
  --ServerApp.token=<your-token> \
  --port 8888
```

The console prints a URL like:

```
http://localhost:8888/lab?token=<your-token>
```

Connect from a client:

* **VS Code**: Command Palette → "Jupyter: Specify Jupyter Server for Connections" → paste the full URL (including token).
* **Cortex Code Desktop**: in the kernel picker choose "Existing Jupyter Server" → paste the URL.

### 5. Verify

Inside the notebook, run:

```python
import sys, snowflake
print(sys.executable)         # should point to .venv/bin/python
print(snowflake.__file__)
```

### Cleanup

Remove the registered kernel when done:

```bash
jupyter kernelspec uninstall e2e-ml
```
