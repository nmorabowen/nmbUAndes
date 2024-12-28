from PyMpc import *
import numpy as np

preprocessor=App.caeDocument()
mesh_object=preprocessor.mesh
mesh_geometries=mesh_object.meshedGeometries

print(mesh_object)
print(dir(mesh_object))

#This print the nodes tags
for item in mesh_object.nodes:
	print(item)

#This print the nodes objects
for item in mesh_object.nodes.items():
	print(item)

mesh_id=9
mesh_object_id=mesh_geometries[mesh_id]

print(mesh_object_id)

for vertex in mesh_object_id.vertices:
    print(vertex)

for edge in mesh_object_id.edges:
	for vector in edge.elements:
		print(vector)
	print(edge)

mesh_object_id_edges=mesh_object_id.edges
print(mesh_object_id_edges)
print(dir(mesh_object_id_edges))


edge=mesh_object_id.edges[0]
print(edge)
print(dir(edge))
print(edge.elements)
print(dir(edge.elements))

print('-------------------------')

print(dir(mesh_object_id.solids))
print(mesh_object_id.solids.__len__())

print(mesh_object_id.solids.__iter__())

print(mesh_object_id.solids.__dict__)

print

solid=mesh_object_id.solids[0]
print(solid)

for j,i in enumerate(solid.elements):
	print(i.id)
	print(i.nodes)
	print(f'elemento no {j}')
	x=i.boundaryFaces
	for k in x:
		print(k)



print(len(solid.elements))

print(dir(x))

print(i.boundaryEdges.__len__())

print(mesh_object_id.solids.__getitem__(0))


print(mesh_object_id.solids.__len__())


solids_collection=mesh_object_id.solids
print(solids_collection)

solid_id_set = set()
nodes_id_set = set()

for solids in solids_collection:
	solid_elements=solids.elements
	for element in solid_elements:
		print(element.id)
		for node in element.nodes:
			print(node)
	


solid_id_set = set()
nodes_id_set = set()

if solids_collection.__len__() != 0:
	
	for solid in solids_collection:
		solid_element=solid.elements
		for solid_element in solid_element:
			solid_id_set.add(solid_element.id)
			for node in solid_element.nodes:
				nodes_id_set.add(node.id)
		
results = {
	'solid_id': solid_id_set,
	'nodes_id': nodes_id_set
}

print(results)


