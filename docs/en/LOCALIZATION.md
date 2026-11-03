# Language coverage and maintenance

**English** · [简体中文](../LOCALIZATION.md) · [Documentation](README.md)

The initial documentation languages are `en` and `zh-CN`. Other languages are not delivered. Adding a language requires an identified maintenance/review process; translated headings alone do not count as support.

| Surface | Current state | Completion criteria |
|---|---|---|
| README and user guides | English/Chinese pairs | Home → install → login → troubleshooting → support without changing language; identical limitations |
| Privacy, security, support, changelog | English/Chinese pairs | Equivalent data flow, cleanup, reporting channels, and support boundaries |
| Issue intake | English/Chinese bug forms and bilingual feature form | Users can complete a report in their language |
| Installer and diagnostics | English | Explicit language selection, locale detection, English fallback, all error paths still to implement/test |
| CLI help, errors, confirmations | English | Message IDs/catalogs and validation pending; commands/API/JSON contracts must not change |
| Agent skills | Existing generated content retained | Locale splitting and bilingual user-scenario acceptance not done; do not install duplicate same-name skills |
| Legal licenses | English LICENSE / TOOLING-LICENSE | License texts unchanged; translated explanations do not create or replace grants |

## Layout

- `README.md` is English; `README.zh-CN.md` is Chinese.
- `docs/en/*.md` contains English guides; existing `docs/*.md` remains Chinese to preserve links.
- SUPPORT and CONTRIBUTING have root English and `.zh-CN.md` counterparts.
- Existing Chinese PRIVACY, SECURITY, and CHANGELOG root paths remain; English counterparts live in `docs/en/`.
- Each page links to its counterpart and documentation navigation.

## Translation rules

Do not translate command names, flags, JSON keys, environment variables, versions, paths, error codes, or API names. Natural-language search examples may be localized; permissions, acknowledgment requirements, and behavior must stay equivalent. Keep placeholders and exclude real accounts, device addresses, and private filenames.

A skill is agent guidance, not a separate NAS application. `search` finds content; `ask` retrieves question context, with the agent/model producing the answer. Distinguish supported, verified, experimental, and planned capabilities.

Update language pairs together when product facts change. Review relative links, example arguments, current version, warnings, and limitations. Add new pages to both documentation indexes. Mark incomplete translations and link their available source explicitly; silent English fallback is not a completed translation.

Automated missing/stale-translation gates are not yet implemented. Maintainers must review parity in PRs; automation and native-language review remain release-quality work. Accept new languages by complete user journeys, not file counts.
