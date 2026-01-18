# Fantasy Console Database (FCDB)

This repository serves as the central data store for fantasy console game metadata and assets.

## Directory Structure

To ensure extensibility for future platforms (like TIC-80, UXN, etc.), the data is organized by platform.

```
fcdb/
├── sources/               # Raw scraped/source metadata (JSON)
│   ├── pico8/
│   │   ├── bbs_release.json
│   │   └── bbs_wip.json
│   └── tic80/
│       └── (future)
│
├── platforms/             # Binary assets and platform-specific files
│   ├── pico8/
│   │   ├── carts/         # Game cartridges (.p8.png)
│   │   └── thumbs/        # Thumbnail images (.png)
│   └── tic80/
│       ├── carts/         # (.tic)
│       └── thumbs/
│
├── dist/                  # Generated/Built database (for consumption)
│   ├── pico8/
│   │   ├── db.json        # Master DB
│   │   └── lists/         # Views/Subsets
│   └── tic80/
│
├── releases/              # Packaged ZIP distributions
│   ├── fcdb_pico8_vX.zip
│   └── fcdb_tic80_vX.zip
│
└── build/                 # Temporary build artifacts (ignored by git)
    ├── pico8/
    └── tic80/
```

## Maintenance
This repository is updated automatically by the `fcdbtool`.
- Source JSONs and Assets (`platforms/`) SHOULD be committed to Git.
- `dist/`, `releases/`, and `build/` are generated artifacts.
