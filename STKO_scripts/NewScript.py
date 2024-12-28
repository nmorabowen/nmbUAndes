import PyMpc.App
import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *

doc = PyMpc.App.caeDocument()
selection_set = doc.selectionSets[2]
geo_geo=selection_set.geometries
geo = selection_set.geometries.items()

vert=geo[0][1].vertices

mesh_of_geom = doc.mesh.meshedGeometries[geo[0][0]]

print(mesh_of_geom)
print(type(mesh_of_geom))
print(dir(mesh_of_geom))

print(vert)
print(dir(vert))

print(mesh_of_geom.vertices[vert])