from PyMpc import *
import numpy as np

preprocessor=App.caeDocument()

selection_set_id=9

selection_set = preprocessor.selectionSets[selection_set_id]
print(f"Processing selection set ID = {selection_set_id}, Name = {selection_set.name}")

selection_set_geometries=selection_set.geometries

geometries_ids = set()  # This will contain all the geometries ids in the selection set

# This will contain all the vertices, edges, faces, and solids ids in the selection set. This correspond to the geometry, not the mesh
stko_geometries = {}  # Dictionary to hold geometry id as key and another dictionary as value

for ids, geometries_subset in selection_set_geometries.items():
	# This gets all the geometries ids in the selection set
	geometries_ids.add(ids)
	# geometries_subset is a PyMpc.MpcSelectionSetItem object
	
	stko_geometries[ids] = {
		'vertices': set(),
		'edges': set(),
		'faces': set(),
		'solids': set()
	}
	
	for vertex in geometries_subset.vertices:
		stko_geometries[ids]['vertices'].add(vertex)
	for edge in geometries_subset.edges:
		stko_geometries[ids]['edges'].add(edge)
	for face in geometries_subset.faces:
		stko_geometries[ids]['faces'].add(face)
	for solid in geometries_subset.solids:
		stko_geometries[ids]['solids'].add(solid)

results = {
	'geometries_ids': geometries_ids,
	'stko_geometries': stko_geometries
}

print(results['stko_geometries'])
