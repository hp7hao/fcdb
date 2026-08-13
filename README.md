# Fantasy Console Database (FCDB)

A source-faithful metadata catalog for fantasy console platforms. Every record
describes one source entry; FCDB does not merge entries into canonical games or
decide product playability. Each platform is built independently.

## Download

| Platform | Download | Contents |
|----------|----------|----------|
| PICO-8 | [fcdb_pico8.zip](https://github.com/hp7hao/fcdb/releases/download/pico8-latest/fcdb_pico8.zip) | Game metadata plus record-declared non-BBS carts, editable sources, and thumbnails |
| Pyxel | [fcdb_pyxel.zip](https://github.com/hp7hao/fcdb/releases/download/pyxel-latest/fcdb_pyxel.zip) | Game metadata with remote GIF preview URLs |
| PyxelPico | [fcdb_pyxelpico.zip](https://github.com/hp7hao/fcdb/releases/download/pyxelpico-latest/fcdb_pyxelpico.zip) + [runtime](https://github.com/hp7hao/fcdb/releases/download/pyxelpico-latest/fcdb_runtime_pyxelpico_web.zip) | Game metadata plus PyxelPico cart ZIPs and optional web runtime |

Each ZIP is updated independently — downloading one platform won't pull changes from another.

## Versioning And Breaking Changes

FCDB separates contract, content, and build provenance:

- `schema_version` identifies the exact package and database contract.
- `package_version` identifies one platform package's content.
- `source_revision` and `producer_revision` identify the exact FCDB and
  FCDBTool Git inputs.

Consumers must read `version.json` before `db.json` and accept only a supported
major.minor schema line. Patch versions within a line are backward compatible:
`0.5.0`, `0.5.1`, and later `0.5.x` packages share the `0.5` contract. A
breaking change bumps the minor line, so `0.5.x` to `0.6.0` requires an
intentional consumer migration.

FCDB publishes each independently valid platform package without waiting for
consumer migration. Every package is available from both `*-latest` and its
`<platform>-schema-<major>.<minor>` compatibility-line channel. Before schema `1.0.0`,
`*-latest` is intentionally unstable and may contain breaking minor-schema
changes.

Consumers must inspect `version.json` before `db.json`. They should pin their
supported schema channel, or reject an unsupported `*-latest` package without
replacing their last working data. Each consumer owns its migration and full
compatibility suite; FCDB keeps no central readiness registry and publishes no
compatibility archive for pre-schema packages. Old `version: "1.0"` values are
package metadata, not schema versions.

The authoritative lifecycle and test requirements are in
`docs/specs/fcdb_database_contract_spec.md` Section 9.

## ZIP Contents

```
fcdb_{platform}.zip
├── version.json          # Build date and version info
├── db.json               # Master database (all games)
├── db.{locale}.json      # Game metadata translation overlays, e.g. db.zh-CN.json
├── lists/                # Curated + auto-generated game lists
│   ├── {name}.json       # List with { meta, games[] }
│   └── {name}.{locale}.json # List meta translations, e.g. celeste.zh-CN.json
├── carts/                # Record-declared cartridge files
│   └── {source}/         # e.g. pico8pixelbomb/, pyxelpico/
├── sources/              # Record-declared editable source artifacts
│   └── {source}/         # e.g. .p8mod files for Pico8IDE
└── thumbs/               # Record-declared thumbnail images
    └── {source}/         # e.g. pico8pixelbomb/, community/
```

## Database Schema

The durable database and release-package contract is defined in
`docs/specs/fcdb_database_contract_spec.md`. `db.json` contains an array of
game objects:

```json
{
  "id": "12345",
  "name": "Game Title",
  "description": "A short description",
  "source": "bbs",
  "creators": [{ "name": "Author Name", "url": "https://example.com/profile" }],
  "license": {
    "type": "CC4-BY-NC-SA",
    "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
  },
  "published_at": "2024-01-15",
  "source_updated_at": "2024-02-20",
  "source_metadata": {
    "cart_url": "https://example.com/cart.p8.png"
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Source-native ID (e.g. PICO-8 BBS `pid`) |
| `name` | string | Game title |
| `description` | string? | Short description |
| `source` | string | Data source (`bbs`, `examples`, etc.) |
| `creators` | array | Required ordered source credits |
| `license.type` | string? | License identifier |
| `license.url` | string? | License URL |
| `published_at` | string? | Source-asserted publication time; absent when unknown |
| `source_updated_at` | string? | Source-asserted update time; absent when unknown |
| `source_metadata` | object? | Strict platform/source-specific facts |

The public identity for a distributed game record is
`fcdb:<platform>:<source>:<id>`, for example
`fcdb:pico8:pico8pixelbomb:picovibe_i18ndemo`. Do not treat `id` or `slug`
alone as a global identity.

### Source-specific metadata

**PICO-8** (`source: "bbs"`):
- `source_metadata.cart_url` — remote `.p8.png` location
- `source_metadata.thumbnail_url` — remote BBS thumbnail location

**PICO-8** (non-BBS sources):
- `source_metadata.cart_file` — complete package-relative primary cart path
- `source_metadata.cart_locale` — non-English primary locale; omission means `en-US`
- `source_metadata.cart_files` — additional locale-to-package-path mappings
- `source_metadata.source_file` — optional complete package-relative editor source path

**Pyxel** (`source: "examples"`):
- `source_metadata.number` — example number
- `source_metadata.github_url` — GitHub project URL
- `source_metadata.thumbnail_url` — GIF preview URL

**PyxelPico** (`platform: "pyxelpico"`, `source: "pyxelpico"`):
- `source_metadata.cart_file` — complete package-relative PyxelPico cart ZIP path
- `source_metadata.cart_format` — `pyxelpico-cart-zip`
- `source_metadata.runtime` — `pyxelpico`

PyxelPico cart zips contain `pyxelpico-cart.json`, a `native/` payload,
browser-ready `web/index.html`, and `cover.png` when available. The shared
browser runtime is shipped as the dedicated
`fcdb_runtime_pyxelpico_web.zip` release asset. Extract it beside
`fcdb_pyxelpico.zip` so `runtimes/pyxelpico/web/` is available, then serve a
cart's `web/` directory without building from `pyxelpico-games`.

### Thumbnails

Thumbnails are stored in the `thumbs/` directory, named by game ID:

- **PICO-8**: `thumbs/{source}/{id}.png` (128×128 PNG)
- **Pyxel**: `thumbs/{source}/{id}.gif` (animated GIF)

## Version Checking

Each platform release uses a fixed tag (`pico8-latest`, `pyxel-latest`,
`pyxelpico-latest`). Use HTTP `ETag` or `Last-Modified` headers on the
download URL to check for updates without re-downloading the full ZIP.

## Directory Structure (Source Repository)

```
fcdb/
├── platforms/{platform}/
│   ├── metadata/
│   │   ├── sources/                 # Records, locale companions, .p8mod mappings
│   │   └── collections/             # Lists and flat locale companions
│   └── artifacts/                   # Retained source and release artifacts
├── dist/{platform}/                 # Generated db and list projections
├── releases/                        # Generated ZIPs
└── build/{platform}/                # Ignored transient fetch/build data
```

### Translation (i18n)

Two layers of companion files:

1. **Game-level**:
   `platforms/{platform}/metadata/sources/{source}.{locale}.json` — keyed by
   canonical FCDB key and merged into `dist/{platform}/db.{locale}.json`
2. **List-level**:
   `platforms/{platform}/metadata/collections/{name}.{locale}.json` — `meta`
   overlays copied to `dist/{platform}/lists/`

Locale filenames use BCP-47 casing such as `zh-CN`, `en-US`, and `ja-JP`.
Missing localized fields fall back to base `db.json` fields.

`{source}.p8mod.json` is reserved for the P8Mod artifact mapping used by sources
such as `pico8pixelbomb`; it is not a locale companion. Its local input paths
remain build-only and do not enter `db.json` or release manifests.

### Auto-generated Lists

Sources without a hand-curated list in
`platforms/{platform}/metadata/collections/` get an auto-generated list view at
build time. BBS sources are excluded because the complete BBS list is too large.

`artifacts/` is storage, not release authority. It may retain source-faithful
files such as the licensed PICO-8 BBS carts and thumbnails. Only paths declared
by records, plus declared runtime families, enter release ZIPs.

## Maintenance

This repository is maintained by [fcdbtool](https://github.com/hp7hao/fcdbtool). Releases are built automatically via GitHub Actions when platform data changes.

## Source Update Commands

To refresh Pyxel data:

```bash
node out/cli.js fetch pyxel examples release
node out/cli.js build pyxel
node out/cli.js pack pyxel
```

To refresh PyxelPico data, run the extraction locally and commit the resulting
FCDB source metadata plus shippable cart files. The release workflow does not
check out or resolve `pyxelpico-games`; it only packages data already committed
here.

```bash
node out/cli.js fetch pyxelpico pyxelpico release --source-dir ../pyxelpico-games --pyxelpico-dir ../pyxelpico
node out/cli.js build pyxelpico
node out/cli.js pack pyxelpico
```

Commit `platforms/pyxelpico/metadata/sources/pyxelpico.json`,
`platforms/pyxelpico/artifacts/carts/pyxelpico/*.zip`, and
`platforms/pyxelpico/artifacts/runtimes/pyxelpico/web/` after refreshing
PyxelPico games. The `fetch pyxelpico pyxelpico` command creates those cart ZIPs
from a local
`../pyxelpico-games` checkout and copies the shared web runtime from a local
`../pyxelpico` checkout.

`pack pyxelpico` creates two release artifacts:

- `releases/fcdb_pyxelpico.zip` — metadata, lists, and game carts
- `releases/fcdb_runtime_pyxelpico_web.zip` — shared web runtime that
  extracts to `runtimes/pyxelpico/web/`

## Data Sources

- **PICO-8**: [Lexaloffle BBS](https://www.lexaloffle.com/bbs/?cat=7)
- **Pyxel**: [Pyxel User Examples](https://kitao.github.io/pyxel-user-examples/)
- **PyxelPico**: Local `pyxelpico-games` port repository
