## Setup


### navigate to proper directory 

```bash
cd 01_getting_started/
```

### sync dependencies

```bash
uv sync
```

### activate environment

```bash
source .venv/bin/activate
```

### to use notebooks

```
uv add --dev ipykernel
uv run python -m ipykernel install --user --name=getting-started
```