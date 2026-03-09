"""DXF area calculator for sheet metal weight estimation.

Parses a DXF file, detects outer contours and inner holes using a
containment-tree approach that mirrors the BricsCAD VBA
``DetectOuterRegionsFromSelection`` / ``FilterOuterRegions`` logic:

- Every closed boundary (LWPOLYLINE, POLYLINE, CIRCLE, ELLIPSE, SPLINE,
  or entities inside INSERT blocks) is converted to a Shapely polygon.
- Individual open entities (LINE, ARC, open LWPOLYLINE / POLYLINE / SPLINE)
  are collected as segments and stitched into closed loops by matching
  endpoints within a configurable tolerance (_STITCH_TOL_MM).  This handles
  common DXF shapes built from separate LINE entities (e.g. a square drawn
  with four individual lines).
- Polygons are sorted by area descending (largest first).
- For each polygon the *direct parent* — the smallest enclosing polygon — is
  found, giving its nesting depth.
- Even depth (0, 2, …) → outer contour or island → **positive** area.
- Odd depth  (1, 3, …) → hole / inner contour           → **negative** area.
- Net area = Σ outer areas − Σ hole areas (in mm²).
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Tuple

# ── Runtime dependencies (added to requirements.txt) ──────────────────────────
try:
    import ezdxf  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError("ezdxf is required: pip install ezdxf") from exc

try:
    from shapely.geometry import Polygon  # type: ignore
    from shapely.validation import make_valid  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError("shapely is required: pip install shapely") from exc

# ── Constants ──────────────────────────────────────────────────────────────────

_ARC_SEGMENTS: int = 64        # interpolation segments per full circle
_MIN_AREA_MM2: float = 1.0     # polygons smaller than this are ignored
_STITCH_TOL_MM: float = 0.01   # endpoint-matching tolerance for open-segment stitching (mm)

# Layer names that contain any of these substrings (case-insensitive) are
# excluded from area analysis (engraving marks, text, bend lines, etc.).
_IGNORED_LAYER_KEYWORDS: tuple[str, ...] = ("gravação", "texto", "dobra")

# DXF $INSUNITS code → scale factor to millimetres
_INSUNITS_TO_MM: dict[int, float] = {
    0: 1.0,           # Unitless – assume mm
    1: 25.4,          # Inches
    2: 304.8,         # Feet
    3: 1_609_344.0,   # Miles
    4: 1.0,           # Millimetres
    5: 10.0,          # Centimetres
    6: 1_000.0,       # Metres
    7: 1_000_000.0,   # Kilometres
    8: 2.54e-5,       # Micro-inches
    9: 0.0254,        # Mils
    10: 914.4,        # Yards
    13: 0.001,        # Microns
    14: 100.0,        # Decimetres
}


# ── Public API ─────────────────────────────────────────────────────────────────

def compute_dxf_net_area(path: "str | Path") -> Tuple[float, int, int]:
    """Return ``(net_area_mm2, outer_count, hole_count)``.

    Reads every entity in the DXF model space, converts closed boundaries to
    polygons, classifies them by nesting depth, and returns the signed net
    area already expressed in **mm²** (regardless of the DXF internal units).

    Parameters
    ----------
    path:
        Path to the ``.dxf`` file.

    Returns
    -------
    net_area_mm2:
        Net enclosed area in mm² (outer areas minus hole areas).
    outer_count:
        Number of identified outer / top-level contours.
    hole_count:
        Number of identified inner contours (holes).

    Raises
    ------
    ezdxf.DXFStructureError, ezdxf.DXFError:
        If the file cannot be read as a valid DXF.
    ValueError:
        If no closed contours are found in the file.
    """
    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()

    # Determine unit scale factor
    insunits: int = int(doc.header.get("$INSUNITS", 0))
    scale: float = _INSUNITS_TO_MM.get(insunits, 1.0)

    polygons: List[Polygon] = []
    _collect_polygons(list(msp), scale, polygons)

    # Also stitch individual open entities (LINE, ARC, open polylines …)
    # into closed loops and add any resulting polygons.
    open_segs = _collect_open_segments(list(msp), scale)
    for loop_pts in _stitch_segs_to_loops(open_segs, tol=_STITCH_TOL_MM):
        try:
            poly = Polygon(loop_pts)
            if not poly.is_valid:
                poly = make_valid(poly)
            if poly.geom_type == "Polygon" and poly.area > _MIN_AREA_MM2:
                polygons.append(poly)
            elif poly.geom_type in ("MultiPolygon", "GeometryCollection"):
                for geom in poly.geoms:
                    if geom.geom_type == "Polygon" and geom.area > _MIN_AREA_MM2:
                        polygons.append(geom)
        except Exception:
            pass

    if not polygons:
        raise ValueError("No closed contours found in the DXF file.")

    # Sort descending by area (mirrors VBA sort-by-area)
    polygons.sort(key=lambda p: p.area, reverse=True)

    n = len(polygons)

    # Build containment tree: find the direct parent (smallest enclosing polygon)
    # for each polygon.  Because the list is sorted largest-first, every
    # potential parent j < i is guaranteed to be at least as large as i.
    direct_parent: List[Optional[int]] = [None] * n
    for i in range(n):
        for j in range(i):
            if polygons[j].contains(polygons[i]):
                # j contains i; prefer the tightest (smallest area) container
                if direct_parent[i] is None or polygons[j].area < polygons[direct_parent[i]].area:
                    direct_parent[i] = j

    # Compute nesting depth for each polygon
    depth: List[int] = [0] * n
    for i in range(n):
        if direct_parent[i] is not None:
            depth[i] = depth[direct_parent[i]] + 1

    # Accumulate net area
    net_area = 0.0
    outer_count = 0
    hole_count = 0
    for i, poly in enumerate(polygons):
        if depth[i] % 2 == 0:   # outer contour or island inside hole
            net_area += poly.area
            outer_count += 1
        else:                    # hole / inner contour
            net_area -= poly.area
            hole_count += 1

    return net_area, outer_count, hole_count


# ── Layer filtering ───────────────────────────────────────────────────────────

def _layer_is_ignored(entity) -> bool:
    """Return True if the entity's layer name contains any ignored keyword."""
    try:
        layer = entity.dxf.layer.lower()
    except Exception:
        return False
    return any(kw in layer for kw in _IGNORED_LAYER_KEYWORDS)


# ── Entity collection ──────────────────────────────────────────────────────────

def _collect_polygons(entities: list, scale: float, out: List[Polygon]) -> None:
    """Recursively convert DXF entities to Shapely Polygons and append to *out*."""
    for entity in entities:
        dxftype = entity.dxftype()

        # Expand block references so nested geometries are included
        if dxftype == "INSERT":
            try:
                _collect_polygons(list(entity.virtual_entities()), scale, out)
            except Exception:
                pass
            continue

        if _layer_is_ignored(entity):
            continue

        pts = _entity_to_points(entity, scale)
        if len(pts) < 3:
            continue

        try:
            poly = Polygon(pts)
            if not poly.is_valid:
                poly = make_valid(poly)

            # make_valid may return a MultiPolygon or GeometryCollection
            if poly.geom_type == "Polygon":
                if poly.area > _MIN_AREA_MM2:
                    out.append(poly)
            elif poly.geom_type in ("MultiPolygon", "GeometryCollection"):
                for geom in poly.geoms:
                    if geom.geom_type == "Polygon" and geom.area > _MIN_AREA_MM2:
                        out.append(geom)
        except Exception:
            pass


# ── Entity → 2-D point list ───────────────────────────────────────────────────

def _entity_to_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Return a list of (x, y) mm points for a *closed* DXF entity, or [] if
    the entity is open / unsupported.  Open entities (LINE, ARC, …) are
    handled separately via _collect_open_segments / _stitch_segs_to_loops."""
    t = entity.dxftype()
    if t == "LWPOLYLINE":
        return _lwpolyline_points(entity, scale) if entity.is_closed else []
    if t == "POLYLINE":
        return _polyline_points(entity, scale) if entity.is_closed else []
    if t == "CIRCLE":
        return _circle_points(entity, scale)
    if t == "ELLIPSE":
        return _ellipse_points(entity, scale)
    if t == "SPLINE":
        return _spline_points(entity, scale)
    return []


def _lwpolyline_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Convert a closed LWPOLYLINE (with optional bulge arcs) to 2-D points."""
    pts_bulge = list(entity.get_points(format="xyb"))  # [(x, y, bulge), …]
    n = len(pts_bulge)
    if n < 2:
        return []

    result: List[Tuple[float, float]] = []
    for i in range(n):
        x0, y0, bulge = pts_bulge[i]
        x1, y1, _ = pts_bulge[(i + 1) % n]

        result.append((x0 * scale, y0 * scale))
        if abs(bulge) > 1e-9:
            result.extend(_bulge_to_arc_points(x0, y0, x1, y1, bulge, scale))

    return result


def _bulge_to_arc_points(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    bulge: float,
    scale: float,
) -> List[Tuple[float, float]]:
    """Approximate a DXF bulge-arc segment as intermediate 2-D points.

    The DXF bulge value is defined as ``tan(included_angle / 4)``.
    Positive bulge → counter-clockwise arc; negative → clockwise.
    The start and end points themselves are *not* included in the returned
    list (the caller already appends the start point).
    """
    dx, dy = x1 - x0, y1 - y0
    chord = math.hypot(dx, dy)
    if chord < 1e-12:
        return []

    theta = 4.0 * math.atan(abs(bulge))             # included angle [rad]
    radius = chord / (2.0 * math.sin(theta / 2.0))   # arc radius

    # Mid-chord point and perpendicular direction
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    sagitta = math.sqrt(max(radius ** 2 - (chord / 2.0) ** 2, 0.0))
    perp_x, perp_y = -dy / chord, dx / chord

    # Arc centre is displaced perpendicularly from the chord mid-point.
    # Sign follows the DXF convention: positive bulge → CCW → centre is to
    # the left of the directed chord (positive perpendicular side).
    sign = math.copysign(1.0, bulge)
    cx = mx + sign * sagitta * perp_x
    cy = my + sign * sagitta * perp_y

    start_angle = math.atan2(y0 - cy, x0 - cx)
    end_angle = math.atan2(y1 - cy, x1 - cx)

    if bulge > 0:   # CCW
        if end_angle <= start_angle:
            end_angle += 2.0 * math.pi
    else:           # CW
        if end_angle >= start_angle:
            end_angle -= 2.0 * math.pi

    # Number of *intermediate* points (exclude start; end belongs to next seg)
    num_pts = max(2, round(abs(theta) / (2.0 * math.pi) * _ARC_SEGMENTS)) - 1

    pts = []
    for k in range(1, num_pts):
        t = k / num_pts
        angle = start_angle + t * (end_angle - start_angle)
        pts.append((
            (cx + radius * math.cos(angle)) * scale,
            (cy + radius * math.sin(angle)) * scale,
        ))
    return pts


def _polyline_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Convert a closed 2-D POLYLINE to a list of points."""
    try:
        return [
            (v.dxf.location.x * scale, v.dxf.location.y * scale)
            for v in entity.vertices
        ]
    except Exception:
        return []


def _circle_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Approximate a CIRCLE as a regular polygon."""
    try:
        cx = entity.dxf.center.x * scale
        cy = entity.dxf.center.y * scale
        r = entity.dxf.radius * scale
    except Exception:
        return []

    step = 2.0 * math.pi / _ARC_SEGMENTS
    return [
        (cx + r * math.cos(i * step), cy + r * math.sin(i * step))
        for i in range(_ARC_SEGMENTS)
    ]


def _ellipse_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Approximate an ELLIPSE (may be a full ellipse or an arc) as points."""
    try:
        # ezdxf's flattening() returns OCS-space Vec3 points with tolerance
        raw = [(p.x * scale, p.y * scale) for p in entity.flattening(0.1 / max(scale, 1e-9))]
        if len(raw) >= 3:
            return raw
    except Exception:
        pass

    # Parametric fallback
    try:
        cx = entity.dxf.center.x * scale
        cy = entity.dxf.center.y * scale
        maj = entity.dxf.major_axis
        a = math.hypot(maj.x, maj.y) * scale
        b = a * float(entity.dxf.ratio)
        ang = math.atan2(maj.y, maj.x)
        step = 2.0 * math.pi / _ARC_SEGMENTS
        return [
            (
                cx + a * math.cos(i * step) * math.cos(ang) - b * math.sin(i * step) * math.sin(ang),
                cy + a * math.cos(i * step) * math.sin(ang) + b * math.sin(i * step) * math.cos(ang),
            )
            for i in range(_ARC_SEGMENTS)
        ]
    except Exception:
        return []


def _spline_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Approximate a closed SPLINE as points via ezdxf's flattening."""
    try:
        if not entity.closed:
            return []
        raw = [(p.x * scale, p.y * scale) for p in entity.flattening(0.1 / max(scale, 1e-9))]
        return raw if len(raw) >= 3 else []
    except Exception:
        return []


# ── Open-segment collection ────────────────────────────────────────────────────

def _arc_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Approximate a DXF ARC entity as an ordered point sequence (CCW)."""
    try:
        cx = entity.dxf.center.x * scale
        cy = entity.dxf.center.y * scale
        r = entity.dxf.radius * scale
        start_angle = math.radians(entity.dxf.start_angle)
        end_angle = math.radians(entity.dxf.end_angle)
    except Exception:
        return []

    # DXF arcs are always CCW; wrap end_angle so it is > start_angle
    if end_angle <= start_angle:
        end_angle += 2.0 * math.pi

    span = end_angle - start_angle
    num_pts = max(3, round(span / (2.0 * math.pi) * _ARC_SEGMENTS))
    return [
        (cx + r * math.cos(start_angle + k / num_pts * span),
         cy + r * math.sin(start_angle + k / num_pts * span))
        for k in range(num_pts + 1)
    ]


def _lwpolyline_open_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Convert an open LWPOLYLINE (with optional bulge arcs) to 2-D points."""
    pts_bulge = list(entity.get_points(format="xyb"))
    n = len(pts_bulge)
    if n < 2:
        return []

    result: List[Tuple[float, float]] = []
    for i in range(n - 1):
        x0, y0, bulge = pts_bulge[i]
        x1, y1, _ = pts_bulge[i + 1]
        result.append((x0 * scale, y0 * scale))
        if abs(bulge) > 1e-9:
            result.extend(_bulge_to_arc_points(x0, y0, x1, y1, bulge, scale))

    xn, yn, _ = pts_bulge[-1]
    result.append((xn * scale, yn * scale))
    return result


def _polyline_open_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Convert an open 2-D POLYLINE to a list of points."""
    try:
        return [
            (v.dxf.location.x * scale, v.dxf.location.y * scale)
            for v in entity.vertices
        ]
    except Exception:
        return []


def _open_entity_to_points(entity, scale: float) -> List[Tuple[float, float]]:
    """Return an ordered (start → end) point list for LINE, ARC, and open
    polyline / spline entities.  Returns [] for unsupported or closed entities.
    """
    t = entity.dxftype()
    if t == "LINE":
        try:
            s = entity.dxf.start
            e = entity.dxf.end
            return [(s.x * scale, s.y * scale), (e.x * scale, e.y * scale)]
        except Exception:
            return []
    if t == "ARC":
        return _arc_points(entity, scale)
    if t == "LWPOLYLINE" and not entity.is_closed:
        return _lwpolyline_open_points(entity, scale)
    if t == "POLYLINE" and not entity.is_closed:
        return _polyline_open_points(entity, scale)
    if t == "SPLINE":
        try:
            if not entity.closed:
                raw = [(p.x * scale, p.y * scale)
                       for p in entity.flattening(0.1 / max(scale, 1e-9))]
                return raw if len(raw) >= 2 else []
        except Exception:
            pass
    return []


def _collect_open_segments(entities: list, scale: float) -> List[List[Tuple[float, float]]]:
    """Recursively collect LINE / ARC / open-polyline entities as point sequences."""
    result: List[List[Tuple[float, float]]] = []
    for entity in entities:
        dxftype = entity.dxftype()
        if dxftype == "INSERT":
            try:
                result.extend(_collect_open_segments(list(entity.virtual_entities()), scale))
            except Exception:
                pass
            continue
        if _layer_is_ignored(entity):
            continue
        pts = _open_entity_to_points(entity, scale)
        if len(pts) >= 2:
            result.append(pts)
    return result


# ── Segment stitching ──────────────────────────────────────────────────────────

def _stitch_segs_to_loops(
    segments: List[List[Tuple[float, float]]],
    tol: float,
) -> List[List[Tuple[float, float]]]:
    """Greedily stitch open segments into closed loops by matching endpoints.

    Parameters
    ----------
    segments:
        Each element is an ordered list of (x, y) mm points for one open
        entity (LINE, ARC, open polyline …).  ``seg[0]`` is the start and
        ``seg[-1]`` is the end.
    tol:
        Endpoint-matching tolerance in mm (same unit as the coordinates).

    Returns
    -------
    List of closed point sequences (the closing point is *not* repeated).
    """
    if not segments:
        return []

    def snap(pt: Tuple[float, float]) -> Tuple[float, float]:
        return (round(pt[0] / tol) * tol, round(pt[1] / tol) * tol)

    n = len(segments)
    seg_start = [snap(seg[0]) for seg in segments]
    seg_end = [snap(seg[-1]) for seg in segments]

    # Build adjacency: snapped endpoint → [(seg_idx, reversed)]
    #   (i, False) - enter at seg[0], exit at seg[-1]  (forward traversal)
    #   (i, True)  - enter at seg[-1], exit at seg[0]  (reverse traversal)
    adj: dict = defaultdict(list)
    for i in range(n):
        adj[seg_start[i]].append((i, False))
        adj[seg_end[i]].append((i, True))

    used = [False] * n
    loops: List[List[Tuple[float, float]]] = []

    for start_idx in range(n):
        if used[start_idx]:
            continue

        # Start a chain with this segment traversed forward
        chain: List[Tuple[int, bool]] = [(start_idx, False)]
        chain_set = {start_idx}
        loop_origin = seg_start[start_idx]
        current_node = seg_end[start_idx]
        closed = (current_node == loop_origin)

        for _ in range(n):
            if closed:
                break
            found = False
            for nbr_idx, nbr_rev in adj[current_node]:
                if nbr_idx in chain_set:
                    continue
                chain.append((nbr_idx, nbr_rev))
                chain_set.add(nbr_idx)
                current_node = seg_start[nbr_idx] if nbr_rev else seg_end[nbr_idx]
                found = True
                closed = (current_node == loop_origin)
                break
            if not found:
                break

        if not closed:
            continue  # open chain — skip, don't mark as used

        # Assemble the closed point list (exclude the shared closing point)
        loop_pts: List[Tuple[float, float]] = []
        for seg_idx, rev in chain:
            used[seg_idx] = True
            seg = segments[seg_idx]
            pts = list(reversed(seg)) if rev else seg
            loop_pts.extend(pts[:-1])

        if len(loop_pts) >= 3:
            loops.append(loop_pts)

    return loops
