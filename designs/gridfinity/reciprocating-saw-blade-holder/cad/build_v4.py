"""V4 support-minimized Gridfinity saw-blade storage; mm.
Original body above z=5.10 and six chamfered feet. Existing outer walls
serve as sleeve guide tracks; no protruding rails or downward hooks.
"""
from pathlib import Path
import os
import time, numpy as np, vtk, trimesh, cadquery as cq
from vtk.util.numpy_support import vtk_to_numpy
from skimage.measure import marching_cubes
from scipy.ndimage import label
ROOT = Path(__file__).resolve().parents[1]
# CI builds produce isolated artifacts instead of overwriting committed STLs.
O = Path(os.environ.get('DESIGN_BUILD_OUTPUT_DIR', str(ROOT / 'stl'))).resolve()
INPUT = ROOT / 'cad' / 'inputs'
WORK = Path(os.environ.get('DESIGN_BUILD_WORK_DIR', str(ROOT / 'cad' / 'build'))).resolve()
O.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)
# CadQuery is used for the fit-critical lid and lightweight detent pockets.
def block(x0,x1,y0,y1,z0,z1):
 return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
# The holder is the original capped upper body + contiguous lofted feet.
# The feet merge into the holder at z5.1; voxel Boolean ensures a single solid.
body=INPUT/'body_capped.stl'; feet=INPUT/'chamfered_feet.stl'
# Shallow open-top relief pockets at the lead side, 7 mm along Y, 0.9 mm deep.
# By extending beyond the top, these have no horizontal cavity ceilings.
pockets=[]
for s in (-1,1):
 x0,x1=(19.75,21.5) if s==1 else (-21.5,-19.75)
 pockets.append(block(x0,x1,-122.0,-114.5,35.1,42))
pocket=pockets[0].union(pockets[1]).clean()
cq.exporters.export(pocket.val(),str(WORK/'detent_reliefs.stl'))

pitch=.4; origin=(-25.6,-130.8,-1.2); dim=(128,654,105)
print('voxel grid',dim,flush=True)
img=vtk.vtkImageData();img.SetOrigin(*origin);img.SetSpacing(pitch,pitch,pitch);img.SetDimensions(*dim);img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
base_array=vtk_to_numpy(img.GetPointData().GetScalars());base_array[:]=1

def voxelize(path):
 t=time.time(); r=vtk.vtkSTLReader();r.SetFileName(str(path));r.Update()
 st=vtk.vtkPolyDataToImageStencil();st.SetInputConnection(r.GetOutputPort());st.SetOutputOrigin(origin);st.SetOutputSpacing(pitch,pitch,pitch);st.SetOutputWholeExtent(img.GetExtent());st.Update()
 out=vtk.vtkImageStencil();out.SetInputData(img);out.SetStencilConnection(st.GetOutputPort());out.SetBackgroundValue(0);out.Update()
 a=vtk_to_numpy(out.GetOutput().GetPointData().GetScalars()).reshape((dim[2],dim[1],dim[0])).astype(bool)
 print('voxelized',path.name,int(a.sum()),round(time.time()-t,1),'s',flush=True)
 return a
vbody=voxelize(body)
vfeet=voxelize(feet)
vpockets=voxelize(WORK/'detent_reliefs.stl')
vholder=(vbody|vfeet)&(~vpockets)
del vbody,vfeet,vpockets
l,n=label(vholder); counts=np.bincount(l.ravel())[1:];print('components',n,'largest',sorted(counts,reverse=True)[:5],flush=True); del l
vertices, faces, _, _=marching_cubes(vholder.astype(np.uint8),.5,spacing=(pitch,pitch,pitch))
vertices=vertices[:,[2,1,0]]+np.array(origin)
mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=True)
print('mesh holder',mesh.is_watertight,len(mesh.faces),len(mesh.split(only_watertight=False)),mesh.bounds,flush=True)
mesh.apply_translation([0,0,0.2])
mesh.export(O/'holder.stl')
m=trimesh.load_mesh(O/'holder.stl');print('final holder',m.is_watertight,len(m.faces),len(m.split(only_watertight=False)),m.bounds,flush=True)
# Lid U-channel: flat face goes on print bed, walls point upward.
# Design intentionally avoids inward bottom hooks; shallow detents on the
# interior skirt engage open-top holder notches near the insertion end.
lid=block(-23.30,23.30,-126.8,127.6,39.20,41.35)
for s in [-1,1]:
 x0,x1=(21.35,23.30) if s==1 else (-23.30,-21.35)
 lid=lid.union(block(x0,x1,-126.0,125.9,33.80,41.35))
# stop wall at trailing (positive Y) end; lid slides on from negative Y.
lid=lid.union(block(-23.30,23.30,126.4,127.6,35.0,41.35))
# accessible tab, still flat against the build plate during print
lid=lid.union(block(-8.0,8.0,-129.15,-126.0,39.20,41.35))
# Low, tapering catches: small compliant bevels, supported in the upside-down
# print orientation.  At fully closed position they align with holder pockets.
# These are printed on the inside of each skirt and intentionally optional
# to shave with a file if tolerance is tight.
for s in [-1,1]:
 # profile in XZ: x decreases progressively as the cover prints upside-down
 profile=[(21.35,37.75),(21.35,35.65),(20.55,35.65),(20.55,36.35)]
 if s==-1: profile=[(-x,z) for x,z in reversed(profile)]
 nib=cq.Workplane('XZ').polyline(profile).close().extrude(2.65,both=True).translate((0,-118.3,0))
 lid=lid.union(nib)
lid=lid.combine().clean()
cq.exporters.export(lid.val(),str(O/'sliding-lid-assembled.stl'),tolerance=.035,angularTolerance=.12)
ml=trimesh.load_mesh(O/'sliding-lid-assembled.stl');print('lid',ml.is_watertight,len(ml.split(only_watertight=False)),ml.bounds,flush=True)

# Convert assembled lid into the expected print orientation.
print_lid = trimesh.load_mesh(O / 'sliding-lid-assembled.stl').copy()
R = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
print_lid.apply_transform(R)
print_lid.apply_translation([0, 0, -print_lid.bounds[0, 2]])
print_lid.export(O / 'sliding-lid-print-face-down.stl')
print('Finished three output STL files in', O)
