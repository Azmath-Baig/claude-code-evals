Make `load_config` also handle YAML files (`.yaml` / `.yml`), picking the loader
from the file extension. JSON must keep working exactly as it does now.

Use the standard library only — don't add a dependency (no `pyyaml`). The config
files are simple: flat `key: value` pairs, one per line, where each value is a
string, integer, float, or boolean (`true` / `false`).
