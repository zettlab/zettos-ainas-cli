# Settings Workflows

## External share prerequisite

1. Read remote access state:
   - `znas settings remote p2p-status`
2. If disabled, enable it only after confirmation:
   - `znas settings remote set-p2p --json '{"enable":true}'`
3. Read device info to inspect current remote access ID:
   - `znas settings device info`
4. If needed, update the ID:
   - `znas settings device set-remote-id --json '{"remote_access_id":"my-office-2922"}'`
   - prefer lowercase IDs with length `>=8`, matching the current frontend validation rule

## UPS workflow

1. Read current UPS state first:
   - `znas settings ups get`
2. UPS enablement is a separate write:
   - `znas settings ups switch --params '{"switch":true}'`
   - `znas settings ups switch --params '{"switch":false}'`
3. Verified UPS payload today:
   - `type=1` means `USB UPS`
   - `standbyMode=1` means `Until the UPS runs low`
   - `standbyMode=2` means `Custom time`
4. Example UPS writes:
   - `znas settings ups set --json '{"type":1,"standbyMode":1}'`
   - `znas settings ups set --json '{"type":1,"standbyMode":2,"customMinutes":5}'`
5. For reversible eval, restore the original `enabled`, `type`, `standbyMode`, and `customMinutes` values from `ups get`.

## User management

1. Read service status and public key first:
   - `znas settings user-auth status`
   - `znas settings user-auth public-key`
2. Read current users and groups before changing them:
   - `znas settings user list`
   - `znas settings group list`
3. For `user create`, pass plaintext password in `--json`; the CLI encrypts it automatically.
4. For `user edit`, only pass `password` when you intend to reset it.
5. Prefer create/delete of disposable test identities when validating the workflow.

## Teams folder permissions

1. For a specific teams folder in the Files permissions modal, read current share-folder permissions first:
   - `znas settings permission share-folder-get --params '{"path":"/zettos/pool/1/teams/demo/DATA/private"}'`
2. Use writable field `set_permission`, not computed field `action_permission`.
3. Preferred shorthand update:
   - `znas settings permission share-folder-update --json '{"path":"/zettos/pool/1/teams/demo/DATA/private","username":"jianzheng","set_permission":0}'`
4. CLI expands that shorthand into the full `group_permissions` payload expected by the backend.
5. For generic user/group ACL routes `permission set` and `permission update`, do not assume `action_permission` is writable.

## Local file-service inspection

1. Read the common service state:
   - `znas settings file-service info`
2. For SMB / FTP / FTPS / WebDAV tasks, stop there unless the user explicitly asked about another service.
3. Do not read `nfs` / `dlna` / `rsync` / `timemachine` for a generic file-service question.
4. Only read those service-specific routes when the user's request is actually about that service.
5. Only then toggle or update the requested service.

## Hardware settings

1. Read current hardware state before changing it:
   - `znas settings fan get`
   - `znas settings light get`
   - `znas settings lcd get`
2. Verified fan mode mapping is:
   - `0=full-speed`
   - `1=silent`
   - `2=standard` which corresponds to the product UI `智能模式 / Smart Mode`
3. For fan changes, send only the verified `fanType` values above:
   - `znas settings fan set-mode --params '{"fanType":1}'`
4. For light changes, reuse the current `light get` values when restoring state instead of guessing:
   - `znas settings light get`
   - `znas settings light set --json '{"mode":0}'`
5. Light mode guardrails:
   - `mode=0=off` can be sent as `{"mode":0}`; the current CLI will auto-fill missing colors/speed from `light get` for backend compatibility
   - `mode=1..5` require both `start_color` and `end_color`
   - `mode=6=constant` requires `start_color`; optional `end_color` must match it
   - `speed` is only validated in the range `1..255`
6. For LCD writes, use the boolean JSON field and read back with `lcd get`:
   - `znas settings lcd set --json '{"enable":false}'`

## SMB / Bonjour / Time Machine workflow

1. Explain the goal in plain language first:
   - `SMB` is the main file-sharing protocol for Finder/Windows Explorer access.
   - `Bonjour` is the auto-discovery layer that helps Macs find the NAS in the network list.
   - `Time Machine folder` is the actual backup destination list, not just the discovery switch.
2. For the real user intent `帮我搞一下 Time Machine 备份`, prefer the single workflow command:
   - `znas settings timemachine setup --folder /teams/demo-backup --enable-smb`
3. The workflow success bar is not `Bonjour=true` alone.
   - success means `SMB=true`, `Bonjour=true`, and at least one configured Time Machine folder
4. If SMB is currently off, do not silently assume it is okay to enable it.
   - ask the user first, then rerun with `--enable-smb`
5. If no Time Machine folder is configured yet and the user did not name one, ask which team-space folder(s) to use.
   - do not guess a folder
   - do not use personal-space folders for this workflow
6. The workflow command may reuse existing Time Machine folders when they already exist.
   - if you need to inspect them explicitly: `znas settings timemachine folders`
7. Keep the low-level commands for partial operations only:
   - `znas settings file-service switch --json '{"enable_smb":true}'`
   - `znas settings bonjour switch --params '{"status":"enable"}'`
   - `znas settings timemachine set-folders --json '{"sharePaths":["/teams/demo-backup"]}'`
8. Do not claim the Time Machine workflow is complete after running only one of those partial commands.
9. Optional Time Machine params can be inspected separately:
   - `znas settings timemachine params`

## Certificate management

1. List certificates first:
   - `znas settings cert list`
2. For export or activation, always confirm the certificate `name`.
3. Upload/edit certificate files with multipart fields:
   - required upload fields: `cert.crt`, `cert_private.key`
   - optional fields: `intermediate_cert.crt`, `notes`
4. Prefer export and list before delete or regenerate actions.

## OTA, AI, and app-store operations

1. Read OTA schedule and firmware metadata before download or upgrade:
   - `znas settings update get-schedule`
   - `znas settings update current-version`
   - `znas settings update latest-version`
2. Read AI status before changing AI settings:
   - `znas settings ai-settings status`
3. Read installed apps for the target pool before any uninstall:
   - `znas settings app-store installed --params '{"pool_name":"pool_1"}'`
4. Treat OTA upgrade and app uninstall as confirmation-required actions.

## Safe time update

1. Read current time config:
   - `znas settings time get`
2. Only read NTP list when the user asks about sync servers or you need to change the sync server:
   - `znas settings time list-ntp`
3. For a simple `当前时间设置和时区` question, stop after `time get`.
4. Confirm timezone / sync mode with the user.
5. Write new config only after confirmation:
   - `znas settings time set --json '{"timezone":"Asia/Shanghai","isSynced":true,"timeServer":"pool.ntp.org","timeStr":"2026-03-10 12:00:00"}'`

## Network inspection before write

1. Read current interfaces:
   - `znas settings network list`
2. Only check external connectivity when the user explicitly asks whether the NAS can reach some domain/service, or when you are diagnosing a connectivity problem:
   - `znas settings network check --params '{"domain":"quickconnect.zettlab.com"}'`
3. For static IP writes, verify the required fields before sending:
   - IPv4: `ipAddress`, `subnetMask`, `gateway`, `dns`
   - IPv6: `ipAddress`, `prefix`, `gateway`, `dns`

## Clean-Agent Execution Discipline

1. If `base-url` and authenticated runtime are already provided, do not start with `znas --help`, `znas auth probe`, or `znas auth status` for ordinary settings tasks.
2. Try the direct feature command first.
3. If you are unsure, read the target route help directly once instead of walking `znas --help` -> feature help chains.
4. Only broaden into diagnosis after a direct command fails, or when the user explicitly asked for diagnosis.
5. Prefer the narrowest route that matches the user question:
   - `设备信息` -> `device info`
   - `外网访问状态` -> `remote p2p-status` or compatibility alias `remote-access status`
   - `网络设置` -> `network list`
   - `文件服务状态` -> `file-service info`
   - `WebDAV 端口` -> `file-service info`
   - `风扇模式` -> `fan get`
   - `灯带配置` -> `light get`
   - `屏幕开关状态` -> `lcd get`
6. For settings-remote intents, stay on `znas settings remote ...` or `znas settings remote-access ...`; do not jump to the top-level `znas remote-access ...` helper unless the controller explicitly marked it as a share-prerequisite task.
7. For eval cases with controller-managed rollback, do not restore the setting inside the same task unless the user intent explicitly asks to revert.

## Bridge creation guardrail

1. Read current interfaces:
   - `znas settings network list`
2. Count non-bridge NICs before creation:
   - normal bridge requires at least 2
   - virtual bridge requires at least 1
3. Only then create the bridge:
   - `znas settings network create-bridge --json '{"names":["LAN1","LAN2"]}'`

## Storage inspection before maintenance

1. Read storage-pool summary:
   - `znas settings storage-pool list`
2. Read physical disks:
   - `znas settings storage-pool disks`
3. Only after confirmation should you run pool repair, expansion, delete, or disk format routes.

## SMART inspection

1. Read disk inventory first:
   - `znas settings storage-pool disks`
2. Read the latest SMART report:
   - `znas settings smart info --params '{"device":"/dev/sdd"}'`
3. Only start or stop SMART tests after confirming the target disk and test type.
