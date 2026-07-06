# FCDB Database Contract Specification

**Version**: 0.1.0
**Status**: Draft
**Level**: feature
**Owner**: fcdb
**Parent**: docs/specs/GLOBAL_SPEC.md
**Last Reviewed**: 2026-07-06

## 1. Purpose

Define the durable database and release-package contract for FCDB fantasy-console
catalog data. This contract lets agents and consumers handle multilingual game
metadata, list metadata, stable identity, and packaged assets without reverse
engineering `fcdbtool` implementation details or consumer-specific import code.

FCDB remains the upstream source package for fantasy-console catalog data.
Downstream products such as xwgamedb, Pico8Go, ManXiangSu, and Pico8IDE may add
their own product-facing models, but they must treat this contract as the
meaning of FCDB release artifacts.

## 2. Scope

In scope:

- FCDB source, dist, and release package data shapes.
- Canonical game identity and translation keys.
- Base metadata and localized metadata fallback rules.
- Curated list membership and list metadata localization.
- Common runtime, media, source, and asset extension fields.
- Agent rules for changing FCDB data, tooling, schema, and release packages.

Out of scope:

- xwgamedb's canonical desktop catalog model and device catalog export.
- Pico8Go, ManXiangSu, Pico8IDE, or xwdesktop presentation behavior.
- Scraper-specific HTML parsing behavior except where it populates this contract.
- User-downloaded carts or consumer-owned caches outside FCDB release packages.

## 3. Identity Contract

FCDB records keep source-native `id` values because upstream systems use
different identifiers. The public identity for a distributed game record is the
canonical FCDB key:

```text
fcdb:<platform>:<source>:<id>
```

Where:

- `platform` is the release platform directory/tag component such as `pico8`,
  `pyxel`, or `pyxelpico`.
- `source` is the record's required `source` field in `db.json`.
- `id` is the source-native record ID string.

Requirements:

- **ID-001**: Every distributed `db.json` game record MUST include non-empty
  `id` and `source` string fields.
- **ID-002**: `platform + source + id` MUST be unique inside a platform release.
- **ID-003**: `id` alone MUST NOT be treated as globally unique by tools,
  translations, list membership validators, importers, or consumers.
- **ID-004**: Derivative relationships MUST NOT be represented by merging two
  records that share `id` across sources. Use an explicit relationship field,
  such as `ref_id`, plus source/platform context until a richer relationship
  schema exists.
- **ID-005**: String list membership references in source or built list files
  MUST use canonical FCDB keys. Producer tooling may read unambiguous legacy
  source-native IDs only inside repository migration code, but agents MUST write
  canonical keys for new or edited list membership.

## 4. Base Database Contract

Each platform release contains a `db.json` base database. The base database is
an array of game records in deterministic order.

Required distributed fields:

| Field | Type | Requirement |
|---|---|---|
| `id` | string | Source-native game ID; required. |
| `source` | string | FCDB source namespace; required. |
| `name` | string | Base-locale display title; required. |
| `description` | string? | Base-locale description; optional. |
| `slug` | string? | Human-readable route/display slug; optional, not identity. |
| `author.name` | string | Base display author; required. |
| `author.id` | string? | Source-native author ID; optional. |
| `author.url` | string? | Author/profile URL; optional. |
| `license.type` | string? | License identifier; optional. |
| `license.url` | string? | License URL; optional. |
| `created` | string | Source creation/upload date; required when known. |
| `updated` | string | Source metadata/content update date; required when known. |
| `ref_id` | string? | Source-native related/original game ID; optional. |
| `extension` | object | Source/platform extension fields; required, may be empty. |

Requirements:

- **DB-001**: `db.json` MUST be valid UTF-8 JSON.
- **DB-001A**: `db.json` ordering MUST be deterministic for the same source
  inputs. The producer MUST write records in stable input/list order and MUST
  sort locale companion filenames before emitting them.
- **DB-002**: `slug` MUST NOT be used as identity. Slugs may collide and may
  contain non-ASCII or source-provided punctuation.
- **DB-003**: Date strings SHOULD use `YYYY-MM-DD` or ISO-like
  `YYYY-MM-DD HH:MM:SS` source timestamps. Unknown dates MUST be represented by
  a missing or `null` optional field only after the schema is updated to allow it.
- **DB-004**: The package `version.json` SHOULD declare `schema_version`,
  `platform`, `default_locale`, `available_locales`, and build timestamp once
  the schema migration begins.

## 5. Multilingual Metadata Contract

FCDB uses locale companion files rather than mutating `db.json` per language.
Public locale identifiers MUST use BCP-47 casing in release files, for example
`zh-CN`, `en-US`, and `ja-JP`. Underscore locale filenames MUST NOT be used by
FCDB source, dist, or release files. Producers MUST reject locale filenames that
can only become valid after case normalization, such as lowercase region tags;
agents must write the canonical filename directly.

### 5.1 Game Metadata Translations

Game translation files are named:

```text
db.<locale>.json
```

The target schema is an object keyed by canonical FCDB key:

```json
{
  "fcdb:pico8:pico8pixelbomb:picovibe_i18ndemo": {
    "name": "i18n Demo",
    "description": "Multi-language internationalization demo for PICO-8.",
    "author": { "name": "hp7hao" }
  }
}
```

Requirements:

- **I18N-001**: Translation entries MUST be overlays. Missing translated fields
  fall back to the base `db.json` record.
- **I18N-002**: Translation files MUST NOT redefine identity, source, asset,
  license, runtime, or list membership fields.
- **I18N-003**: Translation keys MUST be canonical FCDB keys after the
  migration. During migration, tooling may read legacy source-native ID keys but
  must write canonical keys in new release outputs.
- **I18N-003A**: Producer tooling MUST fail the build when a source translation
  entry cannot be resolved to a canonical key present in the built `db.json`.
  It MUST NOT silently drop or partially emit unresolved translation entries.
- **I18N-004**: Consumers SHOULD resolve locale in this order: exact locale,
  configured language alias if explicitly supported, `default_locale`, then
  base `db.json` fields.
- **I18N-005**: Translation files MUST be deterministic and must not include
  empty entries that add no localized fields.
- **I18N-006**: Source translation companion filenames MUST use
  `<source>.<locale>.json`; built translation filenames MUST use
  `db.<locale>.json`. The `<locale>` component MUST pass FCDB's BCP-47 filename
  validator.

### 5.2 List Metadata Translations

Base curated list files are named:

```text
lists/<list_id>.json
```

Localized list metadata overlays are named:

```text
lists/<list_id>.<locale>.json
```

List translation overlays localize `meta` fields only:

```json
{
  "meta": {
    "name": "蔚蓝合集",
    "description": "蔚蓝经典版及受其启发或由其衍生的游戏。"
  }
}
```

Requirements:

- **LIST-001**: Base list files own membership, filters, ranks, inline game
  definitions, and base metadata.
- **LIST-002**: List translation files MUST NOT change membership, filters, or
  rank definitions.
- **LIST-003**: Localized list membership, if needed later, MUST use a new
  explicitly named file type rather than overloading `lists/<id>.<locale>.json`.
- **LIST-004**: Built list files MUST use the shape `{ "meta": object,
  "games": GameMetadata[] }`. Translation list files MUST use the shape
  `{ "meta": object }` only.
- **LIST-005**: Filter and rank source list files MUST resolve to concrete
  built list files at build time; release packages MUST NOT expose source-only
  `filter` or `rank` membership rules as localized list overlays.
- **LIST-006**: Producer tooling MUST fail the build when explicit source list
  membership cannot be resolved to games present in the built `db.json`. It
  MUST NOT silently drop unresolved source list entries.

## 6. Asset And Extension Contract

Common extension fields must keep consistent meaning across tools:

| Field | Meaning |
|---|---|
| `extension.cart_file` | Package-relative runtime artifact under `carts/<source>/`. |
| `extension.cart_path` | Source-repository input path used by tooling; not required in releases. |
| `extension.cart_url` | Remote runtime cart URL. |
| `extension.source_file` | Package-relative editable source artifact under `sources/<source>/`. |
| `extension.source_path` | Source-repository input path used by tooling; not required in releases. |
| `extension.thumbnail_path` | Package-relative thumbnail path, source-relative thumbnail hint, or source remote path as documented by the platform source. |
| `extension.thumb_url` / `extension.image_url` | Remote thumbnail/image URL. |
| `extension.runtime` | Runtime identifier required to launch packaged content. |
| `extension.cart_format` | Format identifier for packaged cart artifact. |
| `extension.controls` | Human-readable control summary. |
| `extension.original_resolution` | Native content resolution when known. |
| `extension.scaling_strategy` | Scaling/migration hint when known. |

Requirements:

- **ASSET-001**: Local package asset paths MUST be relative paths and MUST NOT
  contain `..`, absolute paths, or backslashes.
- **ASSET-002**: Remote assets MUST be represented as explicit `http` or
  `https` URLs.
- **ASSET-003**: Consumers MUST NOT infer redistributability or playability from
  path shape alone. Importers may compute product-specific asset state from
  FCDB fields, but FCDB must keep source facts explicit.
- **ASSET-004**: New reusable extension keys MUST be added to this contract
  before tools or agents rely on them across more than one source or consumer.

## 7. Release Package Contract

Each platform release package uses this layout:

```text
fcdb_<platform>.zip
├── version.json
├── db.json
├── db.<locale>.json
├── lists/
│   ├── <list_id>.json
│   └── <list_id>.<locale>.json
├── carts/
├── sources/
└── thumbs/
```

Requirements:

- **PKG-001**: Each platform release is independently versioned and published.
- **PKG-002**: `version.json` MUST remain machine-readable and SHOULD include
  enough metadata for consumers to compare freshness without parsing GitHub
  release API responses.
- **PKG-003**: Release packages MUST include all generated translation files and
  curated list metadata overlays for that platform.
- **PKG-004**: Runtime ZIPs, when produced, MUST preserve runtime-relative paths
  documented by the platform extension contract.

## 8. Validation Requirements

FCDB contract changes should add or update cheap validation before release:

- **VAL-001**: Validate distributed `db.json` records have required fields and
  unique canonical keys.
- **VAL-002**: Validate translation files use supported locale filenames and
  keys that match existing canonical game keys.
- **VAL-003**: Validate game translation overlays contain only `name`,
  `description`, and `author.name`.
- **VAL-004**: Validate built list files contain `meta` and `games[]`, and
  every list game has a canonical key present in `db.json`.
- **VAL-005**: Validate list translation files contain only `meta` overlays and
  never contain `games`, `filter`, or `rank`.
- **VAL-006**: Validate package-local asset paths and source-repository input
  paths are safe relative paths, thumbnail path hints do not contain traversal
  or backslashes, and remote asset URLs are explicit `http` or `https` URLs.
- **VAL-007**: Validate release ZIPs contain expected metadata, translations,
  lists, and assets for the selected platform when packaging is in scope.

## 9. Agent Contract

This section is the concise contract agents must follow before editing FCDB data
or package-writing code. If an agent cannot satisfy one item, it must stop and
update this spec or report the blocker before editing data.

Governed files:

- `projects/fcdb/README.md`
- `projects/fcdb/sources/**`
- `projects/fcdb/curated/**`
- `projects/fcdb/dist/**`
- `projects/fcdb/releases/**`
- `projects/fcdb/docs/specs/**`
- FCDB package-writing logic in `projects/fcdbtool/src/**`

Agent invariants:

- **AGENT-001**: Use `fcdb:<platform>:<source>:<id>` for cross-source identity,
  translation keys, list membership references, validation messages, and
  consumer-facing examples.
- **AGENT-002**: Never use bare `id`, `slug`, translated name, list position,
  or package path as identity.
- **AGENT-003**: Write locale filenames with hyphenated BCP-47 tags only, such
  as `zh-CN`; never write underscore locale filenames.
- **AGENT-004**: Treat translations as overlays only. Do not put identity,
  membership, asset, license, runtime, or arbitrary extension fields in
  translation files.
- **AGENT-005**: Put list membership, filters, ranks, inline games, and base
  list metadata only in base list files. Put localized list text only in list
  translation files.
- **AGENT-006**: Keep local package asset paths relative and safe. Do not write
  absolute paths, `..`, or backslashes into local package path fields.
- **AGENT-007**: Remove empty optional extension fields instead of writing empty
  strings into distributed `db.json`.
- **AGENT-008**: Before adding a reusable extension key used by more than one
  source or consumer, update Section 6 first.
- **AGENT-009**: After editing FCDB source data or fcdbtool package-writing
  logic, run `npm run test:fcdb-contract` and `node out/cli.js validate
  <platform> --data-dir ../fcdb` from `projects/fcdbtool` for each affected
  platform.
- **AGENT-010**: When specs or indexes change, also run
  `node scripts/specs/validate-specs.mjs` and `bash scripts/specs/check_specs.sh`
  from the monorepo root.

Parent specs: `docs/specs/GLOBAL_SPEC.md`,
`docs/specs/spec_management_spec.md`. Consumer specs include
`projects/xwgamedb/docs/specs/fcdb_import_spec.md`,
`projects/pico8go/docs/specs/fcdb_browser_integration_spec.md`, and
`projects/manxiangsu.web/docs/specs/game_collections_spec.md`.

## 10. References

- FCDB README: `projects/fcdb/README.md`
- FCDBTool guidance: `projects/fcdbtool/AGENTS.md`
- xwgamedb importer: `projects/xwgamedb/docs/specs/fcdb_import_spec.md`
- Pico8Go consumer: `projects/pico8go/docs/specs/fcdb_browser_integration_spec.md`
- ManXiangSu consumer: `projects/manxiangsu.web/docs/specs/game_collections_spec.md`
