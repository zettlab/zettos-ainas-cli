# Agent Command Rules (znas file)

Quick-reference for any agent (Claude Code, Codex, etc.) calling `znas` file commands.
Read this before generating `znas file ...` invocations.

## Preferred Commands

| Intent | Use this | Key params |
|--------|----------|-----------|
| Rename | `znas file rename` | `--json '{"old_path":"...","new_path":"..."}'` |
| Delete | `znas file delete` | `--json '{"paths":["..."]}'` (array) |
| Upload | `znas upload` | `--local <local-file> --remote <nas-dir>` |
| Browse folder | `znas file root list` | `--json '{"path":"...","size":50,"index":0}'` |
| Browse recycle | `znas file root list` | `--json '{"path":"/recycle","size":50,"index":0}'` |
| List favorites | `znas file favorites list` | `--params '{"index":0,"size":50}'` |
| Read text file | `znas file file read` | `--params '{"path":"..."}'` |
| Create subfolder | `znas file folder create` | `--json '{"path":"<parent-path>/<new-folder-name>"}'` (full target path) |
| Remove favorite | `znas file favorites remove` | `--json '{"paths":["..."]}'` |
| Search | `znas search` | `--query '<text>'` (supports `--type`, `--tag`, `--rate`, `--scope`, `--mode` and more) |
| Create tag | `znas file tag create` | `--json '{"name":"..."}'` |
| List tags | `znas file tag list` | `--params '{}'` (path optional) |
| Tag a file | `znas file tag edit-file-tag` | `--json '{"path":"...","tags":[{"id":N,"name":"..."}]}'` |
| Delete tag | `znas file tag delete` | `--json '{"tag_ids":[N]}'` (CLI also accepts legacy `id`) |
| Clear file tags | `znas file tag edit-file-tag` | `--json '{"path":"...","tags":[]}'` |
| Rate a file | `znas file rate update` | `--json '{"path":"...","rate_level":5}'` (0–5; CLI also accepts legacy `rate`) |
| Verify rating | `znas file root detail` | `--params '{"path":"..."}'` then inspect `data.rate.rate_level` |
| Read text file | `znas file file read` | `--params '{"path":"..."}'` |
| Download file | `znas file file raw` | `--params '{"path":"..."}' -o <file>` |

## Forbidden / Wrong Patterns

| Wrong command | Why it fails | Correct alternative |
|--------------|-------------|-------------------|
| `file file edit --json '{"new_name":"..."}'` for rename | `file edit` is content-edit only; rename fields are silently ignored → 65000 | `file rename` (alias for `file root rename`) |
| `file file delete ...` | Route does not exist | `file delete` (alias for `file root delete`) |
| `upload --file X --target Y` | Wrong param names → unrecognized argument | `upload --local X --remote Y` |
| `favorites list` with no params | Backend requires pagination → 64000 PARAM_ERROR | `favorites list --params '{"index":0,"size":50}'` |
| `file root list --json '{"path":"/favorites",...}'` | `/favorites` is not a virtual root | `file favorites list --params '{"index":0,"size":50}'` |
| `file recycle list ...` | No such command exists | `file root list --json '{"path":"/recycle",...}'` |
| `file favorites delete ...` | No such command | `file favorites remove --json '{"paths":["..."]}'` |
| `folder create --json '{"path":"<parent>","name":"X"}'` | Backend silently ignores `name`, returns 200 but creates nothing | `folder create --json '{"path":"<parent>/X"}'` (full target path) |
| `recycle delete --json '{"is_all":false,"paths":["..."]}'` | Selective permanent delete returns 200 but does nothing | `recycle delete --json '{"is_all":true}'` (clear all only) |

## Upload Semantics

- Params: `--local` (local file path) and `--remote` (NAS target path). NOT `--file`/`--target`.
- If `--remote` ends with `/`, local filename is auto-appended.
- If `--remote` last component has no file extension but local file does, CLI treats it as a directory and appends the local filename automatically.
- Always use a server-returned concrete path (e.g. `/zettos/pool/1/teams/cjz/DATA/cjz`) for `--remote`.

## Alias Design

`file rename` and `file delete` are thin aliases:

- `file rename` → dispatches to `file root rename` (PUT /v1/rename)
- `file delete` → dispatches to `file root delete` (DELETE /v1)

Both alias and full-path forms work identically. Aliases exist because agents naturally think operation-first (`rename`), not route-first (`root rename`).

## Parameter Gotchas

| Command | Gotcha |
|---------|--------|
| `favorites list` | Requires `index` + `size` even though it's a list endpoint |
| `file file edit` | Content-edit only; cannot rename/move; for rename use `file rename` |
| `file delete` | CLI auto-injects `delete_mod:1` (move to recycle). To permanently delete, pass `"delete_mod":0` explicitly |
| `recycle restore` | Needs `paths` array for partial restore, or `is_all: true` for all |
| `recycle delete` | Selective `paths` param silently ignored by backend. Only `is_all:true` works (clears entire recycle) |
| `root set-base-path` | For top-level `/personal` or `/teams` create only; requires pool selection first |
| `file delete` | `paths` must be a JSON array, even for a single file |
| `folder create` | `path` is the **full path of the new folder**, not parent + name. `{"path":"/zettos/.../mydir"}` not `{"path":"/zettos/...","name":"mydir"}` |
| `favorites remove` | Command is `remove`, not `delete` |
| `tag edit-file-tag` | `tags: []` is valid and means "clear all tags from this file" |
| `tag delete` | Backend expects `tag_ids: []`; CLI maps legacy `id` / `tagIds` to `tag_ids` |
| `rate update` | Current backend uses `rate_level`; CLI maps legacy `rate` to `rate_level` |
| `share list` | `file_paths` field in response is base64-encoded; decode before display |

## Virtual Paths (Quick Rules)

Valid roots: `/personal`, `/teams`, `/shares`, `/recycle`, `/shared/<user>`, `/users`, `/appfolder`.

NOT a root: `/favorites` — use `favorites list` command instead.

After first listing, always reuse exact `data.content[*].path` from the response. Never manually concatenate path segments.
