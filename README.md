# Fantasy Console Database (FCDB)

A source-faithful metadata catalog for fantasy console platforms. Every record
describes one source entry; FCDB does not merge entries into canonical games or
decide product playability. Each platform is built independently.

## Download

| Platform | Download | Contents |
|----------|----------|----------|
| PICO-8 | [fcdb_pico8.zip](https://github.com/hp7hao/fcdb/releases/download/pico8-latest/fcdb_pico8.zip) | Game metadata + thumbnails + permitted non-BBS carts/source artifacts |
| Pyxel | [fcdb_pyxel.zip](https://github.com/hp7hao/fcdb/releases/download/pyxel-latest/fcdb_pyxel.zip) | Game metadata + GIF thumbnails |
| PyxelPico | [fcdb_pyxelpico.zip](https://github.com/hp7hao/fcdb/releases/download/pyxelpico-latest/fcdb_pyxelpico.zip) + [runtime](https://github.com/hp7hao/fcdb/releases/download/pyxelpico-latest/fcdb_runtime_pyxelpico_web.zip) | Game metadata + PyxelPico zip carts + optional web runtime |

Each ZIP is updated independently — downloading one platform won't pull changes from another.

## ZIP Contents

```
fcdb_{platform}.zip
├── version.json          # Build date and version info
├── db.json               # Master database (all games)
├── db.{locale}.json      # Game metadata translation overlays, e.g. db.zh-CN.json
├── lists/                # Curated + auto-generated game lists
│   ├── {name}.json       # List with { meta, games[] }
│   └── {name}.{locale}.json # List meta translations, e.g. celeste.zh-CN.json
├── carts/                # Non-BBS cartridge files
│   └── {source}/         # e.g. pico8pixelbomb/, pyxelpico/
├── sources/              # Optional editable source artifacts
│   └── {source}/         # e.g. .p8mod files for Pico8IDE
└── thumbs/               # Thumbnail images
    └── {source}/          # e.g. bbs/, pico8pixelbomb/, examples/
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
├── sources/{platform}/              # Raw scraped metadata
│   ├── {source}.json                # Game data (single-dot basename)
│   └── {source}.{locale}.json       # Game-level translations, e.g. source.zh-CN.json
├── platforms/{platform}/
│   ├── carts/{source}/              # Game cartridges
│   └── thumbs/{source}/             # Thumbnail images
├── curated/{platform}/
│   ├── overrides.json               # Manual metadata overrides
│   └── lists/                       # Curated game lists
│       ├── {name}.json              # List definition (IDs, filters, or inline games)
│       └── {name}.{locale}.json     # List meta translations, e.g. celeste.zh-CN.json
├── dist/{platform}/                 # Built output
│   ├── db.json                      # Master database
│   ├── db.{locale}.json             # Canonical-key game translation overlays
│   └── lists/                       # Curated + auto-generated lists
├── releases/                        # Packaged ZIPs
└── build/                           # Temp build artifacts (gitignored)
```

### Translation (i18n)

Two layers of companion files:

1. **Game-level**: `sources/{platform}/{source}.{locale}.json` — keyed by
   canonical FCDB key, merged into `dist/db.{locale}.json` at build time
2. **List-level**: `curated/{platform}/lists/{name}.{locale}.json` — `meta`
   overlays copied to `dist/lists/` at build time

Locale filenames use BCP-47 casing such as `zh-CN`, `en-US`, and `ja-JP`.
Missing localized fields fall back to base `db.json` fields.

### Auto-generated Lists

Sources without a hand-curated list in `curated/{platform}/lists/` get an auto-generated list view at build time. BBS sources are excluded (too large for a single list).

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

Commit `sources/pyxelpico/pyxelpico_release.json`,
`platforms/pyxelpico/carts/pyxelpico/*.zip`, and
`platforms/pyxelpico/runtimes/pyxelpico/web/` after refreshing PyxelPico games. The
`fetch pyxelpico pyxelpico` command creates those zip carts from a local
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
