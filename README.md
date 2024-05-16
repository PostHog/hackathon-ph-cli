# hackathon-ph-cli

hackathon 2024 - ph-cli

## Dev

Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
export PATH=$PATH:./venv/bin/ph
```

Run

```bash
ph
```

## Configuration

Env. variables

`PH_ENDPOINT` defaults to `app.dev.posthog.dev`.

`PH_API_PROTOCOL_WEB` defaults to `https`.

`PH_API_PORT_WEB` defaults to None. If None, it will be ignored.

`PH_API_TOKEN` defaults to None. If None, it will try to read the conf. file `~/.posthog/credentials.json`.

`PH_LOG_LEVEL` defaults to `INFO`.

## Usage

```bash
ph login
ph logout
ph organization # change org if already logged in
ph project # change project if already logged in
ph flags list
ph flags create {key} -d {description} -p {rollout-percentage} # rollout-percentage defaults to 100
ph flags delete {key}
ph flags disable {key}
ph flags enable {key}
ph flags update {key} -d {description} -p {rollout-percentage} # rollout-percentage defaults to 100
```
