# Fantasy Console Database (FCDB)

A curated game database for fantasy console platforms. Each platform is built and released independently.

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
├── db.{lang}.json        # Translated metadata (if available)
├── lists/                # Curated + auto-generated game lists
│   ├── {name}.json       # List with { meta, games[] }
│   └── {name}.{lang}.json # List meta translations
├── carts/                # Non-BBS cartridge files
│   └── {source}/         # e.g. pico8pixelbomb/, pyxelpico/
├── sources/              # Optional editable source artifacts
│   └── {source}/         # e.g. .p8mod files for Pico8IDE
└── thumbs/               # Thumbnail images
    └── {source}/          # e.g. bbs/, pico8pixelbomb/, examples/
```

## Database Schema

`db.json` contains an array of game objects:

```json
{
  "id": "12345",
  "name": "Game Title",
  "description": "A short description",
  "source": "bbs",
  "author": {
    "name": "Author Name",
    "url": "https://..."
  },
  "license": "CC4-BY-NC-SA",
  "created": "2024-01-15",
  "updated": "2024-02-20",
  "extension": {}
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID within the platform (e.g. PICO-8 BBS `pid`) |
| `name` | string | Game title |
| `description` | string? | Short description |
| `source` | string | Data source (`bbs`, `examples`, etc.) |
| `author.name` | string | Author display name |
| `author.url` | string? | Author profile URL |
| `license` | string? | License identifier |
| `created` | string | ISO date (YYYY-MM-DD) when first scraped |
| `updated` | string | ISO date (YYYY-MM-DD) of last metadata change |
| `extension` | object | Platform-specific fields (see below) |

### Platform Extensions

**PICO-8** (`source: "bbs"`):
- `extension.lid` — Lexaloffle BBS lid (cartridge version ID)
- `extension.cart_url` — Direct URL to .p8.png cartridge
- `extension.thumb_url` — Direct URL to thumbnail on BBS

**PICO-8** (non-BBS sources):
- `extension.cart_file` — First-class runtime cart in `carts/{source}/`, preferably `.p8.png`
- `extension.source_file` — Optional editor source in `sources/{source}/`, either `.p8mod` or `.p8`

**Pyxel** (`source: "examples"`):
- `extension.number` — Example number from the Pyxel User Examples page
- `extension.project_url` — GitHub repository URL
- `extension.image_url` — URL to GIF preview

**PyxelPico** (`platform: "pyxelpico"`, `source: "pyxelpico"`):
- `extension.cart_file` — Single-file PyxelPico cart zip in `carts/pyxelpico/`
- `extension.cart_format` — `pyxelpico-cart-zip`
- `extension.runtime` — `pyxelpico`
- `extension.controls` — Handheld control summary
- `extension.scaling_strategy` — Migration scaling strategy

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
│   └── {source}.{lang}.json         # Game-level translations (companion files)
├── platforms/{platform}/
│   ├── carts/{source}/              # Game cartridges
│   └── thumbs/{source}/             # Thumbnail images
├── curated/{platform}/
│   ├── overrides.json               # Manual metadata overrides
│   └── lists/                       # Curated game lists
│       ├── {name}.json              # List definition (IDs, filters, or inline games)
│       └── {name}.{lang}.json       # List meta translations
├── dist/{platform}/                 # Built output
│   ├── db.json                      # Master database
│   ├── db.{lang}.json               # Merged game translations
│   └── lists/                       # Curated + auto-generated lists
├── releases/                        # Packaged ZIPs
└── build/                           # Temp build artifacts (gitignored)
```

### Translation (i18n)

Two layers of companion files:

1. **Game-level**: `sources/{platform}/{source}.{lang}.json` — keyed by game ID, merged into `dist/db.{lang}.json` at build time
2. **List-level**: `curated/{platform}/lists/{name}.{lang}.json` — copied to `dist/lists/` at build time

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
