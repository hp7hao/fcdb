# Fantasy Console Database (FCDB)

A curated game database for fantasy console platforms. Each platform is built and released independently.

## Download

| Platform | Download | Contents |
|----------|----------|----------|
| PICO-8 | [fcdb_pico8.zip](https://github.com/hp7hao/fcdb/releases/download/pico8-latest/fcdb_pico8.zip) | Game metadata + PNG thumbnails |
| Pyxel | [fcdb_pyxel.zip](https://github.com/hp7hao/fcdb/releases/download/pyxel-latest/fcdb_pyxel.zip) | Game metadata + GIF thumbnails |

Each ZIP is updated independently — downloading one platform won't pull changes from another.

## ZIP Contents

```
fcdb_{platform}.zip
├── version.json          # Build date and version info
├── db.json               # Master database (all games)
├── db.{lang}.json        # Translated metadata (if available)
├── lists/                # Curated game lists (subsets of db.json)
│   └── *.json
└── thumbs/               # Thumbnail images
    ├── custom/            # Manually added thumbnails
    └── {source}/          # Source-specific thumbnails (e.g. bbs/, examples/)
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

**Pyxel** (`source: "examples"`):
- `extension.number` — Example number from the Pyxel User Examples page
- `extension.project_url` — GitHub repository URL
- `extension.image_url` — URL to GIF preview

### Thumbnails

Thumbnails are stored in the `thumbs/` directory, named by game ID:

- **PICO-8**: `thumbs/{source}/{id}.png` (128×128 PNG)
- **Pyxel**: `thumbs/{source}/{id}.gif` (animated GIF)

## Version Checking

Each platform release uses a fixed tag (`pico8-latest`, `pyxel-latest`). Use HTTP `ETag` or `Last-Modified` headers on the download URL to check for updates without re-downloading the full ZIP.

## Directory Structure (Source Repository)

```
fcdb/
├── sources/{platform}/          # Raw scraped metadata (JSON)
├── platforms/{platform}/
│   ├── carts/{source}/          # Game cartridges
│   └── thumbs/{source}/         # Thumbnail images
├── curated/{platform}/
│   ├── overrides.json           # Manual metadata overrides
│   └── lists/                   # Curated game lists
├── i18n/{lang}/{platform}.json  # Translations by game ID
├── dist/{platform}/             # Built output (db.json + lists/)
├── releases/                    # Packaged ZIPs
└── build/                       # Temp build artifacts (gitignored)
```

## Maintenance

This repository is maintained by [fcdbtool](https://github.com/hp7hao/fcdbtool). Releases are built automatically via GitHub Actions when platform data changes.

## Data Sources

- **PICO-8**: [Lexaloffle BBS](https://www.lexaloffle.com/bbs/?cat=7)
- **Pyxel**: [Pyxel User Examples](https://kitao.github.io/pyxel-user-examples/)
