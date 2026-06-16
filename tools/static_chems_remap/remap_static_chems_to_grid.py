#!/usr/bin/env python3
"""Remap an MPAS static chemistry file from one grid to another.

This script is intended for files like `x1.163842.static_chems.nc` and a new
MPAS mesh file (for example `x6.827394.grid.nc`).

Approach:
1. Create an output file with dimensions mostly copied from the source static
   file, but replacing grid-size dimensions (`nCells`, `nEdges`, `nVertices`,
   `maxEdges`, `maxEdges2`) with the target grid sizes.
2. For mesh/topology variables that exist in the target grid file, copy those
   values directly from the target grid.
3. For remaining variables containing `nCells`, `nEdges`, or `nVertices`, apply
   nearest-neighbor remapping using source/target Cartesian coordinates.
4. For variables that include `maxEdges` or `maxEdges2` and are not copied from
   target grid, resize those dimensions by truncating/padding as needed.
5. Write output in CDF5 format (NetCDF-3 64-bit data) for MPAS/SMOIL compatibility.

Dependencies:
- Required: numpy, netCDF4
- Optional: pyyaml (if unavailable, a simple flat YAML parser is used)
- Remap backend (choose with --remap-engine):
    - uxarray (preferred when available)
    - scipy (KD-tree fallback)

If neither uxarray nor scipy is available, the script raises an error with
install guidance.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
from pathlib import Path
from typing import Dict, Tuple

import netCDF4 as nc
import numpy as np


HORIZONTAL_DIMS = ("nCells", "nEdges", "nVertices")
TOPO_DIMS = ("maxEdges", "maxEdges2")
GRID_SIZED_DIMS = HORIZONTAL_DIMS + TOPO_DIMS
COORD_SUFFIX = {
    "nCells": "Cell",
    "nEdges": "Edge",
    "nVertices": "Vertex",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remap MPAS static_chems file to a new MPAS grid."
    )
    parser.add_argument(
        "--config-yaml",
        default=None,
        help=(
            "Optional YAML file containing path_grid_base, path_grid_new, "
            "path_static, output_path, and xtime. CLI path args override YAML values."
        ),
    )
    parser.add_argument(
        "--source-static",
        required=False,
        help="Source static chemistry NetCDF file (e.g., x1.163842.static_chems.nc)",
    )
    parser.add_argument(
        "--target-grid",
        required=False,
        help="Target MPAS grid NetCDF file (e.g., x6.827394.grid.nc)",
    )
    parser.add_argument(
        "--output",
        required=False,
        default=None,
        help="Output remapped static chemistry NetCDF file. If omitted, read from YAML.",
    )
    parser.add_argument(
        "--source-grid",
        default=None,
        help=(
            "Optional source grid file. If omitted, the source static file is used "
            "for source grid coordinates."
        ),
    )
    parser.add_argument(
        "--no-copy-target-grid-fields",
        action="store_true",
        help=(
            "If set, do not preferentially copy mesh/topology variables from "
            "target grid; remap everything instead."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-variable remapping details.",
    )
    parser.add_argument(
        "--remap-engine",
        choices=("auto", "uxarray", "scipy"),
        default="auto",
        help="Nearest-neighbor backend. 'auto' tries uxarray first, then scipy.",
    )
    return parser.parse_args()


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _load_simple_yaml(path: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.split("#", 1)[0].strip()
            data[key] = _strip_quotes(value)
    return data


def load_yaml_config(path: str) -> Dict[str, str]:
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as f:
            parsed = yaml.safe_load(f) or {}
        if not isinstance(parsed, dict):
            raise RuntimeError("YAML config must contain a top-level mapping.")
        return {str(k): str(v) for k, v in parsed.items() if v is not None}
    except ModuleNotFoundError:
        return _load_simple_yaml(path)


def resolve_paths(args: argparse.Namespace) -> Tuple[str, str, str, str | None, str | None]:
    cfg: Dict[str, str] = {}
    if args.config_yaml:
        cfg = load_yaml_config(args.config_yaml)

    source_static = args.source_static or cfg.get("path_static")
    target_grid = args.target_grid or cfg.get("path_grid_new")
    source_grid = args.source_grid or cfg.get("path_grid_base")
    output_path = args.output or cfg.get("output_path")
    xtime = cfg.get("xtime")

    if not source_static:
        raise RuntimeError(
            "Missing source static file. Provide --source-static or path_static in YAML."
        )
    if not target_grid:
        raise RuntimeError(
            "Missing target grid file. Provide --target-grid or path_grid_new in YAML."
        )
    if not output_path:
        raise RuntimeError(
            "Missing output path. Provide --output or output_path in YAML."
        )

    source_static = str(Path(source_static).expanduser())
    target_grid = str(Path(target_grid).expanduser())
    source_grid = str(Path(source_grid).expanduser()) if source_grid else None
    output_path = str(Path(output_path).expanduser())

    return source_static, target_grid, output_path, source_grid, xtime


def _fill_value_for(var: nc.Variable):
    return getattr(var, "_FillValue", None)


def _copy_var_attrs(src_var: nc.Variable, dst_var: nc.Variable) -> None:
    for attr in src_var.ncattrs():
        if attr == "_FillValue":
            continue
        dst_var.setncattr(attr, src_var.getncattr(attr))


def _coord_matrix(ds: nc.Dataset, dim_name: str) -> np.ndarray:
    suffix = COORD_SUFFIX[dim_name]
    x = np.asarray(ds.variables[f"x{suffix}"][:], dtype=np.float64)
    y = np.asarray(ds.variables[f"y{suffix}"][:], dtype=np.float64)
    z = np.asarray(ds.variables[f"z{suffix}"][:], dtype=np.float64)
    xyz = np.column_stack([x, y, z])

    norms = np.linalg.norm(xyz, axis=1)
    norms[norms == 0.0] = 1.0
    xyz /= norms[:, None]
    return xyz


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def select_engine(requested: str) -> str:
    if requested == "uxarray":
        if not _module_available("uxarray"):
            raise RuntimeError(
                "--remap-engine uxarray requested, but uxarray is not installed."
            )
        return "uxarray"

    if requested == "scipy":
        if not _module_available("scipy"):
            raise RuntimeError(
                "--remap-engine scipy requested, but scipy is not installed."
            )
        return "scipy"

    if _module_available("uxarray"):
        return "uxarray"
    if _module_available("scipy"):
        return "scipy"

    raise RuntimeError(
        "No remap backend available. Install uxarray (preferred) or scipy."
    )


def build_nearest_map(
    src_ds: nc.Dataset,
    dst_ds: nc.Dataset,
    dim_name: str,
) -> np.ndarray:
    src_xyz = _coord_matrix(src_ds, dim_name)
    dst_xyz = _coord_matrix(dst_ds, dim_name)

    try:
        from scipy.spatial import cKDTree  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "scipy is required for practical nearest-neighbor remapping. "
            "Install with: pip install scipy (or conda install scipy)."
        ) from exc

    tree = cKDTree(src_xyz)
    _, idx = tree.query(dst_xyz, k=1)
    return np.asarray(idx, dtype=np.int64)


def build_nearest_map_uxarray(
    source_grid_path: str,
    dst_ds: nc.Dataset,
    dim_name: str,
) -> np.ndarray:
    try:
        import uxarray as ux  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "uxarray remap backend requested but uxarray is not importable."
        ) from exc

    coord_name_by_dim = {
        "nCells": "face centers",
        "nEdges": "edge centers",
        "nVertices": "nodes",
    }

    src_grid = ux.open_grid(source_grid_path, use_dual=False)
    src_tree = src_grid.get_kd_tree(
        coordinates=coord_name_by_dim[dim_name],
        coordinate_system="cartesian",
    )

    dst_xyz = _coord_matrix(dst_ds, dim_name)
    idx = src_tree.query(dst_xyz, k=1, return_distance=False)
    return np.asarray(idx, dtype=np.int64).reshape(-1)


def _resize_axis(
    arr: np.ndarray,
    axis: int,
    new_size: int,
    fill_value,
) -> np.ndarray:
    old_size = arr.shape[axis]
    if old_size == new_size:
        return arr

    if old_size > new_size:
        slicer = [slice(None)] * arr.ndim
        slicer[axis] = slice(0, new_size)
        return arr[tuple(slicer)]

    pad_shape = list(arr.shape)
    pad_shape[axis] = new_size - old_size

    if fill_value is None:
        if np.issubdtype(arr.dtype, np.floating):
            pad_chunk = np.full(pad_shape, np.nan, dtype=arr.dtype)
        else:
            pad_chunk = np.zeros(pad_shape, dtype=arr.dtype)
    else:
        pad_chunk = np.full(pad_shape, fill_value, dtype=arr.dtype)

    return np.concatenate([arr, pad_chunk], axis=axis)


def _var_uses_horizontal_dim(var: nc.Variable) -> bool:
    return any(d in HORIZONTAL_DIMS for d in var.dimensions)


def _copy_target_var_if_possible(
    var_name: str,
    src_var: nc.Variable,
    target_grid: nc.Dataset,
    copy_target_grid_fields: bool,
) -> Tuple[bool, np.ndarray | None]:
    if not copy_target_grid_fields:
        return False, None

    if var_name not in target_grid.variables:
        return False, None

    if not _var_uses_horizontal_dim(src_var):
        return False, None

    tgt_var = target_grid.variables[var_name]
    if src_var.dimensions != tgt_var.dimensions:
        return False, None

    return True, np.asarray(tgt_var[:])


def remap_static_file(
    source_static_path: str,
    target_grid_path: str,
    output_path: str,
    source_grid_path: str | None = None,
    copy_target_grid_fields: bool = True,
    verbose: bool = False,
    remap_engine: str = "auto",
    xtime_override: str | None = None,
) -> None:
    source_grid_path = source_grid_path or source_static_path
    engine = select_engine(remap_engine)

    with nc.Dataset(source_static_path, "r") as src_static, nc.Dataset(
        source_grid_path, "r"
    ) as src_grid, nc.Dataset(target_grid_path, "r") as tgt_grid, nc.Dataset(
        output_path, "w", format="NETCDF3_64BIT_DATA"
    ) as dst:
        # Dimensions
        for dim_name, dim in src_static.dimensions.items():
            if dim_name in GRID_SIZED_DIMS and dim_name in tgt_grid.dimensions:
                dst_size = len(tgt_grid.dimensions[dim_name])
            else:
                dst_size = None if dim.isunlimited() else len(dim)
            dst.createDimension(dim_name, dst_size)

        # Global attributes
        for attr in src_static.ncattrs():
            dst.setncattr(attr, src_static.getncattr(attr))

        timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        hist_line = (
            f"{timestamp}: remapped to {os.path.basename(target_grid_path)} "
            f"with nearest-neighbor for horizontal dimensions (engine={engine})"
        )
        old_hist = getattr(src_static, "history", "")
        dst.setncattr("history", f"{old_hist}\n{hist_line}".strip())
        dst.setncattr("remap_source_static", os.path.abspath(source_static_path))
        dst.setncattr("remap_source_grid", os.path.abspath(source_grid_path))
        dst.setncattr("remap_target_grid", os.path.abspath(target_grid_path))

        # Build nearest-neighbor maps once
        nn_maps: Dict[str, np.ndarray] = {}
        for dim_name in HORIZONTAL_DIMS:
            if dim_name in src_static.dimensions and dim_name in tgt_grid.dimensions:
                if verbose:
                    print(f"Building nearest map for {dim_name} with {engine}...")
                if engine == "uxarray":
                    nn_maps[dim_name] = build_nearest_map_uxarray(
                        source_grid_path,
                        tgt_grid,
                        dim_name,
                    )
                else:
                    nn_maps[dim_name] = build_nearest_map(src_grid, tgt_grid, dim_name)

        # Variables
        for var_name, src_var in src_static.variables.items():
            fill_value = _fill_value_for(src_var)
            dst_var = dst.createVariable(
                var_name,
                src_var.datatype,
                src_var.dimensions,
                zlib=True,
                complevel=1,
                fill_value=fill_value,
            )
            _copy_var_attrs(src_var, dst_var)

            copied, target_data = _copy_target_var_if_possible(
                var_name,
                src_var,
                tgt_grid,
                copy_target_grid_fields,
            )
            if copied:
                if verbose:
                    print(f"[target grid] {var_name}")
                dst_var[:] = target_data
                continue

            data = np.asarray(src_var[:])
            op_notes = []

            # Apply nearest-neighbor remap along each horizontal axis present.
            for dim_name, nn_idx in nn_maps.items():
                if dim_name in src_var.dimensions:
                    axis = src_var.dimensions.index(dim_name)
                    data = np.take(data, nn_idx, axis=axis)
                    op_notes.append(f"nn({dim_name})")

            # Resize topology dims when needed.
            for topo_dim in TOPO_DIMS:
                if topo_dim in src_var.dimensions:
                    axis = src_var.dimensions.index(topo_dim)
                    new_size = len(dst.dimensions[topo_dim])
                    old_size = data.shape[axis]
                    data = _resize_axis(data, axis, new_size, fill_value)
                    if old_size != new_size:
                        op_notes.append(f"resize({topo_dim}:{old_size}->{new_size})")

            if verbose and op_notes:
                print(f"[remap] {var_name}: {', '.join(op_notes)}")

            dst_var[:] = data

        # Override xtime if provided
        if xtime_override and "xtime" in dst.variables:
            xtime_var = dst.variables["xtime"]
            strlen = len(dst.dimensions.get("StrLen", 64))
            padded_xtime = xtime_override.ljust(strlen)
            xtime_var[0] = padded_xtime
            if verbose:
                print(f"[xtime override] {xtime_override}")


def main() -> None:
    args = parse_args()
    source_static, target_grid, output_path, source_grid, xtime = resolve_paths(args)

    remap_static_file(
        source_static_path=source_static,
        target_grid_path=target_grid,
        output_path=output_path,
        source_grid_path=source_grid,
        copy_target_grid_fields=not args.no_copy_target_grid_fields,
        verbose=args.verbose,
        remap_engine=args.remap_engine,
        xtime_override=xtime,
    )

    print(f"Wrote remapped file: {output_path}")


if __name__ == "__main__":
    main()
