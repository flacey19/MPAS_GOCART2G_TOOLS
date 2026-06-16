# MPAS Static Chemistry Remapping Script

This script remaps an MPAS static chemistry file (`static_chems.nc`) from one unstructured mesh grid to another using nearest-neighbor interpolation.

## Overview

**Purpose:** Convert static chemistry and surface data from an MPAS grid (e.g., `x1.163842`) to a new MPAS grid (e.g., `x6.827394`).

**Features:**
- Nearest-neighbor remapping for all horizontal dimensions (`nCells`, `nEdges`, `nVertices`)
- Smart copying of mesh/topology fields directly from the target grid
- Automatic resizing of topology dimensions (`maxEdges`, `maxEdges2`)
- Support for two remapping backends: **uxarray** (preferred) or **scipy**
- Optional xtime override via YAML configuration
- Output in CDF5 format (NetCDF-3 64-bit data) for MPAS/SMOIL compatibility

## Setup

### 1. Connect to Casper and Activate Environment

```bash
execcasper
```

Then load the `npl-2025b` conda environment (which includes `uxarray`):

```bash
conda load npl-2025b
```

### 2. Verify Dependencies

The script requires:
- **Required:** `numpy`, `netCDF4`
- **Remap backend (choose one):**
  - `uxarray` (preferred; included in `npl-2025b`)
  - `scipy` (fallback)

Check that `uxarray` is available:

```bash
python -c "import uxarray; print('uxarray available')"
```

## Configuration

### YAML Configuration File

Create a YAML file with the following structure:

```yaml
path_grid_base: /path/to/source_grid.nc          # Source MPAS grid (optional; defaults to source static file)
path_grid_new: /path/to/target_grid.nc           # Target MPAS grid (required)
path_static: /path/to/source_static_chems.nc     # Source static chemistry file (required)
output_path: /path/to/output_static_chems.nc     # Output file path (required)
xtime: "2019-07-15_12:00:00"                     # Optional: override xtime in output
```

**Example:** See `remap_paths.yaml.example` in this directory.

### YAML Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `path_grid_base` | No | Path to source MPAS grid file. If omitted, uses `path_static` for grid coordinates. |
| `path_grid_new` | Yes | Path to target MPAS grid file. |
| `path_static` | Yes | Path to source static chemistry NetCDF file. 
| `output_path` | Yes | Path where remapped output file will be written. 
| `xtime` | No | Optional timestamp to override in the output file (format: `YYYY-MM-DD_hh:mm:ss`). If omitted, preserves source xtime. |

## Usage

### Basic Usage with YAML Config

```bash
python remap_static_chems_to_grid.py --config-yaml remap_paths.yaml
```

### With Verbose Output

```bash
python remap_static_chems_to_grid.py \
  --config-yaml remap_paths.yaml \
  --verbose
```

### Override Paths from Command Line

CLI arguments override YAML values:

```bash
python remap_static_chems_to_grid.py \
  --config-yaml remap_paths.yaml \
  --target-grid /different/grid.nc
```

### Select Remap Engine Explicitly

```bash
python remap_static_chems_to_grid.py \
  --config-yaml remap_paths.yaml \
  --remap-engine uxarray
```

Supported engines:
- `auto` (default): tries uxarray first, then scipy
- `uxarray`: use uxarray (requires uxarray to be installed)
- `scipy`: use scipy (requires scipy to be installed)

## Command-Line Options

```
usage: remap_static_chems_to_grid.py [-h] [--config-yaml CONFIG_YAML]
                                     [--source-static SOURCE_STATIC]
                                     [--target-grid TARGET_GRID]
                                     [--output OUTPUT]
                                     [--source-grid SOURCE_GRID]
                                     [--no-copy-target-grid-fields]
                                     [--verbose]
                                     [--remap-engine {auto,uxarray,scipy}]

Options:
  -h, --help                      Show help message and exit
  --config-yaml CONFIG_YAML       Path to YAML config file with paths
  --source-static SOURCE_STATIC   Source static chemistry NetCDF file
  --target-grid TARGET_GRID       Target MPAS grid NetCDF file
  --output OUTPUT                 Output remapped static chemistry file (optional; overrides YAML)
  --source-grid SOURCE_GRID       Optional source grid file
  --no-copy-target-grid-fields    Remap all fields instead of copying mesh/topology from target
  --verbose                       Print per-variable remapping details
  --remap-engine {auto,uxarray,scipy}  Nearest-neighbor backend
```

## Example Workflow

1. **Prepare YAML config:**
   ```bash
   cp remap_paths.yaml.example remap_paths.yaml
   # Edit remap_paths.yaml with your actual file paths
   ```

2. **Activate environment:**
   ```bash
   execcasper
   conda load npl-2025b
   ```

3. **Run the script:**
   ```bash
   python remap_static_chems_to_grid.py \
     --config-yaml remap_paths.yaml \
     --remap-engine uxarray \
     --verbose
   ```

4. **Verify output:**
   ```bash
   ncdump -h x6.827394.static_chems.nc | head -100
   ```

## Output

The output file is created in **NetCDF4 format** for full MPAS compatibility.

**Metadata added to output:**
- `history`: Records remapping operation, engine used, and source files
- `remap_source_static`: Absolute path to source static file
- `remap_source_grid`: Absolute path to source grid file
- `remap_target_grid`: Absolute path to target grid file

## How It Works

### Remapping Strategy

1. **Dimensions:** Output dimensions are copied from source, but `nCells`, `nEdges`, `nVertices`, `maxEdges`, and `maxEdges2` are replaced with target grid sizes.

2. **Mesh/Topology Fields:** Variables like `latCell`, `lonCell`, connectivity arrays, etc., are copied directly from the target grid (safer for geometry/topology).

3. **Data Fields:** Remaining variables (e.g., `ter`, `greenfrac`, `soilcomp`) are remapped using nearest-neighbor on:
   - `nCells` → face centers
   - `nEdges` → edge centers
   - `nVertices` → nodes

4. **Dimension Resizing:** Variables with `maxEdges` or `maxEdges2` dimensions are truncated or padded as needed.

5. **xtime Override:** If `xtime` is provided in YAML, the output xtime variable is replaced.

### Coordinate Systems

- **uxarray backend:** Uses uxarray's KD-tree on Cartesian coordinates (x/y/z on unit sphere)
- **scipy backend:** Uses scipy's cKDTree for fast nearest-neighbor queries

## Troubleshooting

### Error: "No remap backend available"

Install one of the backends:
```bash
conda install uxarray   # Preferred
# or
conda install scipy
```

### Error: "Missing output path"

Ensure YAML contains `output_path` or pass `--output` on CLI.

### Error: "Missing source static file"

Ensure YAML contains `path_static` or pass `--source-static` on CLI.

### Error: "Missing target grid file"

Ensure YAML contains `path_grid_new` or pass `--target-grid` on CLI.

### Slow Remapping

If using `scipy` backend, consider switching to `uxarray`:
```bash
--remap-engine uxarray
```

## Output Validation

Check the remapped file:

```bash
# View header and variable list
ncdump -h x6.827394.static_chems.nc | head -150

# Check file size
ls -lh x6.827394.static_chems.nc

# Verify xtime was updated (if override was used)
ncdump -v xtime x6.827394.static_chems.nc
```

## Output

The output file is created in **CDF5 format** (NetCDF-3 64-bit data), which:
- Supports large files (>4 GB)
- Is required by MPAS/SMOIL to avoid errors
- Is backwards compatible with older NetCDF tools

## References

- MPAS Model Documentation: https://mpas-dev.github.io/
- uxarray Documentation: https://uxarray.readthedocs.io/
- NetCDF4 Documentation: https://www.unidata.ucar.edu/software/netcdf/

---

For questions or issues, consult the script header or the inline documentation.
