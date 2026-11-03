---
name: znas-file
description: "Call zettos-file APIs through znas for CRUD, upload, share, and metadata operations."
---

# znas file

> Prerequisite: read `../znas-shared/SKILL.md`.

## References

- `./references/agent-rules.md` — **read first**: DO/DON'T table, forbidden patterns, parameter gotchas
- `./references/commands.md`
- `./references/errors.md`
- `./references/workflows.md`

## Capability Summary

- Browse and query NAS files (`list/detail/spaces/history/search/exif`).
- High-level user search via `znas search` — supports hybrid keyword+AI, **plus rich filters**: `--type`, `--tag`, `--rate`, `--city`, `--equipment`, `--created-from/to`, `--file-size-min/max`, `--rgb`, `--scope`, `--mode`.
- NAS knowledge QA context retrieval via `znas ask` (`/v1/file/aiText`).
- High-level copy via `znas copy` (task `file_op` with CLI guardrails).
- File/folder CRUD (`create/edit/rename/delete`).
- Uploads through the stable batch upload endpoint + high-level `znas upload`.
- Share operations (auth and noauth-share routes).
- Remote-access prerequisite management for external sharing.
- **Tag management**: create/rename/delete tags, tag/untag files, search by tag.
- **Rating**: rate files 0–5 stars, search by rating.
- **Favorites**: add/remove favorites, list favorites.
- **Recycle bin**: browse, restore, clear.
- **EXIF**: device/address tree and search.
- **Content access**: read text files, download raw files, AI-powered text retrieval.

## Onboarding Script (Use This in Conversation)

1. Ask for gateway URL (if unknown).
2. Run `znas --base-url <gateway> auth probe`.
3. Run login command.
4. Discover spaces: `znas file root spaces`.
5. Start from virtual read-only paths (`/personal`, `/teams`, `/shares`, `/recycle`), not `/`.
6. For user search intents, run `znas search --query <text>` first (global scope by default).
7. For NAS knowledge Q&A intents, run `znas ask --question <text>`.
8. Before external sharing, check `znas remote-access status` and enable it if needed.
9. For copy intents, prefer `znas copy` instead of low-level task routes.
10. Only then perform write/delete/upload/share actions after explicit confirmation.

## Freshness Rules (Critical)

1. For current file facts, rerun a `znas` read command before answering.
2. This applies to:
   - current spaces or virtual roots
   - current folder entries or item counts
   - current search hits
   - current share list / favorites / tags / rate / recycle state
3. If the user asks follow-ups like `现在有几个`, `现在还有吗`, `我现在能打开哪些地方`, or says they just uploaded, deleted, moved, or shared something, treat earlier results as stale.
4. Previous results may supply an exact `path`, `share id`, or filter values for the next query.
   - They do not justify reusing the old count/list/status.
5. If a write or external action just happened, re-read and then answer.
   - request accepted is not the same as latest verified state

## Copy Workflow (Critical)

User-facing copy should go through `znas copy`, not `znas task file-op create`, unless you are debugging raw backend task payloads.

1. Preferred command:
   - `znas copy --source '<path>' --target '<directory>' --on-conflict skip`
2. `--source` is repeatable:
   - `znas copy --source '/teams/demo/a.txt' --source '/teams/demo/b.txt' --target '/teams/demo/archive'`
3. `--target` is the destination directory, not a renamed final file path.
4. Conflict modes:
   - `skip`: keep destination item and skip conflicting copy
   - `copy`: create a renamed duplicate when names conflict
   - `overwrite`: replace destination item
5. CLI default is `skip` because there is no interactive popup flow in CLI mode.
6. Guardrails:
   - cannot copy to the same directory
   - cannot copy a folder into itself
   - cannot copy a folder into one of its subdirectories
7. After copy submission, re-list the destination if the user asks for the latest contents or counts.

## Content Access Decision (Critical)

When user asks to read/summarize/classify by content, choose one path:

0. Local Access Gate: once a physical path (`/zettos/...`) is known, check local accessibility first.
   - if `local_readable=true` (from `znas search` result), use local tools first.
   - do not start with `znas file file raw` on same machine.
1. Local-first: if file is already accessible in current runtime, use local tools first.
2. Remote text-like content: `znas file file read --params '{"path":"<full-path>"}'`
3. Remote binary/raw content: `znas file file raw --params '{"path":"<full-path>"}' -o <local-file>`
4. NAS knowledge QA retrieval: `znas ask --question '<natural-language-question>'`
5. Low-level equivalent: `znas file file ai-text --params '{"question":"总结最近账单变化"}'`
   - `ai-text` is not path-based read; `question` is required.

## Path Traversal Hard Rules (Read Once)

1. Resolve a native Files app copied `/This_NAS/...` path before any search:
   `znas file root virtual-to-real --params '{"path":"<complete-copied-path>"}'`.
   It identifies an exact file or folder and must not be used as a
   `znas search --query` value.
2. Only first listing can use virtual roots (`/personal`, `/teams`, `/shares`, `/recycle`).
3. From second listing onward, always use exact `data.content[*].path` returned by previous response.
4. Do not manually concatenate repeated virtual segments.
   - wrong: `/teams/test-space/test-space`
   - correct: list `/teams` first, then copy returned `path` exactly.
5. Exception for top-level folder creation:
   - `/personal` and `/teams` root-level create flows cannot blindly reuse a child path returned by `list`
   - the target pool must be checked and, when needed, chosen first
   - after the pool is chosen, use `znas file root set-base-path` instead of guessing a physical path from aggregate list output

## Virtual Path Policy (Critical)

- Never start first listing from `path="/"` for normal NAS usage.
- First listing should use one of: `/personal`, `/teams`, `/shares`, `/recycle`.
- Use `root spaces` to discover server-provided `ReqInitPath` and follow it.
- `/users` and `/appfolder` are usually admin-oriented.
- `/shared/<username>` is valid for "I shared" tree exploration.
- `/favorites` is NOT a valid virtual root — use `znas file favorites list --params '{"index":0,"size":50}'` instead.

Traversal rule:

- After first virtual-root listing, always use exact returned `data.content[*].path` for next-level calls.
- Do not manually append duplicate folder names like `/teams/<x>/<x>` unless response path explicitly contains it.

Virtual-to-real mapping is handled server-side:

```bash
znas file root virtual-to-real \
  --params '{"path":"/This_NAS/XHXH/录屏资料/demo.mp4"}'
```

For this dedicated route, the CLI maps the native display form to the
file-service form first: `/This_NAS/Teams/...` becomes `/teams/...`,
`/This_NAS/appfolder/...` becomes `/appfolder/...`, and
`/This_NAS/<user>/...` becomes `/users/<user>/...`. Preserve returned
`data.real_path` exactly and do not search for a same-named replacement.

- `/teams/...` -> `/zettos/pool/<pool-id>/teams/<team>/DATA/...`
- `/personal/...` -> `/zettos/pool/<pool-id>/users/<me>/DATA/<me>/...`
- `/users/<name>/...` -> `/zettos/pool/<pool-id>/users/<name>/DATA/...`
- `/shares/...` -> `/zettos/pool/<pool-id>/users/<other>/shared/...`
- `/appfolder/...` -> `/zettos/pool/<pool-id>/virtual_machine/docker/DATA/installed/...`

## Which Routes Actually Resolve Virtual Roots (Measured)

Virtual roots resolve on **directory-level** routes only. File-level routes need a
concrete path. Measured on a device (2026-08-23), same file, same credentials:

| route | `/personal/<file>` | resolved real path |
|---|---|---|
| `file root list` (POST /v1/list) | 200 | 200 |
| `file root virtual-to-real` | 200 | — |
| `file file read` (GET /v1/file/str) | **60016** | 200 |
| `file file raw` (GET /v1/file/raw) | **60016** | 200 |
| `file root detail` (GET /v1) | **60004** | 200 |

The codes are misleading: `60016` reads as "no read permission" and `60004` as
"directory does not exist", but **neither is what happened**. The exact same
credentials read the exact same file successfully once the path is resolved, and
the result is identical whether the caller authenticates with a user token or
with the loopback `USER_ID` mode. It is a path-resolution boundary, not a
permission boundary. Chasing the code text leads to auditing accounts and ACLs
and finding nothing.

So for any read of a user file:

```bash
# 1) resolve (either of these)
znas file root list --json '{"path":"/personal"}'          # take data.content[*].path
znas file root virtual-to-real --params '{"path":"/personal"}'   # take data.real_path

# 2) read with the concrete path
znas file file read --params '{"path":"/zettos/pool/1/users/<me>/DATA/<me>/<file>"}'
```

## Writing Into User Space (Measured)

Same resolution boundary applies on the write side, and getting it wrong leaves a file
the **owner cannot delete**.

Measured on a device (2026-08-23):

| attempt | result |
|---|---|
| `POST /v1/file` with `path: /personal/x.md` | **60017** (`FILE_PERM_WRITE_ERROR`) |
| `POST /v1/file` with the resolved real path | 200, and the owner can delete it afterwards |
| shell redirect / `write_file`-style bash landing | file appears, but the owner **cannot delete it** |

The last row is the one that costs you later. A file written straight to the filesystem
takes its mode from the process umask (022 → 0644). In a user directory carrying default
ACLs that collapses the ACL **mask** to `r--`, which downgrades every named entry —
**including the owner's own** — to read-only:

```
user:<owner>:rwx   #effective:r--     ← owner cannot write or delete
mask::r--
```

`ls -l` does not show this. Only `getfacl` reveals the `#effective:` column. The file
service then refuses the owner's own delete with `60010 FILE_PERM_ERROR`, which reads as
an account problem and sends you auditing roles that are perfectly fine.

So, for anything that lands in the user's space:

```bash
# 1) resolve the parent to a real path
znas file root list --json '{"path":"/personal"}'        # take data.content[*].path

# 2) write through the file service, never through a shell redirect
znas file file create --json '{"path":"/zettos/pool/<id>/users/<me>/DATA/<me>/report.md","content":"..."}'
```

Writing through the file service also keeps the file index correct. A shell redirect
bypasses it, which is why the repo rule says NAS file operations go through `znas` only.

## Top-Level Folder Create Guardrail (Critical)

This rule is specific to creating a new folder directly under `/personal` or `/teams`.

1. For `/personal` root-level create, follow the frontend flow:
   - prefer `znas settings storage-pool user-pools`
   - if that route is unavailable in the current environment, fall back to `znas settings storage-pool list`
   - after the pool is chosen, call `znas file root set-base-path --json '{"folder_name":"<name>","pool_name":"<pool>","type":2}'`
2. For `/teams` root-level create, follow the frontend flow:
   - refresh with `znas settings storage-pool list`
   - after the pool is chosen, call `znas file root set-base-path --json '{"folder_name":"<name>","pool_name":"<pool>","type":1,"quota_size":-1}'` unless a quota was explicitly requested
3. Eligible pools are only those verified as healthy/writable on the current backend.
   - `status=0` (`ACTIVE`) is required when using `storage-pool list`
   - if the writable file-system state cannot be verified from current fields, do not guess
4. If multiple eligible pools exist, apply **standing pool preference**:
   - if the user has already chosen a pool earlier in this conversation, reuse that pool automatically
   - if no prior choice exists, ask the user which pool to use
   - if only one eligible pool exists, auto-select it without asking
   - when auto-selecting or reusing, briefly mention which pool is being used (e.g., "我用 pool_1 来创建")
   - the user can override at any time by saying "换到 pool_2" or specifying a pool explicitly
   - this preference is conversation-scoped, not persistent across sessions
5. Do not pick `pool_1` or any other pool just because `/personal` or `/teams` listing happened to return child paths under that pool.
   - aggregate `/personal` or `/teams` list results may contain entries from multiple pools
   - the chosen pool must remain the chosen pool
6. `znas file root set-base-path` returns the concrete created path in `data.path`.
   - use that returned path for follow-up verification, upload continuation, or later child operations
7. Once the target is already a concrete path returned by the server, such as:
   - `/zettos/pool/.../users/<me>/DATA/<me>/...`
   - `/zettos/pool/.../teams/<team>/DATA/<team>/...`
   the pool is already fixed, so child-folder creation under that path does not need a new pool-selection question.
8. If no healthy writable pool is available, stop and explain that safe creation cannot proceed.

## Preferred Search Workflow

- Default search command: `znas search --query <text>`
- It executes keyword + ai_visual + ai_semantic and merges results.
- ai_visual uses `/v1/list`; ai_semantic uses `/v1/ai/getAiSearchByTypes`.
- Global scope is default; add `--scope` only if user asks.
- If a global search already ran, do not recommend teams/personal/shares reruns by default; recommend refining filters first.
- If request has no `--scope/--path`, state clearly that current result is from global search.
- If user intent is NAS question answering, choose `znas ask --question ...` instead of `znas search`.
- Text filter values for `--tag/--city/--equipment` are auto-resolved to backend IDs.
- If unresolved values exist, CLI reports them in `unresolved_*` fields.
- `filter_status` reports whether each explicit structured filter was applied,
  partially applied, unresolved, or not requested. An applied status describes
  search execution, not an independent per-result attestation.
- `filter_match_confidence=no_structured_filters_requested` means words in
  `--query` remain content/name/topic text; do not claim they became metadata
  filters. `candidates_unverified_filters` means at least one explicit filter
  was unresolved.
- A value explicitly supplied as a tag, city, or equipment filter stays
  structured across attempts. If it is unresolved, do not move it into
  `--query`, split it into substring searches, or retry translated synonyms.
- Each result's `match_channels` records keyword, visual, or semantic retrieval
  evidence. A visual-only match is weak content evidence and does not prove
  metadata such as location, equipment, tag, or time.
- Inspect `attempts` and `result_summary` before answering, and report branch
  failures separately. Describe results as degraded visual candidates only when
  the semantic branch executed and failed, `result_count > 0`, and
  `visual_only_count == result_count`. Otherwise describe the surviving
  evidence from each result's `match_channels`.
- Keep search as one atomic capability. Do not wrap search with presentation,
  selection, or mutation, and do not add a natural-language parser or hidden
  fixed workflow inside the CLI.
- If `--query ''` is used for a filter-only search, CLI skips AI branches and uses the keyword/list filter path only.

## External Share Prerequisite (Critical)

- Before `znas file share create`, run `znas remote-access status`.
- If remote access is disabled, ask whether to enable it first; in an interactive terminal `znas file share create` may prompt to enable it and continue.
- Only answer `yes` after the user agreed to open 外网访问 (`remote access`) for this workflow or test.
- If you are not using the interactive prompt, run `znas remote-access enable` first.
- If the environment requires a custom remote access ID, inspect it with `znas remote-access show-id` and set it with `znas remote-access set-id --id <value>`.
- External sharing should fail closed until remote access is ready; do not treat a returned link as usable unless it opens successfully in a browser.

### Search Filter Reference

`znas search` supports rich filtering beyond bare `--query`. All filters are combinable.

| Filter | Flag | Example | Notes |
|--------|------|---------|-------|
| File type | `--type` | `--type image` | Repeatable. Accepts: image, video, audio, document, or numeric code |
| Tag | `--tag` | `--tag 旅行` | Repeatable. Name auto-resolved to ID |
| Rating | `--rate` | `--rate 5` | Repeatable. Values 0–5 |
| City/Location | `--city` | `--city 上海` | Repeatable. Name auto-resolved to ID |
| Equipment | `--equipment` | `--equipment iPhone` | Repeatable. Name auto-resolved to ID |
| Date range | `--created-from` / `--created-to` | `--created-from 1711900800` | Unix epoch seconds |
| File size | `--file-size-min` / `--file-size-max` | `--file-size-min 1048576` | Bytes |
| Image dimensions | `--width-min` / `--height-min` | `--width-min 1920` | Pixels |
| Color | `--rgb` | `--rgb 255,0,0` | Format: r,g,b |
| Scope | `--scope` | `--scope teams` | global (default), all, teams, personal, shares, recycle, users, path |
| Custom scope path | `--path` | `--path /personal/Documents` | Required when `--scope path`; use an exact visible/resolved path |
| Search mode | `--mode` | `--mode keyword` | hybrid (default), auto, keyword, ai |
| Sort | `--sort-type` / `--sort-order` | `--sort-type 6 --sort-order 1` | Types: 0 name, 1 size, 2 type, 3 imported, 4 modified, 5 color, 6 created, 7 keyword score, 8 AI distance. Order: 0 ascending, 1 descending |
| Sort shortcut | `--sort-type 6 --sort-order 1` | `--sort-type 6 --sort-order 1` | Newest-first / created-time descending |

Invocation discipline:

- Invoke each `znas search` directly as one visible command per attempt.
- Do not hide it inside Python, a shell script, a loop, a pipe, command
  substitution, or an output-capture helper. Those wrappers hide the atomic
  command trace, stderr, and exit status.
- When a date boundary must be computed dynamically, compute that value
  separately and copy the resulting Unix epoch number into the direct search.
- If an exact flag or numeric code is unknown, read `znas search --help` before
  the first attempt instead of guessing and repairing an avoidable error.

Search examples:

```bash
# default: global hybrid search (best for natural language)
znas search --query '猫'

# NAS knowledge question answering (RAG context)
znas ask --question '演讲技巧'

# search only in teams
znas search --query '猫' --scope teams

# search by file type only (no keyword)
znas search --query '' --type image

# search by tag
znas search --query '' --tag 旅行

# search by rating
znas search --query '' --rate 5

# combined filters (text names auto-resolved)
znas search --query '海边' --type image --type audio --tag 旅行 --city 上海 --equipment iPhone --rate 5

# newest-first sort (created time, descending)
znas search --query '' --type video --sort-type 6 --sort-order 1

# keep metadata constraints out of query text
znas search --query '小孩玩车' --type video --equipment iPhone --created-from 1722384000

# pure equipment filter: there is no independent content query
znas search --query '' --type video --equipment 'Leica Q3'

# if Leica Q3 is unresolved, do not retry it as query text or split it into
# `Leica Q3`, `Leica`, or `Q3` searches

# recent files (last 7 days)
znas search --query '' --created-from 1711900800

# bad: sort-order only accepts numeric code, avoid --sort-order desc
znas search --query '' --type image --sort-type 6 --sort-order desc

# keyword-only mode (no AI)
znas search --query 'cjz' --mode keyword
```

### Tag & Rating Workflow

**Tag lifecycle:**
1. Create: `znas file tag create --json '{"name":"旅行"}'` → returns `{id, name}`
2. Tag a file: `znas file tag edit-file-tag --json '{"path":"<file>","tags":[{"id":1,"name":"旅行"}]}'`
3. List tags: `znas file tag list` (global) or `--params '{"path":"..."}'` (scoped)
4. Search by tag: `znas search --query '' --tag 旅行`
5. Remove tags from file: `edit-file-tag` with `"tags":[]`
6. Rename: `znas file tag rename --json '{"id":1,"name":"旅游"}'`
7. Delete: `znas file tag delete --json '{"tag_ids":[1]}'` (CLI also accepts legacy `id`)

**Rating:**
1. Rate: `znas file rate update --json '{"path":"<file>","rate_level":5}'` (0–5, 0 to clear; CLI also accepts legacy `rate`)
2. Verify on current backend: `znas file root detail --params '{"path":"<file>"}'` and inspect `data.rate.rate_level`
3. Search by rating: `znas search --query '' --rate 5`
4. Batch: `znas file rate batch-update --json '{"paths":["<a>","<b>"],"rate_level":4}'` (CLI also accepts legacy `rate`)

## Usage

```bash
znas file <feature> <command> --params '{}' --json '{}'
```

### Common Operations Quick Reference

| Intent | Command | Key params |
|--------|---------|-----------|
| List spaces | `znas file root spaces` | — |
| Browse folder | `znas file root list` | `--json '{"path":"...","size":50,"index":0}'` |
| Create subfolder | `znas file folder create` | `--json '{"path":"<full-path>"}'` |
| Create top-level folder | `znas file root set-base-path` | `--json '{"folder_name":"...","pool_name":"...","type":1\|2}'` (see Top-Level Folder Create Guardrail) |
| **Rename file/folder** | `znas file rename` | `--json '{"old_path":"...","new_path":"..."}'` (alias for `file root rename`) |
| **Delete file/folder** | `znas file delete` | `--json '{"paths":["..."]}'` (array; alias for `file root delete`) |
| Upload | `znas upload` | `--local <local-file> --remote <nas-dir>` |
| Copy | `znas copy` | `--source '<path>' --target '<dir>' --on-conflict skip` |
| Search | `znas search` | `--query '<text>'` |
| Create share | `znas file share create` | `--json '{"file_paths":["..."],"invalid_time":7}'` (check remote-access first) |
| List shares | `znas file share list` | `--params '{"index":0,"size":50}'` |
| Add favorite | `znas file favorites add` | `--json '{"paths":["..."]}'` |
| Remove favorite | `znas file favorites remove` | `--json '{"paths":["..."]}'` |
| Browse recycle bin | `znas file root list` | `--json '{"path":"/recycle","size":50,"index":0}'` |
| Recycle restore | `znas file recycle restore` | `--json '{"paths":["..."],"is_all":false}'` |
| Clear recycle bin | `znas file recycle delete` | `--json '{"is_all":true}'` |
| **Create tag** | `znas file tag create` | `--json '{"name":"..."}'` |
| **List tags** | `znas file tag list` | `--params '{"path":"..."}'` (path optional) |
| **Tag a file** | `znas file tag edit-file-tag` | `--json '{"path":"...","tags":[{"id":N,"name":"..."}]}'` |
| **Rename tag** | `znas file tag rename` | `--json '{"id":N,"name":"new-name"}'` |
| **Delete tag** | `znas file tag delete` | `--json '{"tag_ids":[N]}'` (CLI also accepts legacy `id`) |
| **Rate a file** | `znas file rate update` | `--json '{"path":"...","rate_level":5}'` (0–5; CLI also accepts legacy `rate`) |
| **Verify file rating** | `znas file root detail` | `--params '{"path":"..."}'` then inspect `data.rate.rate_level` |
| **Read text file** | `znas file file read` | `--params '{"path":"..."}'` |
| **Download file** | `znas file file raw` | `--params '{"path":"..."}' -o <local-file>` |
| **EXIF device tree** | `znas file exif tree` | `--params '{"tree_type":1}'` (1=device, 2=address) |
| **AI summaries** | `znas file ai summary-list` | `--json '{"paths":["..."]}'` |

> **Rename/Delete note**: `znas file rename` and `znas file delete` are convenience aliases for `file root rename` / `file root delete`. Both forms work. Do NOT use `file file edit` for rename (that's content-edit only) or look for `file file delete` (it doesn't exist).

Read-first examples:

```bash
znas file root spaces
znas file root list --json '{"path":"/personal","size":50,"index":0}'
znas file root list --json '{"path":"/teams","size":50,"index":0}'
```

High-level copy examples:

```bash
znas copy --source '/teams/test-space/test-a.txt' --target '/teams/test-space/archive' --on-conflict skip
znas copy --source '/teams/test-space/a.txt' --source '/teams/test-space/b.txt' --target '/teams/test-space/archive' --on-conflict copy
```

Low-level search examples (debug/manual calls):

```bash
# keyword search in list (use keyword_search)
znas file root list --json '{"path":"/teams","size":20,"index":0,"keyword_search":"猫"}'

# ai semantic search is internal to `znas search` and not exposed as a direct low-level command
znas search --query '骑自行车' --type audio

# exif search (tree_type: 1=device, 2=address)
znas file exif search --params '{"key":"猫","tree_type":1}'
```

## Features

### ai

- `POST` `summary-list` -> `/v1/ai/summaryList` (auth)

### exif

- `GET` `tree` -> `/v1/exif` (auth)
- `GET` `search` -> `/v1/exif/search` (auth)

### favorites

- `POST` `add` -> `/v1/favorites` (auth)
- `DELETE` `remove` -> `/v1/favorites` (auth)
- `GET` `list` -> `/v1/favorites/list` (auth)

### file

- `POST` `upload` -> `/v1/file/batch_upload` (auth)
- `POST` `batch-upload` -> `/v1/file/batch_upload` (auth)
- `GET` `upload-error` -> `/v1/file/getUploadErr` (auth)
- `GET` `upload-tmp-progress` -> `/v1/file/getUploadTmpProcess` (auth)
- `POST` `upload-tmp-progress-batch` -> `/v1/file/batchGetUploadTmpProcess` (auth)
- `POST` `files-exists` -> `/v1/file/postFilesIsExists` (auth)
- `POST` `create` -> `/v1/file` (auth)
- `PUT` `edit` -> `/v1/file` (auth) — **content edit only**; for rename use `root rename`
- `GET` `read` -> `/v1/file/str` (auth)
- `GET` `raw` -> `/v1/file/raw` (auth)
- `GET` `ai-text` -> `/v1/file/aiText` (auth)
- `POST` `download-to-nas` -> `/v1/file/download_to_nas` (auth)

### folder

- `POST` `create` -> `/v1/folder` (auth)
- `GET` `path-size` -> `/v1/folder/get_path_size` (auth)

### noauth-share

- `GET` `token` -> `/v1/noauth/share/token` (noauth)
- `GET` `comment-list` -> `/v1/noauth/share/comment/list` (noauth)
- `POST` `comment-create` -> `/v1/noauth/share/comment` (noauth)
- `DELETE` `comment-delete` -> `/v1/noauth/share/comment` (noauth)
- `PUT` `comment-update` -> `/v1/noauth/share/comment` (noauth)
- `GET` `info` -> `/v1/noauth/share/info` (noauth)
- `GET` `file-list` -> `/v1/noauth/share/file/list` (noauth)
- `GET` `file-raw` -> `/v1/noauth/share/file/raw` (noauth)
- `GET` `file-raw-str` -> `/v1/noauth/share/file/rawStr` (noauth)
- `GET` `file-detail` -> `/v1/noauth/share/file/detail` (noauth)
- `POST` `file-download` -> `/v1/noauth/share/file/download` (noauth)
- `HEAD` `file-download-head` -> `/v1/noauth/share/file/download` (noauth)
- `GET` `thumbnail` -> `/v1/noauth/share/file/thumbnail` (noauth)
- `GET` `short-side-webp` -> `/v1/noauth/share/file/getShortSideWebP` (noauth)

### rate

- `PUT` `update` -> `/v1/rate` (auth)
- `PUT` `batch-update` -> `/v1/rate/batchUpdateFileRates` (auth)
- `GET` `get` -> `/v1/rate` (auth)

### recycle

> **Browsing**: There is no dedicated `recycle list` command. To browse recycle bin contents, use `znas file root list --json '{"path":"/recycle","size":50,"index":0}'`. Note: empty folders may be permanently deleted by the backend and not appear in recycle.

- `DELETE` `delete` -> `/v1/recycle` (auth)
- `PUT` `restore` -> `/v1/recycle` (auth)

### root

- `GET` `windows-upgrade-version` -> `/v1/getWindowsUpgradeVersion` (auth)
- `GET` `spaces` -> `/v1/spaces` (auth)
- `PUT` `rename` -> `/v1/rename` (auth)
- `POST` `list` -> `/v1/list` (auth)
- `DELETE` `delete` -> `/v1` (auth)
- `GET` `detail` -> `/v1` (auth)
- `GET` `exifraw` -> `/v1/exifraw` (auth)
- `POST` `download` -> `/v1/download` (auth)
- `HEAD` `download-head` -> `/v1/download` (auth)
- `GET` `history` -> `/v1/history` (auth)
- `PUT` `set-base-path` -> `/v1/base_path` (auth)
- `GET` `path-quota` -> `/v1/get_path_quota` (auth)
- `GET` `virtual-to-real` -> `/v1/virtual_path_to_real_path` (auth)

### share

- `GET` `list` -> `/v1/share/list` (auth)
- `POST` `create` -> `/v1/share` (auth)
- `DELETE` `delete` -> `/v1/share` (auth)
- `POST` `create-internal` -> `/v1/share/internal` (auth)
- `DELETE` `delete-internal` -> `/v1/share/internal` (auth)
- `GET` `list-internal` -> `/v1/share/internal` (auth)

### tag

- `POST` `create` -> `/v1/tag` (auth)
- `PUT` `edit-file-tag` -> `/v1/tag/file_tag` (auth)
- `POST` `batch-create-file-tags` -> `/v1/tag/batchCreateFileTags` (auth)
- `DELETE` `delete` -> `/v1/tag` (auth)
- `GET` `list` -> `/v1/tag` (auth)
- `PUT` `rename` -> `/v1/tag/rename` (auth)

## Upload

Use high-level upload for stable batch upload:

```bash
znas upload --local /path/local.bin --remote /zettos/pool/.../target.bin
```

## Command Guardrails / Allowed Commands

1. Only real `znas` commands are allowed.
2. Allowed commands:
   - `znas search`
   - `znas ask`
   - `znas copy`
   - `znas remote-access status`
   - `znas remote-access enable`
   - `znas remote-access disable`
   - `znas remote-access show-id`
   - `znas remote-access set-id`
   - `znas file root spaces`
   - `znas file root list`
   - `znas file file read`
   - `znas file file raw`
   - `znas file file ai-text`
   - `znas copy`
   - `znas upload`
   - `znas file root delete` (or alias `znas file delete`)
   - `znas file root rename` (or alias `znas file rename`)
   - `znas file share create`
   - `znas file share delete`
   - `znas file share list`
   - `znas file tag create`
   - `znas file tag list`
   - `znas file tag edit-file-tag`
   - `znas file tag rename`
   - `znas file tag delete`
   - `znas file tag batch-create-file-tags`
   - `znas file rate update`
   - `znas file rate batch-update`
   - `znas file exif tree`
   - `znas file exif search`
   - `znas file ai summary-list`
   - `znas file favorites list`
   - `znas file favorites add`
   - `znas file favorites remove`
   - `znas file recycle restore`
   - `znas file recycle delete`
3. Forbidden fabricated commands:
   - `list_directory`
   - `search videos`
   - `znas gateway connect`
   - `znas file ls`
   - `znas-file share`
4. Confirmation policy:
   - Read operations do not require confirmation by default.
   - Write/delete/share/upload operations must be confirmed before execution.
