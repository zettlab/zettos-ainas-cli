# Commercial release readiness

**English** · [简体中文](../READINESS.md) · [Documentation](README.md)

The project is building distribution infrastructure and product acceptance. **It is not commercially ready.** Judge each dimension by evidence of user outcomes, not README counts, route counts, or a single green CI run.

| Dimension | Foundation present | Remaining delivery and acceptance |
|---|---|---|
| Product positioning and navigation | Bilingual home, task entry points, documentation hub | First-use journey tested with new users; genuine demos and clear success criteria |
| Languages | English/Chinese documentation journeys and issue forms | Installer/CLI localization, fallback, stale-translation gates, native-language review |
| Installation and version lifecycle | Signed downloads, version directories, recovery, rollback, uninstall | Anonymous installation after publication; upgrades between actual releases; Mac signing/notarization decision and checks |
| Core reliability | Native Linux checks; NAS login and some reads | Prepared-NAS browsing/search/QA, permissions, session expiry, reversible writes/cleanup, upstream refresh issue resolution |
| Compatibility and maintenance | Platform/firmware matrix and recorded evidence | Mac/minimum-OS coverage, firmware support range, retirement policy, regression devices |
| Security and supply chain | Credential protection, dangerous-action acknowledgment, signatures, dependency audit, private reports | Key backup/rotation drills, repair ownership/support lifetime, continuous advisory gate, provenance and recovery drills |
| Diagnostics and support | Minimal local diagnostic, bilingual forms, ordinary/security routing | Stable error categories and actionable recovery, verified redaction, triage ownership and response policy |
| Release engineering | Private implementation/public distribution separation, three-platform tool CI, Linux asset acceptance | Complete all-platform gates, signature/tag consistency, versioned documentation, withdrawal/rollback drills |
| Licensing, privacy, operations | Separate binary/tooling grants, third-party notices, data-flow guide | Publisher approval of legal/privacy wording, named maintenance ownership and support commitments; no invented SLAs or certifications |

## Delivery batches

1. **Documentation and language entry points:** this batch supplies both language journeys, support/contribution guides, issue forms, and gap tracking. Review links, examples, and factual parity.
2. **Runtime language and first use:** establish installer/CLI message catalogs, explicit language selection and fallback, keep machine-readable output stable, and validate first successful browsing with new users.
3. **Blocking acceptance:** complete Mac delivery, exercise core scenarios on a prepared NAS, and resolve long-lived-login issues. Keep the release in draft until these gates pass.
4. **Sustainable delivery:** translation synchronization, release evidence, compatibility regression, maintenance ownership, version support, and real upgrade/recovery drills before claiming those capabilities complete.

[ACCEPTANCE.md](ACCEPTANCE.md) contains concrete evidence. Immediate external needs are an Apple Silicon Mac, a NAS with storage/test files, and resolution of the backend refresh-token behavior. Documentation can progress independently, but cannot mark those dependencies complete.
