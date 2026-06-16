# MPAS GOCART2G Tools

Collection of utilities for preparing, remapping, and validating MPAS-GOCART2G inputs.

## Repository Structure

This repository uses a monorepo layout where each tool is developed and versioned in its own folder under `tools/`.

```
MPAS_GOCART2G_TOOLS/
├── tools/
│   └── static_chems_remap/
│       ├── README.md
│       ├── remap_static_chems_to_grid.py
│       ├── remap_paths.yaml.example
│       └── remap_paths.yaml
└── .gitignore
```

## Design Principles

- One folder per tool under `tools/`
- Each tool contains its own documentation and example config files
- Tool workflows are independent, so updates to one tool do not disrupt others
- Large generated outputs are excluded with `.gitignore`

## Available Tools

### static_chems_remap

Path: `tools/static_chems_remap/`

Purpose:
- Remap MPAS static chemistry fields from a base grid to a new grid
- Uses nearest-neighbor remapping on unstructured meshes
- Supports YAML-driven paths and optional `xtime` override
- Writes MPAS-compatible output format

Quick start:
1. See `tools/static_chems_remap/README.md`
2. Copy and edit `tools/static_chems_remap/remap_paths.yaml.example`
3. Run `tools/static_chems_remap/remap_static_chems_to_grid.py`

## Adding New Tools

To add a new utility, create a new folder under `tools/`:

1. `tools/<new_tool_name>/`
2. Add a local `README.md`
3. Add an example YAML/config if needed
4. Keep scripts and helper files scoped to that folder
5. Add ignore rules for large outputs to the repo `.gitignore`

## Version Control Workflow

Recommended workflow for independent development:

1. Create feature branch per tool update
2. Commit only files in that tool folder (plus shared docs if needed)
3. Open pull request with tool-specific summary
4. Tag releases at repository level when needed

## Notes

- Input/output data files are usually large and should remain outside version control unless intentionally tracked.
- Repository tracks code, docs, and lightweight configuration examples.
