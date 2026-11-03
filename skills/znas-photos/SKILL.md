---
name: znas-photos
description: "Call Zettos Photos APIs for photo search, timeline buckets, user albums, similar-photo tasks, photo map, and AI recognized albums."
---

# znas photos

> Use this skill when the user asks about NAS Photos: search photos or videos, browse timeline/map data, manage albums, download albums, find similar photos, or inspect AI recognized people/pet albums.

## What This Skill Is For

- Read and update Photos configuration paths.
- Search indexed photos/videos and read timeline buckets.
- Create, list, update, delete, and download user albums.
- Start/list/delete similar-photo scan tasks and inspect groups.
- Read photo-map clusters, locations, and map switch state.
- Read and manage AI recognized feature albums such as people or pets.

## Discovery Rules

1. Prefer progressive CLI discovery instead of guessing:
   - `znas photos --help`
   - `znas photos <feature> --help`
   - `znas photos <feature> <command> --help`
2. Use `znas schema photos` when you need the route inventory, payload type, examples, and binary/write flags in JSON.
3. Keep backend field names exactly as shown in help/schema: examples include `fileIds`, `taskId`, `groupId`, `albumId`, `album_id`, `fIds`, and `eaHash`.
4. Do not translate all IDs to strings blindly. Preserve the field names and value shapes returned by prior API reads.

## Safety Rules

1. Read current state before every write or delete.
2. After a write/delete succeeds, rerun the matching read command before reporting final success.
3. Do not use host-native tools or direct internal `curl` for Photos control-plane work when `znas photos ...` has the route.
4. The Photos backend does not expose a universal dry-run mode. For destructive actions, inspect the exact target first and keep the mutation narrow.
5. For async similar-photo scans, task creation only enqueues work. Use `similar task-list` and group reads for status.
6. Normal album routes and AI feature album routes are different surfaces; do not mix `album_id` with `albumId`.

## Binary Output Rules

Routes marked as binary require `-o <file>` so stdout stays parseable:

- `znas photos album download ... -o album.zip`
- `znas photos photo stream ... -o live.mov`
- `znas photos feature avatar ... -o avatar.jpg`

If the command fails, the CLI validates JSON error responses before writing a file.

## Common Workflows

### Read Photos State

```bash
znas photos setting config
znas photos photo search --json '{"index":0,"size":20}'
znas photos photo timeline --params '{"time_tpl":"YYYY-MM","sort_order":1}'
```

### Album Workflow

```bash
znas photos album list --params '{"index":0,"size":20}'
znas photos album create --json '{"name":"Trip"}'
znas photos album add-photos --json '{"album_id":123,"fileIds":["456"]}'
znas photos album get --params '{"album_id":123}'
znas photos album download --json '{"album_id":123,"download_name_prefix":"Trip"}' -o trip.zip
```

### Similar Photos

```bash
znas photos similar task-list --params '{"index":0,"size":20,"imgSize":20,"groupSize":4}'
znas photos similar task-create --json '{"dirPath":["/personal/Photos"]}'
znas photos similar group-list --params '{"taskId":123,"index":0,"size":20,"imgSize":20}'
znas photos similar group-detail --params '{"taskId":123,"groupId":456,"offset":0,"size":50}'
```

### Map And AI Feature Albums

```bash
znas photos map last-location
znas photos map bounds --params '{"minLat":30,"maxLat":31,"minLon":120,"maxLon":121,"zoomLevel":10}'
znas photos feature progress --params '{"taskType":1}'
znas photos feature album-list --params '{"taskType":1,"index":0,"size":20,"isHide":false}'
znas photos feature album-photos --params '{"albumId":123,"index":0,"size":50}'
```

## Features

### album

- `POST` `download` -> `/downloadFiles` (auth)
  - flags: `binary`
  - canonical: `photos album download`
  - payload: `--json`
  - example: `znas photos album download --json '{"album_id":123,"download_name_prefix":"album"}' -o album.zip`
  - pitfall: Download can use `album_id` or `str_paths`; it returns binary zip data and needs `-o <file>`.
- `POST` `create` -> `/album/createAlbum` (auth)
  - flags: `write`
  - payload: `--json`; required: `name`
  - example: `znas photos album create --json '{"name":"Trip","description":"2026 trip"}'`
  - pitfall: Create the album first, then add photos with `album add-photos`.
- `PUT` `update` -> `/album/updateAlbum` (auth)
  - flags: `write`
  - payload: `--json`; required: `id`
  - example: `znas photos album update --json '{"id":123,"name":"Trip edited"}'`
  - pitfall: Use backend field `id`, not `album_id`, for normal album update.
- `DELETE` `delete` -> `/album/deleteAlbum` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `id`
  - example: `znas photos album delete --json '{"id":123}'`
  - pitfall: Delete the album only after reading it; this does not mean delete original files unless backend behavior changes.
- `GET` `list` -> `/album/listAlbum` (auth)
  - payload: `--params`; required: `size`
  - example: `znas photos album list --params '{"index":0,"size":20,"sort_type":2,"sort_order":1}'`
  - pitfall: List is GET query; use `index` and `size`, not a JSON body.
- `POST` `add-photos` -> `/album/addPhotoToAlbum` (auth)
  - flags: `write`
  - payload: `--json`; required: `album_id`
  - example: `znas photos album add-photos --json '{"album_id":123,"fileIds":["456"]}'`
  - pitfall: Backend field is `fileIds` with a capital I; `paths` is also supported when you have exact NAS paths.
- `DELETE` `remove-photos` -> `/album/removeAlubmPhotos` (auth)
  - flags: `destructive`
  - canonical: `photos album remove-photos`
  - payload: `--json`; required: `album_id`
  - example: `znas photos album remove-photos --json '{"album_id":123,"fileIds":["456"]}'`
  - pitfall: CLI hides upstream typo `removeAlubmPhotos`; use semantic command `remove-photos`.
- `GET` `get` -> `/album/getAlbum` (auth)
  - payload: `--params`; required: `album_id`
  - example: `znas photos album get --params '{"album_id":123}'`
  - pitfall: Album detail is GET query; pass `album_id` via `--params`.

### feature

- `GET` `progress` -> `/feature/process` (auth)
  - payload: `--params`
  - example: `znas photos feature progress --params '{"taskType":1}'`
  - pitfall: Omitting `taskType` reads backend default progress; pass it when the user asks face or pet specifically.
- `DELETE` `clear` -> `/feature/clear` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `taskType`
  - example: `znas photos feature clear --json '{"taskType":1}'`
  - pitfall: This resets discovered feature album data for the task type; read progress/list first.
- `GET` `switch` -> `/feature/switch` (auth)
  - payload: `--params`; required: `type`
  - example: `znas photos feature switch --params '{"type":1}'`
  - pitfall: Switch reads use field `type`; task album filters use `taskType`.
- `PUT` `set-switch` -> `/feature/switch` (auth)
  - flags: `write`
  - payload: `--json`; required: `type`, `switch`
  - example: `znas photos feature set-switch --json '{"type":1,"switch":1}'`
  - pitfall: After toggling, re-read `feature switch` before reporting final state.
- `PUT` `set-config` -> `/feature/switch/config` (auth)
  - flags: `write`
  - payload: `--json`; required: `type`, `hideNum`
  - example: `znas photos feature set-config --json '{"type":1,"hideNum":5}'`
  - pitfall: Use `hideNum` exactly; snake_case is not accepted by this backend.
- `GET` `album-list` -> `/feature/album/list` (auth)
  - payload: `--params`; required: `index`, `size`
  - example: `znas photos feature album-list --params '{"taskType":1,"index":0,"size":20,"isHide":false}'`
  - pitfall: Recognized feature albums use camelCase fields such as `taskType` and `isHide`.
- `GET` `album-count` -> `/feature/album/count` (auth)
  - payload: `--params`
  - example: `znas photos feature album-count --params '{"taskType":1,"isHide":false}'`
  - pitfall: Use `album-list` when you need album identities, not just counts.
- `GET` `relation` -> `/feature/relation` (auth)
  - payload: `--params`
  - example: `znas photos feature relation --params '{"taskType":1}'`
  - pitfall: Relations are options for recognized albums; read them before updating relation text.
- `GET` `album-get` -> `/feature/album` (auth)
  - payload: `--params`; required: `albumId`
  - example: `znas photos feature album-get --params '{"albumId":123}'`
  - pitfall: Feature album IDs use field `albumId`, unlike normal album detail which uses `album_id`.
- `PUT` `album-update` -> `/feature/album` (auth)
  - flags: `write`
  - payload: `--json`; required: `albumId`
  - example: `znas photos feature album-update --json '{"albumId":123,"name":"Alice"}'`
  - pitfall: Use `coverId`, `coverPath`, or `relation` only when you have values from prior reads.
- `POST` `album-hide` -> `/feature/album/hide` (auth)
  - flags: `write`
  - payload: `--json`; required: `albumIds`, `isHide`
  - example: `znas photos feature album-hide --json '{"albumIds":[123],"isHide":true}'`
  - pitfall: Verify hidden vs visible lists after changing `isHide`.
- `POST` `album-merge` -> `/feature/album/merge` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `albumIds`, `targetId`
  - example: `znas photos feature album-merge --json '{"albumIds":[123,124],"targetId":123}'`
  - pitfall: Read all source albums first; `targetId` must be the album that remains.
- `GET` `album-photos` -> `/feature/album/photos` (auth)
  - payload: `--params`; required: `albumId`, `index`, `size`
  - example: `znas photos feature album-photos --params '{"albumId":123,"index":0,"size":50}'`
  - pitfall: Use this for recognized albums; use `album get` for normal user albums.
- `PUT` `album-photo-update` -> `/feature/album/photo` (auth)
  - flags: `write`
  - payload: `--json`; required: `albumId`, `fIds`
  - example: `znas photos feature album-photo-update --json '{"albumId":123,"fIds":[456]}'`
  - pitfall: This moves recognized feature photo rows; `fIds` are feature row IDs from `album-photos`.
- `DELETE` `album-photo-delete` -> `/feature/album/photo` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `fIds`
  - example: `znas photos feature album-photo-delete --json '{"fIds":[456]}'`
  - pitfall: Read `album-photos` first and reuse the returned feature row IDs.
- `GET` `avatar` -> `/feature/avatar` (auth)
  - flags: `binary`
  - payload: `--params`; required: `eaHash`
  - example: `znas photos feature avatar --params '{"eaHash":"<hash>"}' -o avatar.jpg`
  - pitfall: This route returns an image file; always pass `-o <file>`.

### map

- `GET` `forward` -> `/map/forward` (auth)
  - payload: `--params`; required: `coords`, `model`
  - example: `znas photos map forward --params '{"coords":"116.3,39.9","model":1}'`
  - pitfall: Multiple coordinates are semicolon-separated inside `coords`.
- `GET` `switch` -> `/map/switch` (auth)
  - payload: `--params`; required: `type`
  - example: `znas photos map switch --params '{"type":2}'`
  - pitfall: Map switch uses feature request field `type`; current map switch type is usually 2.
- `PUT` `set-switch` -> `/map/switch` (auth)
  - flags: `write`
  - payload: `--json`; required: `type`, `switch`
  - example: `znas photos map set-switch --json '{"type":2,"switch":1}'`
  - pitfall: Write then re-read `map switch` before reporting the final state.
- `GET` `last-location` -> `/map/lastLocation` (auth)
  - payload: `none`
  - example: `znas photos map last-location`
  - pitfall: An empty result can mean no indexed photo has usable GPS data.
- `GET` `bounds` -> `/map/bounds` (auth)
  - payload: `--params`; required: `minLat`, `maxLat`, `minLon`, `maxLon`, `zoomLevel`
  - example: `znas photos map bounds --params '{"minLat":30,"maxLat":31,"minLon":120,"maxLon":121,"zoomLevel":10}'`
  - pitfall: Bounds use camelCase latitude/longitude fields; min values must be smaller than max values.
- `GET` `geohash` -> `/map/geohash` (auth)
  - payload: `--params`; required: `geohash`, `index`, `size`
  - example: `znas photos map geohash --params '{"geohash":"wtw3;wtw6","index":0,"size":20,"sortOrder":1}'`
  - pitfall: Multiple geohashes are semicolon-separated in a single `geohash` string.
- `GET` `countries` -> `/map/location/country` (auth)
  - payload: `--params`; required: `index`, `size`, `viewType`, `citySize`
  - example: `znas photos map countries --params '{"index":0,"size":20,"viewType":1,"citySize":5}'`
  - pitfall: Use this route for grouped location overview; use `cities` after choosing a country.
- `GET` `cities` -> `/map/location/city` (auth)
  - payload: `--params`; required: `country`, `offset`, `size`
  - example: `znas photos map cities --params '{"country":"China","offset":0,"size":20}'`
  - pitfall: City lookup requires the exact `country` string returned by `countries`.
- `GET` `city-photos` -> `/map/location/city/photo` (auth)
  - payload: `--params`; required: `addressId`, `index`, `size`
  - example: `znas photos map city-photos --params '{"addressId":123,"index":0,"size":50}'`
  - pitfall: Use `addressId` from the city response, not the display city name.

### photo

- `POST` `search` -> `/photos/search` (auth)
  - payload: `--json`; required: `index`, `size`
  - example: `znas photos photo search --json '{"index":0,"size":20,"keyword_search":"beach"}'`
  - pitfall: Photo search is POST JSON; keep backend field names such as `keyword_search`, `album_ids`, and `city_ids`.
- `GET` `timeline` -> `/photos/getTimeBuckets` (auth)
  - payload: `--params`
  - example: `znas photos photo timeline --params '{"time_tpl":"YYYY-MM","sort_order":1}'`
  - pitfall: Timeline is a GET route; pass filters with `--params`, not `--json`.
- `GET` `stream` -> `/photos/stream` (auth)
  - flags: `binary`
  - payload: `--params`; required: `id`
  - example: `znas photos photo stream --params '{"id":123456}' -o live.mov`
  - pitfall: This route returns binary live-photo data; always pass `-o <file>`.

### setting

- `POST` `init` -> `/setting/init` (auth)
  - flags: `write`
  - payload: `--json`; required: `init_path`
  - example: `znas photos setting init --json '{"init_path":"/personal/Photos"}'`
  - pitfall: Run `setting config` first; `init_path` is a NAS-visible path, not a host-local agent path.
- `GET` `config` -> `/setting/getConfig` (auth)
  - payload: `none`
  - example: `znas photos setting config`
  - pitfall: This read route requires photos setting to be initialized on the NAS.
- `POST` `add-path` -> `/setting/addPhotoPath` (auth)
  - flags: `write`
  - payload: `--json`; required: `path`
  - example: `znas photos setting add-path --json '{"path":"/personal/Camera","risk":false}'`
  - pitfall: Use the exact NAS path returned by file/settings APIs; do not invent physical pool paths.
- `DELETE` `remove-path` -> `/setting/removePhotoPath` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `path`
  - example: `znas photos setting remove-path --json '{"path":"/personal/Camera"}'`
  - pitfall: This changes the indexed photo roots; read config before and after removing a path.

### similar

- `GET` `task-list` -> `/photos/similar/task` (auth)
  - payload: `--params`; required: `index`, `size`, `imgSize`
  - example: `znas photos similar task-list --params '{"index":0,"size":20,"imgSize":20,"groupSize":4}'`
  - pitfall: Use camelCase field names from the backend: `imgSize` and `groupSize`.
- `POST` `task-create` -> `/photos/similar/task` (auth)
  - flags: `write`
  - payload: `--json`; required: `dirPath`
  - example: `znas photos similar task-create --json '{"dirPath":["/personal/Photos"]}'`
  - pitfall: This starts an async scan; list tasks after creating before claiming completion.
- `DELETE` `task-delete` -> `/photos/similar/task` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `taskId`
  - example: `znas photos similar task-delete --json '{"taskId":123}'`
  - pitfall: Read `similar task-list` first and reuse the exact `taskId`.
- `GET` `group-list` -> `/photos/similar/task/group` (auth)
  - payload: `--params`; required: `taskId`, `index`, `size`, `imgSize`
  - example: `znas photos similar group-list --params '{"taskId":123,"index":0,"size":20,"imgSize":20}'`
  - pitfall: Group list is query-based; do not pass `task_id` or snake_case field names.
- `GET` `group-detail` -> `/photos/similar/task/group/detail` (auth)
  - payload: `--params`; required: `taskId`, `groupId`, `offset`, `size`
  - example: `znas photos similar group-detail --params '{"taskId":123,"groupId":456,"offset":0,"size":50}'`
  - pitfall: Use `offset` for group detail paging; this route does not use `index`.
- `DELETE` `delete-photo` -> `/photos/similar/task/group/detail` (auth)
  - flags: `destructive`
  - payload: `--json`; required: `taskId`, `groupId`, `fileId`
  - example: `znas photos similar delete-photo --json '{"taskId":123,"groupId":456,"fileId":789}'`
  - pitfall: This removes one similar-group file relation; verify the group detail after the delete.
