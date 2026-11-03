---
name: znas-app-store
description: "Call Zettos App Store APIs for app catalog, compose app install/update/status, and app-store settings."
---

# znas app-store

> Use this skill when the user wants to browse NAS apps, install or update an app, start/stop an installed app, read app-store settings, or manage Zettlab apps from an app-centric perspective.

## What This Skill Is For

- Browse what apps are available or already installed.
- Read or change the default app install pool.
- Read catalog app YAML, Zettlab app versions, and update reminders.
- Install a compose app from YAML.
- Update, start, stop, cancel-install, or uninstall a compose app.
- Broadcast installed compose status and trigger update discovery.
- Install or update Zettlab-branded apps, including from a NAS-local ZPK.

## User Framing

For beginners, explain App Store as:
- `给 NAS 装软件和管理软件的地方`
- Mention `Docker/Compose` only if the user needs the technical detail.
- Prefer the app-centric wording: install app, update app, stop app, uninstall app.

## Safety Rules

1. Read app state before changing it.
2. For compose app install, send the real install request directly; do not use `dry_run=true` on this backend.
3. Confirm before uninstall/update/install unless the user explicitly asked for the action.
4. Read the default install pool before changing it.
5. For a store app YAML template, use `znas app-store app yaml --params '{"app_name":"<app-name>"}'`.
6. Do not bypass `znas app-store ...` with native `docker`, `docker compose`, `podman`, or direct internal HTTP calls.
7. If an app-store route is missing or fails, report the limitation instead of falling back to host-native runtime commands.

8. `install_pool` is a NAS storage-pool name such as `pool_1`, not an arbitrary filesystem path.
9. Ask the user which storage pool to install into unless they already gave a standing install-pool preference.
10. Treat `znas app-store settings default-pool` as reference only; do not silently use it as the install target unless the user explicitly said to keep using that pool.
11. Do not send `dry_run=true` for `app-store compose install`; CLI should send the real install request with `dry_run=false`.
12. If the user gives a made-up path or non-existent pool, reject it and explain the valid pool choices first.
13. If the current store catalog already contains the target app, do not rewrite the install intent into a Docker image flow just because the product runs on containers underneath.
14. This matters for productized store apps that expose presets or metadata beyond raw image creation.
   - current canonical example: qBittorrent store metadata exposes default account hints and troubleshooting notes that a Docker-first path can lose

## Workflow Boundary (Critical)

1. Default app install flow: check `znas app-store app list --params '{"only_installed":false}'` first.
2. If the target app exists in the store catalog, stay on the app-store path.
3. If the target app exists in the store catalog and the user wants to install it, ask which `install_pool` to use before `compose install` unless they already set a standing pool preference.
4. If the target app is missing from the catalog, do not invent an app-store compose install flow.
5. For a store app template, use `znas app-store app yaml --params '{"app_name":"<app-name>"}'`; do not probe catalog membership through an installed-app route.
6. For `现在安装了什么 app` or equivalent wording, use `znas app-store installed list`, which forces `only_installed=true`.
7. `znas app-store app list` is the catalog/store shelf, not the installed-app answer.
8. If a store app is present in `app list` but currently shows `waiting`, `installing`, or `install`, report that in-progress state instead of switching to `znas docker ...`.
9. Missing catalog app => switch to `znas docker ...`:
   - single-image app: use `znas docker create-from-image --image <repo:tag>` to let CLI resolve the image, read recommend-config, keep default env/network/port sections, and show NAS folder candidates
   - custom compose/yaml app: `project yaml-example` or user YAML -> user chooses `compose_file_path` -> `project create`
10. `app-store compose install` is for store-provided compose apps, not generic third-party Docker onboarding.

## Freshness Rules (Critical)

1. Installed apps, app counts, compose status, default pool, and browser-openable URLs are mutable state.
2. When the user asks `现在装了哪些应用`, `还有几个应用`, `默认装到哪个池`, `现在这个应用好了没`, or any equivalent current-state question, rerun the relevant read command before answering.
3. After install, update, start, stop, cancel, or uninstall, always re-query installed and runtime state before claiming the latest result.
4. A prior turn may identify the target app or pool.
   - It does not make the old installed/status result reusable as the current truth

## After Install Or Start (Mandatory)

If the app can be opened in a browser (`open_in_browser=true`), do not stop at `installation enqueued` or `container running`.

Async install state handling:
- `installation enqueued` means the request was accepted, not that the app is installed yet.
- app-store status `install` means the app is still in the async installation pipeline.
- app-store status `waiting` means the task is queued; `installing` means the worker has started it.
- if install returns conflict or any ambiguous error, rerun `app list` immediately; if the app now shows `waiting` or `installing`, do not submit install again.
- Do not translate `install` into a specific root cause such as `正在下载镜像` unless you have direct evidence from image/project/container state or backend logs.
- Do not claim `network/Docker Hub/registry is broken` unless you have explicit failure evidence.

Trusted ZPK install is also asynchronous:
- Do not use legacy `zettlab install-offline`: some NAS versions return an empty HTTP 200 without installing. Require fresh operation completion linked to this verified artifact plus installed source/package identity; an unchanged same-version row is insufficient.
- First run `znas app-store zpk verify` and match package identity/trust; `znas app-store zpk install` then submits exactly one POST; an accepted response means queued, not completed.
- Read `znas app-store installed list` (`only_installed=true`) and map a full package id such as `com.zettlab.zettagent` to its installed-list key `zettagent`.
- For a package built by Coder/GitHub, the ownership chain is: Coder build -> `znas coder artifact download` -> this trusted `zpk install` route -> `znas app-store installed list` and open-metadata readback.
- Coder's `artifact install` is a lower-level/legacy installer and does not register App Store metadata; do not present it as the App Store delivery path.
- After an ambiguous 5xx or `unknown error`, only status `waiting`, `install`, `downloading`, `installing`, or `updating` corroborates this request. A stable `is_installed=true` record confirms presence but may predate an update, so report `offline install outcome could not be verified` and do not retry automatically.
- If the authoritative readback succeeds but the app is absent, preserve the original upstream error. If readback itself fails, report `offline install outcome could not be verified`.

1. Read the installed-app metadata and confirm the app is actually present.
2. Read the runtime/container status and confirm the main app container is running.
3. Build a user-usable URL from `scheme + host + port_map + index`.
4. Host selection rule:
   - if the active login/base URL host is a real reachable NAS host, reuse that host
   - if the active login/base URL is `localhost` or `127.0.0.1`, resolve a connected NAS IPv4 via `znas settings network list` and use that IP instead
5. Verify the URL before sending it to the user.
   - for local HTTP verification with shell tools, unset `http_proxy`, `https_proxy`, and `all_proxy` first
6. If the app metadata or docs expose default credentials, include them in the reply.
7. Prefer `app yaml` metadata when checking whether a store app exposes default credentials or product-specific troubleshooting notes.
8. If no default credentials are exposed, explicitly say the app requires first-run setup instead of inventing a username/password.

Recommended install verification sequence:
1. `znas app-store app list --params '{"only_installed":false}'` to read catalog/store status.
2. If the target app now shows `waiting` or `installing`, report that state and stop retrying `compose install`.
3. `znas app-store installed list` to read the current installed-app grid.
4. `znas app-store compose installed --params '{"pool_name":"pool_1"}'` to see if the app has entered the installed compose-app set.
5. `znas app-store app version --params '{"app_name":"<app-name>"}'` to read Zettlab version/update state.
6. `znas docker project list --params '{"page":1,"page_size":100}'` and `znas docker container list --params '{"page":1,"page_size":100}'` to confirm runtime state.
7. If the app is still `install` and runtime state has not appeared yet, report it as `still installing / pending backend completion`, not as success or as a guessed root cause.

## Key Commands

```bash
znas app-store app list --params '{"only_installed":false}'
znas app-store installed list
znas app-store settings default-pool
znas app-store app yaml --params '{"app_name":"paperless"}' --header accept=application/yaml -o paperless.yml
znas app-store app version --params '{"app_name":"zettagent"}'
znas app-store app set-reminder --params '{"app_name":"zettagent"}' --json '{"version":"1.2.3","mode":2}'
znas app-store app discover-updates
znas app-store compose installed --params '{"pool_name":"pool_1"}'
znas app-store compose install --params '{"install_pool":"pool_1","check_port_conflict":true}' --body-file ./paperless.yml --content-type application/yaml
znas app-store compose install --params '{"install_pool":"not_a_pool","check_port_conflict":true}' --body-file ./paperless.yml --content-type application/yaml  # should fail: invalid pool
znas app-store compose status --params '{"id":"paperless"}' --json '{"status":"stop"}'
znas app-store compose update --params '{"id":"paperless"}'
znas app-store compose broadcast-installed-status
znas app-store compose uninstall --params '{"id":"paperless"}'
znas app-store zpk verify --json '{"zpk_path":"/zettos/pool/1/users/demo/DATA/demo.zpk"}'
znas app-store zpk install --json '{"zpk_path":"/zettos/pool/1/users/demo/DATA/demo.zpk","storage_pool":"pool_1","async":true}'
znas app-store zettlab status --json '{"appName":"zettagent","status":"start"}'
znas app-store zettlab update --json '{"app_name":"zettagent"}'
znas app-store zpk verify --json '{"zpk_path":"/zettos/emmc/appstore/trusted-zpk/1000/example.zpk"}'
znas app-store zpk install --json '{"zpk_path":"/zettos/emmc/appstore/trusted-zpk/1000/example.zpk","storage_pool":"pool_1"}'
```

## Features

### app

- `GET` `list` -> `/v2/app_management/apps` (auth)
- `GET` `yaml` -> `/v2/app_management/apps/:app_name/compose` (auth)
- `GET` `version` -> `/v2/app_management/apps/:app_name/version` (auth)
- `PUT` `set-reminder` -> `/v2/app_management/apps/:app_name/version/reminder` (auth)
- `POST` `discover-updates` -> `/v2/app_management/apps/discover_updates` (auth)

### compose

- `GET` `installed` -> `/v2/app_management/apps/installed` (auth)
- `POST` `install` -> `/v2/app_management/compose` (auth)
- `PATCH` `update` -> `/v2/app_management/compose/:id` (auth)
- `PUT` `status` -> `/v2/app_management/compose/:id/status` (auth)
- `DELETE` `cancel-install` -> `/v2/app_management/compose/:id/cancel_install` (auth)
- `DELETE` `uninstall` -> `/v2/app_management/compose/:id` (auth)
- `POST` `broadcast-installed-status` -> `/v2/app_management/compose/installed/send_app_status` (auth)

### settings

- `GET` `get` -> `/v2/app_management/settings` (auth)
- `PUT` `set` -> `/v2/app_management/settings` (auth)
- `GET` `default-pool` -> `/v2/app_management/default_install_pool` (auth)
- `PUT` `set-default-pool` -> `/v2/app_management/default_install_pool` (auth)

### zettlab

- `POST` `install` -> `/v2/app_management/install/zettlab_app` (auth)
- `DELETE` `uninstall` -> `/v2/app_management/uninstall/zettlab_app` (auth)
- `POST` `install-offline` -> `/v2/app_management/install/zettlab_app/offline` (auth)
- `PUT` `status` -> `/v2/app_management/zettlab_app/status` (auth)
- `POST` `update` -> `/v2/app_management/update/zettlab_app` (auth)

### zpk

- `POST` `verify` -> `/v2/app_management/zpk/verify` (auth)
- `POST` `install` -> `/v2/app_management/zpk/install` (auth)
