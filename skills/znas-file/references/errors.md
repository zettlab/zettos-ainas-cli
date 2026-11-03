# File Error Reference

- `60004`: invalid path traversal; use virtual entry + returned next path.
- `64000`: request fields missing/wrong type; check command `--help`.
- `64001`: root path rejected; physical-path APIs should use `/zettos/pool/...`.
- `62001`: quota error; check pool quota with `settings storage-pool list`; for teams, verify team folder quota allocation.
- `62002`: space full; free space or move data to a path with available quota.
- `65002`: AI/DB search failed; prefer high-level `znas search --query ...`.
