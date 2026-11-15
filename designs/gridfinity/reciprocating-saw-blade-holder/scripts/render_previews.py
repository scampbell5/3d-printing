#!/usr/bin/env python3
"""Generate accurate preview PNGs from the project's checked-in V4 STL meshes.

Uses VTK for offscreen rendering. These are CAD previews, not photographs
of physical prints; colors are illustrative. This script does not alter STL files.

Run from repository root (after uv.lock exists):
    uv run --locked --no-default-groups --group cad-saw-blade-holder \
        python designs/gridfinity/reciprocating-saw-blade-holder/scripts/render_previews.py
"""
from __future__ import annotations

import argparse
from pathlib import Path
import vtk

PROJECT = Path(__file__).resolve().parents[1]
STLS = PROJECT / "stl"
COLORS = {"holder": (0.75, 0.80, 0.85), "lid": (0.20, 0.43, 0.70)}


def render(name: str, parts: list[tuple], camera_pos: tuple, camera_focus: tuple,
           scale: float, view_up: tuple, output_dir: Path, size: tuple[int, int]):
    scene = vtk.vtkRenderer()
    scene.SetBackground(0.98, 0.985, 0.99)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(*size)
    window.SetMultiSamples(6)
    window.AddRenderer(scene)
    for type_, stl_name, position, rotation_z in parts:
        src = STLS / stl_name
        if not src.is_file():
            raise FileNotFoundError(f"Required STL not found: {src}")
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(src))
        reader.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*COLORS[type_])
        prop.SetAmbient(0.45)
        prop.SetDiffuse(0.63)
        prop.SetSpecular(0.18)
        prop.SetSpecularPower(26)
        prop.SetInterpolationToPhong()
        if rotation_z:
            actor.RotateZ(rotation_z)
        actor.SetPosition(*position)
        scene.AddActor(actor)

    for loc, strength in [((-250, -350, 380), 1.1), ((280, 220, 320), 0.7)]:
        lamp = vtk.vtkLight()
        lamp.SetLightTypeToSceneLight()
        lamp.SetPosition(*loc)
        lamp.SetFocalPoint(0, 0, 10)
        lamp.SetIntensity(strength)
        scene.AddLight(lamp)

    camera = scene.GetActiveCamera()
    camera.SetFocalPoint(*camera_focus)
    camera.SetPosition(*camera_pos)
    camera.SetViewUp(*view_up)
    camera.SetParallelProjection(True)
    camera.SetParallelScale(scale)
    scene.ResetCameraClippingRange()
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.SetInputBufferTypeToRGB()
    capture.Update()
    outfile = output_dir / f"{name}.png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(outfile))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    if outfile.stat().st_size == 0:
        raise RuntimeError(f"Empty preview: {outfile}")
    print(f"Rendered {outfile}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "images")
    parser.add_argument("--width", type=int, default=1500)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()
    if args.width < 300 or args.height < 300:
        parser.error("Preview dimensions must be >=300 pixels")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    holder = ("holder", "holder.stl", (0, 0, 0), 0)
    lid = ("lid", "sliding-lid-assembled.stl", (0, 0, 0), 0)
    layout = [
        ("hero-exploded", [holder, ("lid", "sliding-lid-assembled.stl", (-9, -46, 34), 0)], (280, -290, 275), (0, -12, 30), 100, (0, 0, 1)),
        ("closed-lid", [holder, lid], (310, -240, 200), (0, 0, 24), 85, (0, 0, 1)),
        ("holder-open", [holder], (200, -175, 285), (0, 0, 22), 85, (0, 0, 1)),
        ("gridfinity-feet", [holder], (160, -180, -195), (0, 0, 18), 90, (0, 0, 1)),
        ("print-orientation", [("holder", "holder.stl", (0, 54, 0), 90),
                               ("lid", "sliding-lid-print-face-down.stl", (0, -54, 0), 90)],
         (0, -1, 400), (0, 0, 0), 95, (0, 1, 0)),
    ]
    for name, parts, cam, target, scale, up in layout:
        render(name, parts, cam, target, scale, up, args.output_dir, (args.width, args.height))


if __name__ == "__main__":
    main()
