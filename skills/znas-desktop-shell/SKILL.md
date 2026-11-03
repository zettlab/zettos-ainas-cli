---
name: znas-desktop-shell
description: "Call Zettos desktop-shell routes for resource monitor, task center, message center, desktop preferences, and profile avatar."
---

# znas desktop shell

> Use this skill when the user is asking about the right-top shell workflows: resource monitor, task center, message center, desktop language, desktop wallpaper, or user avatar.

## Command Families

- `znas monitor ...`
- `znas task ...`
- `znas message ...`
- `znas desktop ...`
- `znas profile ...`

## What This Skill Owns

- resource monitor reads
- task-center list and cleanup
- message-center unread/read/delete/red-dot flows
- desktop language get/set
- desktop wallpaper current/list/upload/set/delete
- profile avatar current/list/upload/select/delete

## What This Skill Does Not Own

- user/group/permission admin workflows
- network, device, storage-pool, SMART, cert, OTA, AI settings
- self password change
- logout
- session switch / relogin
- device restart / shutdown under shell commands

Route those to other layers instead:

- admin control-plane -> `znas-settings`
- auth/session lifecycle -> `znas auth` or higher-level agent runtime

## Intent Routing Rules

- "看 CPU / 内存 / 网速" -> `znas monitor ...`
- "看任务 / 清空任务记录" -> `znas task ...`
- "看消息 / 已读 / 全部已读 / 删除消息" -> `znas message ...`
- "换语言 / 看当前语言" -> `znas desktop language ...`
- "换壁纸 / 上传壁纸 / 删除壁纸" -> `znas desktop wallpaper ...`
- "换头像 / 上传头像 / 删除头像" -> `znas profile avatar ...`

## Safety Rules

1. Read current state before write operations when possible.
2. For avatar/wallpaper/language writes, prefer reversible flows and restore test changes on shared machines.
3. Do not start ordinary shell reads with a help chain when the intent is already clear and `base-url` + authenticated runtime are already available.
4. Use the canonical command families directly:
   - current shell overview -> `znas monitor view get`
   - task center -> `znas task task ...` or compatibility aliases `znas task center ...` / `znas task list`
   - language/wallpaper/avatar -> `znas desktop ...` / `znas profile ...`
   - compatibility shell alias `znas desktop-shell ...` is allowed, but the canonical families above remain preferred
5. If the user asks to change their own password, explain that this is intentionally not exposed through the CLI and direct them to the NAS UI flow. If the user or agent probes `znas auth change-password` / `znas auth password change` / `znas account password change`, that command should stop with the same UI-flow guidance instead of continuing toward `settings user`.
6. Never probe `znas settings user edit` / `znas settings user list` as a workaround for current-account password change.
7. Route explicit logout or session-management requests to `znas auth` or the higher-level agent runtime instead of treating them as desktop-shell features.
8. When the user explicitly asks to log out of the current NAS account, `znas auth logout` is the correct CLI path. This is a valid route-away outcome, not a desktop-shell command-family success.

## Freshness Rules (Critical)

1. Monitor metrics, task/message lists, unread counts, and current desktop preferences are mutable state.
2. For prompts about what is happening now, whether there are unread or failed items now, or what the current language/wallpaper/avatar is now, rerun the matching read command before answering.
3. If the user says they already changed the wallpaper/avatar/language or cleared messages/tasks elsewhere, do not reuse earlier state from the conversation.

## Preferred Command Patterns

- `znas monitor view get`
- `znas desktop-shell status`
- `znas task task list`
- `znas task center list`
- `znas task list`
- `znas task task delete --json '{...}'`
- `znas message v2-msg unread-messages`
- `znas message v2-msg read --json '{\"read_all\":true}'`
- `znas desktop language get`
- `znas desktop language set --json '{\"language\":\"en_us\"}'`
- `znas desktop-shell language get`
- `znas desktop wallpaper current`
- `znas desktop wallpaper info`
- `znas desktop wallpaper list`
- `znas desktop-shell wallpaper current`
- `znas desktop-shell wallpaper info`
- `znas desktop wallpaper upload --form-file file=./wallpaper.png`
- `znas desktop wallpaper upload-from-nas --json '{\"path\":\"/zettos/pool/.../wallpaper.png\"}'`
- `znas desktop wallpaper set --json '{\"from\":\"Upload\",\"path\":\"...\"}'`
- `znas profile avatar current`
- `znas profile avatar info`
- `znas profile avatar list`
- `znas desktop-shell avatar current`
- `znas desktop-shell avatar info`
- `znas profile avatar upload --json '{\"file\":\"data:image/png;base64,...\"}'`
- `znas profile avatar select --json '{\"avatar_url\":\"...\",\"from\":\"Upload\"}'`

## High-Risk / Disallowed Actions

- `self password change`
- `logout`
- `session switch`
- `device shutdown`
- `device restart`

These are not command mistakes. They are product-boundary exclusions.
