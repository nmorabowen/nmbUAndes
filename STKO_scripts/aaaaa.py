from PyMpc import *
from STKO_APE import modelAPE

#model=modelAPE(verbose=True)
selection_set_id=3
#model.extract_mesh_data(selection_set_id=selection_set_id)


doc = App.caeDocument()
mesh = doc.mesh

print(mesh)
print(dir(mesh))

print('------------')

mesh_geo=mesh.meshedGeometries

mesh_node=mesh.nodes

mesh_subset=mesh_geo[422]
nodes=mesh_subset.vertices
edges=mesh_subset.edges
faces=mesh_subset.faces

print(edges)

edge=edges[1]
face=faces[1]

print(edge)
print(dir(edge))
print(edge.elements)

print(len(edge.elements))

a=edge.elements[1]

print(a)
print(a.nodes)
print(dir(a))

print(face)
print(dir(face))

print(len(face.elements))

b=face.elements[5]

print(b)
print(b.area())
print(b.id)

print(len(nodes))
print(nodes[0])



