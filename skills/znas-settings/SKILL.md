---
name: znas-settings
description: "Call Zettos settings APIs for device, system, analysis-plan, firewall, user management, local-storage services, gateway certificates, OTA, AI settings, app-store hooks, network, hardware, storage, SMART, remote access, and time workflows."
---

# znas settings

> Use this skill when the user wants NAS settings, analysis-plan preference, firewall status/configuration, user and permission management, local file-service switches, certificate management, OTA or AI settings, app-store related control-plane tasks, remote access, device info, network and hardware control, storage-pool inspection, SMART status, time settings, or other control-plane tasks.

## References

- `./references/commands.md`
- `./references/workflows.md`

## Scope In This Version

- Device info and device identity settings
- System readiness and system configs
- Analysis and improvement preference
- Firewall status, helper data, config CRUD, activation, and raw JSON update
- User status, public-key, password verification, user CRUD, group CRUD, and permission routes
- Local-storage file services: SMB, FTP, FTPS, WebDAV, NFS, DLNA, rsync, Bonjour, and Time Machine
- Gateway certificate list, activation, export, regenerate, upload, and edit
- OTA schedule, current/latest firmware metadata, download progress, and upgrade triggers
- AI settings status and AI model upgrade progress
- App-store installed-app listing and uninstall trigger
- Network inspection, connectivity checks, and guarded bridge/network writes
- Hardware settings for fan, RGB light, LCD, and UPS
- Storage-pool inspection and controlled storage maintenance routes
- SMART inspection and SMART test control
- Remote access / remote support
- Time settings and NTP server list

## Explicit Exclusions

- Do not use this skill for `monitor`, `task`, `message`, desktop `language`, desktop `wallpaper`, or profile `avatar`.
- Do not use this skill for self password change or logout/session management.
- Those shell-facing intents belong to `znas-desktop-shell`; session lifecycle belongs to `znas auth` or the higher-level agent runtime.
- Admin password reset for another account may still use `znas settings user edit`, but current-user self password change must not.
- If the user asks to change their own password, explain that this is intentionally not exposed through the CLI and direct them to the NAS UI flow.

## Newbie Communication Rules

1. Start with the user goal in plain language, not internal product terms.
2. If a technical term is necessary, explain it in one short sentence first.
3. Preferred plain-language mapping:
   - `remote access` -> `外网访问`
   - `NTP` -> `自动对时 / 自动校时`
   - `SMB / FTP / WebDAV / NFS` -> `电脑访问 NAS 文件的方式`
   - `DDNS` -> `让外网更容易找到你家 NAS 的固定地址方式`
   - `storage pool` -> `存储空间池 / 磁盘空间组织方式`
4. For first-time users, answer in this order:
   - what this feature helps them do
   - whether most people need it
   - the safest default or recommended option
   - the exact command only after the user agrees or asks for action
5. When multiple settings options exist, prefer a short recommendation list over a protocol dump.

## Command Entry

- Route-level entry: `znas settings <feature> <command>`
- For settings intents, prefer the route-level entry first.
- High-level `znas remote-access ...` still exists, but reserve it for share-prerequisite orchestration or when the user explicitly asks for that helper flow.
- For `settings` module eval or other route-surface validation, prefer `znas settings remote ...` or the settings-side compatibility alias `znas settings remote-access ...` over the top-level helper `znas remote-access ...`.
- For clean-agent `settings` eval, treat the top-level `znas remote-access ...` helper as off-limits unless the controller explicitly says the task is a share-prerequisite flow.

## Safety Rules

1. Read state before changing settings.
2. For write actions, explain the impact and confirm before execution.
3. For power or connectivity-affecting actions, require explicit confirmation.
4. Prefer reversible changes first.
5. For share-related tasks, keep the remote-access prerequisite check.
6. For network writes, validate required fields before request.
7. For bridge writes, preflight available NIC count before request.
8. Storage-pool and SMART writes are operationally sensitive; require explicit confirmation.
9. Certificate upload/edit uses multipart form fields, not JSON bodies.
10. User password fields are entered as plaintext in CLI JSON and encrypted by the CLI before request.
11. OTA upgrade, firmware download, and app uninstall are high-risk actions; confirm before execution.
12. For RGB light recommendations or writes, stay within verified modes and payload shape:
   - refer to modes as number + name together, for example `2=fountain` or `6=constant`
   - only verified modes are `0=off`, `1=breathing`, `2=fountain`, `3=flow`, `4=gradient`, `5=flicker`, `6=constant`
   - do not invent unsupported effects such as rainbow, full-spectrum auto cycle, or mode-specific behavior not confirmed in product code
   - `mode=1..5` are treated as two-color effects in the frontend UI; `mode=6=constant` is single-color
   - `mode=0=off` can be sent as `{"mode":0}`; the current CLI auto-fills missing colors/speed from `light get` for backend compatibility
   - `speed` only has a verified numeric range `1..255`; do not assert exact fast/slow direction unless the user confirms it on the current device
13. For fan writes, stay within the verified upstream enum:
   - `0=full-speed`
   - `1=silent`
   - `2=standard` which is presented as `智能模式 / Smart Mode` in the product UI
   - do not invent extra fan modes such as `3..8`

## Freshness Rules (Critical)

1. For current control-plane facts, rerun the matching read command before answering.
2. This applies to mutable state such as:
   - storage-pool count/list/disks
   - network status and interface list
   - remote-access status or id
   - device readiness, device info, and service enablement state
   - OTA current/latest metadata and progress
   - AI status, SMART status, firewall state, time config, current users/groups
3. If the user says they changed something manually, or another device/user may have changed it, discard earlier read results and query again.
4. Read-before-write is not enough here.
   - repeated read-only questions about `current` state also require a fresh query
5. If refresh fails, report that the latest state could not be verified instead of repeating an older answer.

## Preferred Workflows

1. Device snapshot:
   - `znas settings device info`
2. Check whether the box is ready:
   - `znas settings system ready`
3. Read remote-access state before changing it:
   - `znas settings remote p2p-status`
4. Read user and group state before changing identities or permissions:
   - `znas settings user-auth status`
   - `znas settings user list`
   - `znas settings group list`
   - for Files modal on a teams folder, read `znas settings permission share-folder-get --params '{"path":"<folder-path>"}'` first
5. Read local file-service state before changing SMB/FTP/WebDAV:
   - `znas settings file-service info`
   - only read `nfs` / `dlna` / `rsync` / `timemachine` when the user explicitly asks about those services
   - exception: for a real `Time Machine 备份` intent, do not decompose the flow into separate Bonjour/folder guesses; prefer `znas settings timemachine setup`
6. Read certificate state before activation/export/edit:
   - `znas settings cert list`
7. Read OTA / AI / app-store state before any upgrade or uninstall action:
   - `znas settings update get-schedule`
   - `znas settings update current-version`
   - `znas settings update latest-version`
   - `znas settings ai-settings status`
   - `znas settings app-store installed --params '{"pool_name":"pool_1"}'`
8. Read analysis-plan / firewall state before changing security-facing settings:
   - `znas settings analysis-plan get`
   - `znas settings firewall status`
   - `znas settings firewall list-configs`
9. Read network state before connectivity-affecting changes:
   - for ordinary network status/settings questions, start with `znas settings network list`
   - only use `znas settings network check --params '{"domain":"quickconnect.zettlab.com"}'` when the user explicitly asks for connectivity diagnosis or asks whether the NAS can reach some domain/service
10. Inspect storage and disks before any maintenance action:
   - `znas settings storage-pool list`
   - `znas settings storage-pool disks`
11. Read current time settings before changing them:
   - start with `znas settings time get`
   - only read `znas settings time list-ntp` when the user explicitly asks about NTP servers or you are changing sync-server config
   - for simple `当前时间设置和时区` questions, stop at `time get`
12. Read hardware state before changing hardware settings:
   - `风扇模式` -> `znas settings fan get`
   - `灯带模式/颜色/速度` -> `znas settings light get`
   - `屏幕开关状态` -> `znas settings lcd get`
   - for fan writes, use the verified mode ids only: `0=full-speed`, `1=silent`, `2=standard(smart UI mode)`

## Execution Discipline For Clean-Agent Eval

1. If the controller already gave a valid `base-url` and authenticated runtime, do not begin with a global help chain like `znas --help` or `znas settings --help` for ordinary settings tasks.
2. Execute the most likely direct settings command first.
3. If you are unsure, prefer reading the target route help directly once, for example `znas settings file-service info --help`, instead of walking global help layers.
4. Only inspect auth state or broader help after a direct command fails, or when the user explicitly asked about auth/login/connectivity.
5. For read-only questions, do not broaden the scope on your own:
   - `设备信息` -> `znas settings device info`
   - `外网访问状态` -> `znas settings remote p2p-status` or compatibility alias `znas settings remote-access status`
   - `网络设置` -> `znas settings network list`
   - `文件服务状态` -> `znas settings file-service info`
   - `WebDAV 端口` -> `znas settings file-service info`
   - `风扇模式` -> `znas settings fan get`
   - `灯带当前配置` -> `znas settings light get`
   - `屏幕开关状态` -> `znas settings lcd get`
   - do not append `nfs`, `dlna`, `rsync`, or `timemachine` reads unless the user asked about them
   - do not switch a settings-remote case to the top-level `znas remote-access ...`
6. For write questions, read the target feature's current state, perform the write, then re-read that same target feature.
   - `fan set-mode` readback should still use `fan get`
   - `light set` readback should use `light get`
   - `lcd set` readback should use `lcd get`
   - `timemachine setup` should finish with `SMB=true`, `Bonjour=true`, and at least one configured backup folder
7. For eval cases with controller-managed rollback, stop after the target state is verified.
   - do not restore or clean up inside the same task unless the user intent explicitly asked to revert
8. For a `帮我搞一下 Time Machine 备份` intent:
   - prefer `znas settings timemachine setup`
   - if SMB is off, ask the user whether the CLI may enable SMB, then rerun with `--enable-smb`
   - if no backup folder is currently configured and the user did not specify one, ask which team-space folder(s) to use; do not guess
   - do not claim success after only enabling Bonjour

## Storage-Pool Selection Notes For File Create

1. For `/personal` root-level folder creation, frontend-first behavior is:
   - prefer `znas settings storage-pool user-pools`
   - if that route is unavailable in the current environment, fall back to `znas settings storage-pool list`
2. For `/teams` root-level folder creation, use `znas settings storage-pool list`.
3. Only treat pools as eligible when both are true:
   - `status=0` (`ACTIVE`) when using `storage-pool list`
   - writable file-system state is explicitly verified on the current backend
     - documented shape may be `RW`
     - if the current response uses numeric encoding and you cannot verify the mapping, do not guess
4. Do not recommend degraded, failed, delayed, read-only, or unmounted pools for that create flow.
5. If more than one eligible pool exists, the file-create workflow should ask the user which pool to use unless they already declared a default pool.
6. After the pool is chosen, file creation should switch to `znas file root set-base-path`, not back to an aggregate `/personal` or `/teams` `list`.

## Feature Summary

### ai-settings

- `GET` `status` -> `/ai_settings/ai_status` (auth)
- `POST` `set` -> `/ai_settings/set_settings` (auth)
- `GET` `upgrade-progress` -> `/ai_settings/get_upgrade_progress` (auth)

### analysis-plan

- `GET` `get` -> `/v1/system/analysis-plan` (auth)
- `POST` `set` -> `/v1/system/analysis-plan` (auth)

### app-store

- `GET` `installed` -> `/v2/app_management/apps/installed` (auth)
- `DELETE` `uninstall` -> `/v2/app_management/uninstall/zettlab_app` (auth)

### bonjour

- `PUT` `switch` -> `/v1/samba/bonjour/:status` (auth)

### cert

- `GET` `list` -> `/v1/cert` (auth)
- `PUT` `activate` -> `/v1/cert/:name/activate` (auth)
- `POST` `upload` -> `/v1/cert/upload` (auth)
- `DELETE` `delete` -> `/v1/cert/:name` (auth)
- `POST` `regenerate-self-signed` -> `/v1/cert/self-signed/regenerate` (auth)
- `GET` `export` -> `/v1/cert/:name/export` (auth)
- `PUT` `edit` -> `/v1/cert/:name` (auth)

### device

- `GET` `info` -> `/v1/device` (auth)
- `GET` `device-auth` -> `/v1/device/auth` (auth)
- `PUT` `set-name` -> `/v1/device/name` (auth)
- `PUT` `set-remote-id` -> `/v1/device/remote-access-id` (auth)
- `GET` `refresh-remote-id` -> `/v1/device/refreshRemoteId` (auth)
- `GET` `be-scan` -> `/v1/device/beScan` (noauth)

### dlna

- `GET` `info` -> `/v1/fs/get_dlna_info` (auth)
- `POST` `add-dir` -> `/v1/fs/add_dlna_dir` (auth)
- `POST` `remove-dir` -> `/v1/fs/remove_dlna_dir` (auth)
- `POST` `switch` -> `/v1/fs/switch` (auth)

### fan

- `GET` `get` -> `/v1/fan` (auth)
- `POST` `set-mode` -> `/v1/fan/:fanType` (auth)
  - verified mapping: `0=full-speed`, `1=silent`, `2=standard(smart UI mode)`

### file-service

- `GET` `info` -> `/v1/fs/info` (auth)
- `POST` `switch` -> `/v1/fs/switch` (auth)

### firewall

- `GET` `status` -> `/v1/firewall/status` (auth)
- `PUT` `set-status` -> `/v1/firewall/status` (auth)
- `PUT` `switch-config` -> `/v1/firewall/switch/:configId` (auth)
- `GET` `interfaces` -> `/v1/firewall/interfaces` (auth)
- `GET` `builtin-services` -> `/v1/firewall/builtin-services` (auth)
- `GET` `protocols` -> `/v1/firewall/protocols` (auth)
- `GET` `countries` -> `/v1/firewall/countries` (auth)
- `GET` `list-configs` -> `/v1/firewall/configs` (auth)
- `GET` `get-config` -> `/v1/firewall/configs/:id` (auth)
- `POST` `save-config` -> `/v1/firewall/configs` (auth)
- `PUT` `update-config-raw` -> `/v1/firewall/configs/:id/raw` (auth)
- `DELETE` `delete-config` -> `/v1/firewall/configs/:id` (auth)

### group

- `GET` `list` -> `/v1/groups` (auth)
- `POST` `create` -> `/v1/groups` (auth)
- `PUT` `update` -> `/v1/groups` (auth)
- `DELETE` `delete` -> `/v1/groups` (auth)

### lcd

- `GET` `get` -> `/v1/lcd` (auth)
- `POST` `set` -> `/v1/lcd` (auth)

### light

- `GET` `get` -> `/v1/light` (auth)
- `POST` `set` -> `/v1/light` (auth)
  - validated fields: `mode`, optional `speed`, optional `start_color`, optional `end_color`

### network

- `GET` `list` -> `/v1/network` (auth)
- `PUT` `update` -> `/v1/network` (auth)
- `GET` `check` -> `/v1/network/check` (auth)
- `GET` `test-download-speed` -> `/v1/network/testDownloadSpeed` (auth)
- `POST` `test-upload-speed` -> `/v1/network/testUploadSpeed` (auth)
- `POST` `create-bridge` -> `/v1/network/bridge` (auth)
- `DELETE` `delete-bridge` -> `/v1/network/bridge` (auth)
- `POST` `create-virtual-bridge` -> `/v1/network/vir-bridge` (auth)
- `DELETE` `delete-virtual-bridge` -> `/v1/network/vir-bridge` (auth)

### nfs

- `GET` `info` -> `/v1/fs/get_nfs_info` (auth)
- `POST` `add-dir` -> `/v1/fs/add_nfs_dir` (auth)
- `POST` `remove-dir` -> `/v1/fs/remove_nfs_dir` (auth)
- `POST` `switch` -> `/v1/fs/switch` (auth)

### permission

- `GET` `get` -> `/v1/permissions` (auth)
- `POST` `set` -> `/v1/permissions` (auth)
- `PUT` `update` -> `/v1/permissions` (auth)
- `GET` `paths` -> `/v1/permissions/paths` (auth)
- `GET` `share-folder-get` -> `/v1/permissions/share_folder` (auth)
- `PUT` `share-folder-update` -> `/v1/permissions/share_folder` (auth)
- `GET` `personal-share-get` -> `/v1/permissions/personal_share_folder` (auth)
- `PUT` `personal-share-update` -> `/v1/permissions/personal_share_folder` (auth)

Permission write rule:

- writable field is `set_permission`, not computed field `action_permission`
- for a specific teams folder from the Files permissions modal, prefer `share-folder-update`
- CLI supports shorthand for `share-folder-update`, for example:
  `znas settings permission share-folder-update --json '{"path":"<folder>","username":"jianzheng","set_permission":0}'`

### remote

- `GET` `p2p-status` -> `/v1/service/remote/p2p` (auth)
- `PUT` `set-p2p` -> `/v1/service/remote/p2p` (auth)
- `GET` `support-status` -> `/v1/service/remote/support` (auth)
- `POST` `set-support` -> `/v1/service/remote/support` (auth)
- `DELETE` `stop-support` -> `/v1/service/remote/support` (auth)

### rsync

- `GET` `info` -> `/v1/fs/get_rsync_info` (auth)
- `POST` `enable` -> `/v1/fs/open_rsync` (auth)
- `POST` `disable` -> `/v1/fs/close_rsync` (auth)

### smart

- `POST` `start` -> `/v1/device/smart/start` (auth)
- `POST` `stop` -> `/v1/device/smart/stop` (auth)
- `GET` `status` -> `/v1/device/smart/status` (auth)
- `GET` `status-async` -> `/v1/device/smart/statusAsync` (auth)
- `GET` `info` -> `/v1/device/smart/info` (auth)

### storage-pool

- `GET` `list` -> `/v1/storage-pool` (auth)
- `POST` `create` -> `/v1/storage-pool` (auth)
- `DELETE` `delete` -> `/v1/storage-pool/:id` (auth)
- `POST` `repair` -> `/v1/storage-pool/repair` (auth)
- `POST` `upgrade` -> `/v1/storage-pool/upgrade` (auth)
- `POST` `expansion` -> `/v1/storage-pool/expansion` (auth)
- `GET` `disks` -> `/v1/storage-pool/disks` (auth)
- `POST` `format-disk` -> `/v1/storage-pool/disks/format` (auth)
- `POST` `available-info` -> `/v1/storage-pool/available-info` (auth)
- `POST` `add-spare` -> `/v1/storage-pool/spare` (auth)
- `DELETE` `delete-spare` -> `/v1/storage-pool/spare` (auth)
- `POST` `add-ssd` -> `/v1/storage-pool/ssd` (auth)
- `DELETE` `delete-ssd` -> `/v1/storage-pool/ssd` (auth)
- `GET` `user-pools` -> `/v1/storage-pool/user_pools` (auth)
- `GET` `have` -> `/v1/storage-pool/HAVE` (auth)

### system

- `GET` `get-configs` -> `/v1/system/configs` (auth)
- `PUT` `set-configs` -> `/v1/system/configs` (auth)
- `GET` `ready` -> `/v1/system/ready` (auth)
- `PUT` `shutdown` -> `/v1/system/state/off` (auth)
- `PUT` `restart` -> `/v1/system/state/restart` (auth)

### time

- `GET` `get` -> `/v1/time` (auth)
- `PUT` `set` -> `/v1/time` (auth)
- `GET` `list-ntp` -> `/v1/time/ntpList` (auth)
- `PUT` `add-ntp` -> `/v1/time/ntpList` (auth)
- `DELETE` `delete-ntp` -> `/v1/time/ntpList` (auth)

### timemachine

- `GET` `folders` -> `/v1/samba/timeMachineFile` (auth)
- `POST` `set-folders` -> `/v1/samba/timeMachineFile` (auth)
- `GET` `params` -> `/v1/samba/timeMachineFile/params` (auth)
- `POST` `set-params` -> `/v1/samba/timeMachineFile/params` (auth)

### update

- `GET` `get-schedule` -> `/v2/get/schedule` (auth)
- `DELETE` `delete-schedule` -> `/v2/del/schedule` (auth)
- `POST` `set-schedule` -> `/v2/set/schedule` (auth)
- `GET` `current-version` -> `/v2/getCurrentVersion` (auth)
- `GET` `latest-version` -> `/v2/getLatestVersion` (auth)
- `PUT` `download` -> `/v2/download` (auth)
- `GET` `download-progress` -> `/v2/download/progress` (auth)
- `POST` `upgrade` -> `/v2/upgrade` (auth)

### ups

- `GET` `get` -> `/v1/ups` (auth)
- `PUT` `set` -> `/v1/ups` (auth)
- `PUT` `switch` -> `/v1/ups/switch/:switch` (auth)

### user

- `GET` `list` -> `/v1/users` (auth)
- `POST` `create` -> `/v1/users` (auth)
- `PUT` `edit` -> `/v1/users` (auth)
- `DELETE` `delete` -> `/v1/users` (auth)
- `PUT` `lock` -> `/v1/users/lock` (auth)

### user-auth

- `GET` `status` -> `/v1/status` (noauth)
- `GET` `public-key` -> `/v1/public_key` (noauth)
- `POST` `verify-password` -> `/v1/passwd_verification` (auth)

## Guardrails

- Do not fabricate settings commands outside `znas settings ...` or `znas remote-access ...`.
- Keep frontend-only validation in mind when the backend may not enforce it.
- If a setting write can break connectivity or access, surface that risk before running it.
- Path-parameter settings routes consume fields from `--params` (for example `id`, `fanType`, `switch`).
