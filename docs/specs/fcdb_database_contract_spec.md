# FCDB Database Contract Specification

**Version**: 0.5.0
**Status**: Draft
**Level**: feature
**Owner**: fcdb
**Parent**: docs/specs/GLOBAL_SPEC.md
**Last Reviewed**: 2026-07-23

## 1. Purpose

Define the durable database and release-package contract for FCDB fantasy-console
catalog data. FCDB is a versioned, source-faithful catalog of source entries,
descriptive metadata, asserted relationships, curated collections, and available
bundled or remote content.

An FCDB record does not claim to be the canonical identity of a game, work,
edition, release, or person. Downstream products such as xwgamedb, Pico8Go,
ManXiangSu, and Pico8IDE may add product-facing models, but they must treat this
contract as the meaning of FCDB release artifacts.

This draft defines target package schema `0.5.0`. Published packages and current
consumers remain on schema `0.4.0` until the coordinated migration in Section 10
is implemented and validated. A package always declares exactly one schema.

## 2. Scope And Architectural Boundary

In scope:

- FCDB source-entry identity and common descriptive metadata.
- Base metadata and localized metadata fallback rules.
- Explicit source-entry relationships.
- Source-specific metadata and bundled-cart references.
- Curated list membership and list metadata localization.
- Deterministic per-platform release packages and provenance.
- Validation and migration rules for schema `0.5.0`.

Out of scope:

- Canonical work, edition, release, or person identity.
- Automatic cross-source deduplication or merging.
- Generic resource, artifact, or per-resource rights models.
- Product-facing playability, installability, launch commands, or cache state.
- Product-specific locale filtering and presentation behavior.
- Scraper-specific parsing behavior except where it populates this contract.
- User-downloaded carts or consumer-owned caches outside FCDB packages.

FCDB MUST preserve separate source entries even when they have the same title,
slug, creator, content, or apparent upstream work. It MUST NOT infer equivalence
from those fields or from relationships. A downstream system may merge entries
only under its own authority.

## 3. Source-Entry Identity

Every distributed record represents one item as published or described by one
source. Its public FCDB source-entry key is:

```text
fcdb:<platform>:<source>:<id>
```

Where:

- `platform` is the release platform component, such as `pico8`, `tic80`,
  `pyxel`, or `pyxelpico`.
- `source` is the record's required source namespace.
- `id` is the source-native record identifier.

Requirements:

- **ID-001**: Every record MUST contain non-empty `id` and `source` strings.
- **ID-002**: `platform + source + id` MUST be unique inside a platform release.
- **ID-003**: Bare `id`, title, translated title, slug, creator, list position,
  package path, and relationship target MUST NOT be treated as global identity.
- **ID-004**: FCDB source-entry keys MUST key translations, list membership,
  relationships, validation diagnostics, and consumer provenance.
- **ID-005**: A producer MUST NOT merge records automatically. Explicit
  relationships preserve assertions without changing record identity.

## 4. Common Source-Entry Record

Each platform release contains a `db.json` array in deterministic source-entry
key order. A representative schema `0.5.0` record is:

```json
{
  "id": "103",
  "source": "pyxelpico",
  "name": "ACLM",
  "description": "Optional source description",
  "slug": "aclm",
  "creators": [
    {
      "name": "Jay Kumogata",
      "id": "optional-source-native-id",
      "url": "https://example.com/optional-profile"
    }
  ],
  "license": {
    "type": "Apache-2.0",
    "url": "https://example.com/optional-license"
  },
  "published_at": "2026-04-04",
  "source_updated_at": "2026-05-11",
  "relationships": [
    {
      "kind": "derived-from",
      "target": "fcdb:pyxel:examples:103"
    }
  ],
  "source_metadata": {
    "github_url": "https://github.com/jay-kumogata/RetroGames",
    "cart_file": "carts/pyxelpico/aclm.zip",
    "cart_format": "pyxelpico-cart-zip",
    "runtime": "pyxelpico"
  }
}
```

Common fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Required source-native entry ID. |
| `source` | string | Required source namespace. |
| `name` | string | Required base-locale display title. |
| `description` | string? | Optional base-locale description. |
| `slug` | string? | Optional human-readable route/display slug; never identity. |
| `creators` | creator[] | Required non-empty ordered source credits. |
| `license` | object? | Optional upstream license assertion for game/cart/source content. |
| `published_at` | string? | Optional source-asserted publication or upload time. |
| `source_updated_at` | string? | Optional source-asserted content or metadata update time. |
| `relationships` | relationship[]? | Optional asserted links to FCDB source entries. |
| `source_metadata` | object? | Optional metadata governed by the `platform + source` schema. |

Creator requirements:

- **CREATOR-001**: `creators` MUST contain at least one entry.
- **CREATOR-002**: Every creator MUST contain a non-empty `name` and MAY contain
  a source-native `id` and an explicit `http` or `https` profile `url`.
- **CREATOR-003**: Creator order MUST preserve source order when the source
  provides one. Order does not assert importance or contribution size.
- **CREATOR-004**: FCDB MUST NOT assign contributor roles or global person IDs.

Date and license requirements:

- **META-001**: `published_at` and `source_updated_at` MUST contain only times
  asserted by the upstream source. Unknown values are absent.
- **META-002**: Scrape, observation, import, migration, and package-build times
  MUST NOT appear as entry dates. Package `built_at` remains release provenance.
- **META-003**: Date strings SHOULD preserve an available source timestamp in
  `YYYY-MM-DD` or ISO-like form without manufacturing missing precision.
- **META-004**: `license`, when present, records an upstream assertion about the
  game, cart, or editable source content. It MUST NOT be interpreted as granting
  rights to thumbnails, linked websites, hosting infrastructure, or unrelated
  source metadata.
- **META-005**: Missing license data means FCDB has no license assertion. It
  MUST NOT be interpreted as redistributable, proprietary, or forbidden.

General requirements:

- **DB-001**: `db.json` MUST be valid UTF-8 JSON.
- **DB-002**: Producers MUST sort source and locale companion filenames before
  reading them and MUST emit records in source-entry key order.
- **DB-003**: Optional fields with no value MUST be omitted, not emitted as
  empty strings or synthetic placeholders.
- **DB-004**: `slug` MUST NOT participate in identity or joins.

## 5. Localized Metadata

FCDB uses locale companion files instead of mutating `db.json` per language.
Release locale identifiers and filenames MUST use canonical BCP-47 casing, such
as `zh-CN`, `en-US`, and `ja-JP`. Underscore filenames and lowercase region tags
are invalid package inputs.

Game translation files are named `db.<locale>.json` and are objects keyed by
FCDB source-entry key:

```json
{
  "fcdb:pico8:pico8pixelbomb:picovibe_i18ndemo": {
    "name": "i18n 演示",
    "description": "PICO-8 多语言国际化演示。"
  }
}
```

Requirements:

- **I18N-001**: Translation entries are overlays. Missing fields fall back to
  the base `db.json` record.
- **I18N-002**: A game translation entry MAY contain only `name` and
  `description`. It MUST NOT redefine creators, identity, dates, relationships,
  license, source metadata, assets, or list membership.
- **I18N-003**: Translation keys MUST be FCDB source-entry keys that resolve to
  records in the built `db.json`.
- **I18N-004**: Producers MUST fail on unresolved translation keys and MUST NOT
  silently discard or partially emit translation entries.
- **I18N-005**: Consumers SHOULD resolve metadata locale in this order: exact
  locale, an explicitly configured language alias, package `default_locale`,
  then base `db.json` fields.
- **I18N-006**: Translation files MUST be deterministic and omit entries that
  add no localized fields.
- **I18N-007**: Source companions use `<source>.<locale>.json`; built companions
  use `db.<locale>.json`.

Package metadata locale and bundled-cart locale are independent. Package
`default_locale` affects metadata fallback only and MUST NOT imply cart locale.

## 6. Relationship Registry

Schema `0.5.0` recognizes one relationship kind:

| Kind | Directional meaning |
|---|---|
| `derived-from` | This source entry is asserted to be based on the target source entry. |

Requirements:

- **REL-001**: Each relationship contains exactly `kind` and `target`.
- **REL-002**: `kind` MUST be `derived-from`. Other strings fail validation.
- **REL-003**: `target` MUST be a well-formed FCDB source-entry key and MUST
  differ from the containing entry's key.
- **REL-004**: Cross-platform targets are allowed even when the target is not
  present in the current platform package.
- **REL-005**: A relationship is an explicit directional source assertion. It
  MUST NOT cause merging, canonicalization, field inheritance, or equivalence.
- **REL-006**: New relationship kinds require demonstrated source data, defined
  direction and semantics, validation, and a schema revision.

## 7. Source-Specific Metadata And Bundled Carts

### 7.1 Source-Specific Boundary

`source_metadata` preserves facts that do not have stable cross-source meaning.
FCDBTool MUST select a strict schema using the package `platform` and record
`source`.

Examples include PICO-8 BBS likes and tags, TIC-80 ratings and categories,
Pyxel example numbers and GitHub URLs, and PyxelPico runtime hints. Natural
field names such as `cart_url`, `thumbnail_url`, `github_url`, `cart_format`,
and `runtime` are preferred over a universal resource abstraction.

Requirements:

- **SOURCE-001**: Every supported `platform + source` pair MUST have an explicit
  producer schema defining allowed keys, types, required values, URL rules, and
  package-path rules.
- **SOURCE-002**: Unknown source-metadata keys and wrong value types MUST fail
  the build with the source file and FCDB source-entry key.
- **SOURCE-003**: Generic consumers MUST treat `source_metadata` as opaque.
  Source-aware consumers may use a declared source schema.
- **SOURCE-004**: Adding a source-specific field does not give it common FCDB
  semantics. Promotion into the common record requires demonstrated shared
  meaning and a schema revision.
- **SOURCE-005**: Producer-only repository input paths MUST NOT appear in
  released records. A producer may keep those paths in build configuration.
- **SOURCE-006**: Remote facts use explicit `http` or `https` URLs. FCDB does
  not promise that a remote URL is reachable, downloadable, or redistributable.
- **SOURCE-007**: Local package paths MUST be relative, use `/`, contain no
  `..`, and name members inside the platform package.
- **SOURCE-008**: Scrape, observation, import, and migration timestamps are not
  source metadata and MUST NOT be distributed there.

### 7.2 Bundled-Cart Convention

A source schema that distributes playable cart content may use these fields:

| Field | Type | Meaning |
|---|---|---|
| `cart_file` | string | Package-relative primary or only bundled cart. |
| `cart_locale` | string? | Non-English locale of `cart_file`; omitted for `en-US`. |
| `cart_files` | object? | Additional locale-to-package-relative-cart mappings. |
| `cart_url` | string? | Upstream remote cart location; does not assert bundling. |

The convention deliberately optimizes for the existing catalog, where ordinary
carts are treated as `en-US` unless FCDB has specific non-English knowledge.
There is no unknown cart-locale state in schema `0.5.0`.

Requirements:

- **CART-001**: Presence of a valid `cart_file` is FCDB's sole assertion that an
  entry has a primary bundled cart. FCDB MUST NOT add redundant `bundled` or
  `playable` booleans.
- **CART-002**: When `cart_locale` is absent, `cart_file` means `en-US`.
- **CART-003**: `cart_locale` MUST be present when the primary cart is known to
  be non-English and MUST use canonical BCP-47 casing. The value `en-US` is
  invalid because English is represented by omission.
- **CART-004**: `cart_files`, when present, maps canonical BCP-47 locale keys to
  additional package-relative cart paths. It MUST NOT contain the primary
  locale or duplicate a cart path.
- **CART-005**: If an `en-US` cart exists, it MUST be `cart_file`,
  `cart_locale` MUST be absent, and `cart_files` MUST NOT contain `en-US`.
- **CART-006**: If no English cart exists, one available non-English cart is
  `cart_file` and its locale is required in `cart_locale`.
- **CART-007**: When English is added to an entry whose primary cart was
  non-English, English becomes `cart_file`; the former primary moves to
  `cart_files` under its locale.
- **CART-008**: A locale-aware consumer selects an exact `cart_files` match and
  otherwise falls back to `cart_file`. Consumers MUST NOT infer cart locale from
  filenames, titles, metadata locale, or host locale.
- **CART-009**: Every distributed `cart_file` and `cart_files` value MUST be a
  safe package-relative path and MUST resolve to a member of the release.
- **CART-010**: `cart_url` alone never means bundled or locally playable.
  Products compute remote/local playability under their own authority.

Examples:

```json
{
  "cart_file": "carts/pico8pixelbomb/game.p8.png"
}
```

The preceding primary cart is treated as `en-US`.

```json
{
  "cart_file": "carts/pico8pixelbomb/game.zh-CN.p8.png",
  "cart_locale": "zh-CN"
}
```

The preceding entry has only a Chinese primary cart.

```json
{
  "cart_file": "carts/pico8pixelbomb/game.en-US.p8.png",
  "cart_files": {
    "zh-CN": "carts/pico8pixelbomb/game.zh-CN.p8.png"
  }
}
```

The preceding entry has an English primary cart and a Chinese alternative.

## 8. Curated Lists

Base list files are named `lists/<list_id>.json`. Localized list metadata
overlays are named `lists/<list_id>.<locale>.json`.

Built base lists use:

```json
{
  "meta": {
    "name": "Example List",
    "description": "Optional description"
  },
  "games": [
    "fcdb:pico8:bbs:9971"
  ]
}
```

List translation overlays contain `meta` only.

Requirements:

- **LIST-001**: Base list files own membership, filters, ranks, inline source
  definitions, and base metadata.
- **LIST-002**: Built list files contain exactly `meta` and ordered
  source-entry-key `games`. They MUST NOT duplicate records.
- **LIST-003**: List translation files localize `meta` only and MUST NOT change
  membership, filters, or ranks.
- **LIST-004**: Source filter and rank rules MUST materialize into concrete
  ordered `games` during the build.
- **LIST-005**: Producers MUST fail on unresolved explicit membership and MUST
  NOT silently discard entries.
- **LIST-006**: Duplicate membership keys are invalid. Membership order is
  significant.
- **LIST-007**: Localized membership, if introduced later, requires a distinct
  explicitly named file type rather than overloading metadata overlays.

## 9. Release Package Contract

Each platform release package retains the flat deterministic layout:

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

`version.json` MUST declare `schema_version`, `package_version`, `platform`,
`default_locale`, `available_locales`, `source_revision`, `producer_revision`,
and `built_at`. Revisions are immutable Git object IDs. `built_at` describes the
package build only and is not an entry date.

Requirements:

- **PKG-001**: Each platform package is independently versioned and published.
- **PKG-002**: Identical inputs and revisions MUST produce deterministic record,
  translation, and list ordering.
- **PKG-003**: `package_version` identifies packaged content rather than a fixed
  placeholder.
- **PKG-004**: The producer builds into staging, validates staged output,
  creates and validates a temporary ZIP, and atomically promotes it. Failure
  leaves the previous final package unchanged.
- **PKG-005**: CI release production MUST use a pinned FCDBTool Git revision,
  never a moving branch.
- **PKG-006**: A consumer MUST reject every schema version except the exact
  version it supports before replacing a working package or cache.
- **PKG-007**: Schema `0.x` minor versions are breaking. Consumers MUST NOT infer
  compatibility from field presence.

## 10. Schema 0.5 Migration And Compatibility

Migration from `0.4.0` to `0.5.0` is an atomic shape migration for every
platform package:

| Schema 0.4 field | Schema 0.5 result |
|---|---|
| `author` | One entry in required `creators[]`; additional asserted collaborators may be added. |
| `created` | `published_at` only when it is a source publication/upload time. |
| `updated` | `source_updated_at` only when it is a source content/metadata update time. |
| `relationships` | Retained only when `kind` is `derived-from` and the target is valid. |
| `extension` | Mapped field-by-field into the strict `source_metadata` schema. |
| `license` | Retained as the optional entry-level assertion defined by `META-004`. |
| translated `author.name` | Removed; schema 0.5 translations contain only name and description. |
| `cart_file`, `cart_locale`, `cart_variants` | Converted to the bundled-cart convention in Section 7.2. |
| producer input paths | Moved to producer configuration and omitted from packages. |
| scrape/import/migration dates | Discarded from entry data. |

Requirements:

- **MIG-001**: A schema `0.5.0` package MUST contain only `0.5.0` records. Mixed
  shapes and dual legacy/new fields are invalid.
- **MIG-002**: Schema `0.5.0` MUST reject `author`, `created`, `updated`,
  `extension`, `ref_id`, and legacy cart-variant structures.
- **MIG-003**: Migration MUST NOT blindly rename ambiguous dates or the entire
  extension object. Each source schema owns explicit classification.
- **MIG-004**: Migration MUST fail with source filename and FCDB source-entry
  key when a value cannot be mapped safely. It MUST NOT synthesize creators,
  dates, locales, relationships, or paths merely to pass validation.
- **MIG-005**: FCDB MUST NOT promote a `0.5.0` package to a consumer channel
  whose declared consumer still supports only `0.4.0`.
- **MIG-006**: Each consumer updates its contract and fixtures, adds exact
  `0.5.0` support, and switches intentionally. Published `0.4.0` packages remain
  usable until that coordinated cutover.

## 11. Validation Requirements

Schema `0.5.0` validation MUST cover:

- **VAL-001**: Required common fields, non-empty creators, and unique FCDB
  source-entry keys.
- **VAL-002**: Deterministic record ordering and byte-stable results for
  identical inputs.
- **VAL-003**: Translation filename casing, allowed overlay fields, resolvable
  source-entry keys, and deterministic output.
- **VAL-004**: Ordered list entries, no duplicate or unresolved membership, and
  metadata-only list translation overlays.
- **VAL-005**: Only `derived-from` relationships, valid non-self targets, and no
  retired relationship forms.
- **VAL-006**: Strict `platform + source` metadata schemas, safe paths, explicit
  URLs, and rejection of unknown keys and wrong types.
- **VAL-007**: Bundled-cart default/locale invariants, canonical BCP-47 tags,
  no duplicate paths or locale ownership, and existence of every referenced
  package member.
- **VAL-008**: Complete and consistent manifests, exact schema version, safe ZIP
  members, expected translations/lists/assets, and no unexpected members.
- **VAL-009**: Fail-closed ingestion with source file and entry-key context for
  invalid JSON, non-array sources, missing fields, duplicate ownership,
  unresolved overlays/lists, retired fields, invalid source metadata, and
  missing declared package files. Logging and skipping is not success.

Representative contract fixtures MUST cover:

- two same-title entries in different source namespaces remaining distinct;
- multiple ordered creators;
- absent unknown source dates;
- title/description-only translations;
- valid and invalid `derived-from` relationships;
- PICO-8 remote metadata with no bundled cart;
- an implicit-`en-US` bundled cart;
- a `zh-CN`-only bundled cart;
- an English primary cart with a Chinese alternative;
- migration from non-English primary to English primary when English is added;
- Pyxel GitHub/thumbnail metadata;
- PyxelPico GitHub/bundled-ZIP metadata;
- TIC-80 bundled and remote cart metadata;
- missing carts, unsafe paths, unknown source keys, retired fields, and
  unsupported schema versions failing closed.

## 12. Consumer Boundary

Generic FCDB consumers may depend on common entry fields, localized title and
description overlays, relationships, lists, and package provenance. They MUST
NOT interpret source-specific fields without selecting the matching source
schema.

Source-aware consumers may project declared `source_metadata` fields:

- Pico8Go may resolve PICO-8 carts and thumbnails.
- ManXiangSu may project likes, tags, carts, and previews.
- xwgamedb may normalize entries into works, releases, contributors, media,
  runtime requirements, and product asset state.

Those projections do not make FCDB the owner of canonical identity,
installability, playability, launch behavior, or product cache policy.

## 13. Agent Contract

Governed files:

- `projects/fcdb/README.md`
- `projects/fcdb/sources/**`
- `projects/fcdb/curated/**`
- `projects/fcdb/dist/**`
- `projects/fcdb/releases/**`
- `projects/fcdb/docs/specs/**`
- FCDB package-writing logic in `projects/fcdbtool/src/**`

Agent invariants:

- **AGENT-001**: Use `fcdb:<platform>:<source>:<id>` as a source-entry key,
  never as an assertion of canonical game/work identity.
- **AGENT-002**: Never merge records by title, slug, creator, asset, or
  relationship.
- **AGENT-003**: Write locale filenames and explicit locale values using
  canonical BCP-47 casing.
- **AGENT-004**: Keep game translations limited to `name` and `description` and
  list translations limited to `meta`.
- **AGENT-005**: Update the strict `platform + source` validator before adding
  or changing source-specific metadata.
- **AGENT-006**: Keep producer-only input paths outside released records and
  keep distributed package paths relative and safe.
- **AGENT-007**: Do not add `bundled`, `playable`, or inferred locale fields;
  use the cart convention in Section 7.2.
- **AGENT-008**: A common field or relationship kind requires demonstrated
  cross-source need and an FCDB schema revision.
- **AGENT-009**: Schema changes require synchronized FCDBTool validation,
  representative fixtures, exact-version rejection tests, and consumer contract
  review before channel promotion.
- **AGENT-010**: After editing FCDB data or package-writing logic, run
  `npm run test:fcdb-contract` and `node out/cli.js release <platform>
  --data-dir ../fcdb --check-only` from `projects/fcdbtool` for each affected
  platform.
- **AGENT-011**: After editing this spec or its index, run
  `node scripts/specs/validate-specs.mjs`, `bash scripts/specs/check_specs.sh`,
  and `git diff --check` from the monorepo root.

Parent specs: `docs/specs/GLOBAL_SPEC.md` and
`docs/specs/spec_management_spec.md`.

Direct consumer contracts include
`projects/xwgamedb/docs/specs/fcdb_import_spec.md`,
`projects/pico8go/docs/specs/fcdb_browser_integration_spec.md`, and
`projects/manxiangsu.web/docs/specs/game_collections_spec.md`.

## 14. References

- FCDB README: `projects/fcdb/README.md`
- FCDBTool guidance: `projects/fcdbtool/AGENTS.md`
- xwgamedb importer: `projects/xwgamedb/docs/specs/fcdb_import_spec.md`
- Pico8Go consumer: `projects/pico8go/docs/specs/fcdb_browser_integration_spec.md`
- ManXiangSu consumer: `projects/manxiangsu.web/docs/specs/game_collections_spec.md`
