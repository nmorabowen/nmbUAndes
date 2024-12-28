from PyMpc import *
from STKO_APE import modelAPE
from STKO_APE import write_in_terminal_blue, write_in_terminal_red, write_in_terminal

def _get_STKO_ids_per_geometry_id(geometry_id, selection_set_results):
		stko_vertices=selection_set_results['stko_geometries'][geometry_id]['vertices'] #Set of all the vertuces in the selection set
		stko_edges=selection_set_results['stko_geometries'][geometry_id]['edges'] #Set of all the vertuces in the selection set
		stko_faces=selection_set_results['stko_geometries'][geometry_id]['faces'] #Set of all the vertuces in the selection set
		stko_solids=selection_set_results['stko_geometries'][geometry_id]['solids'] #Set of all the vertuces in the selection set
		return stko_vertices, stko_edges, stko_faces, stko_solids

file=modelAPE()

selection_set_id=3

selection_set_results=file._get_selection_set_items(selection_set_id=selection_set_id)
print(selection_set_results)

print('---------------------------------------------------------------------')

preprocessor=App.caeDocument()

#mesh geometry results
mesh_nodes=set()
mesh_edges=set()
mesh_faces=set()
mesh_solids=set()

geometries_ids=selection_set_results['geometries_ids'] #set of all the geometries ids in the selection set

if geometries_ids:
	for geometry_id in geometries_ids:
		
		mesh_geometry=preprocessor.mesh.meshedGeometries[geometry_id]
		
		mesh_geometry_vertices=mesh_geometry.vertices
		mesh_geometry_edges=mesh_geometry.edges
		mesh_geometry_faces=mesh_geometry.faces
		mesh_geometry_solids=mesh_geometry.solids
		
		stko_vertices, stko_edges, stko_faces, stko_solids=_get_STKO_ids_per_geometry_id(geometry_id,selection_set_results)



		if stko_vertices: #Check if the set is not empty
			stko_vertices_list=list(stko_vertices)
			for geometry_vertices in stko_vertices_list:
				node_id=mesh_geometry_vertices.__getitem__(geometry_vertices)
				mesh_nodes.add(node_id.id)

		if stko_edges: #Check if the set is not empty
			stko_edges_list=list(stko_edges)
			for geometry_edges in stko_edges_list:
				mesh_domain=mesh_geometry_edges.__getitem__(geometry_edges)
				for edge in mesh_domain.elements:
					nodes=edge.nodes
					mesh_edges.add(edge.id)
					for node in nodes:
						mesh_nodes.add(node.id)


		if stko_faces:  # Check if the set is not empty
			stko_faces_list = list(stko_faces)
			for geometry_faces in stko_faces_list:
				mesh_domain = mesh_geometry_faces.__getitem__(geometry_faces)  # Get the face domain
				for face in mesh_domain.elements:  # Iterate over elements in the face
					mesh_faces.add(face.id)
					print(dir(face))
					for edge in face.boundaryEdges:  # Access edges in the face
						mesh_edges.add(edge.id)  # Add edge ID to the set
						for node in edge.nodes:  # Access nodes in the edge
							mesh_nodes.add(node.id)  # Add node ID to the set

		if stko_solids:  # Check if the set is not empty
			stko_solids_list = list(stko_solids)
			for geometry_solids in stko_solids_list:
				mesh_domain = mesh_geometry_solids.__getitem__(geometry_solids)  # Get the solid domain
				for solid in mesh_domain.elements:  # Iterate over elements in the solid
					mesh_solids.add(solid.id)  # Add the solid ID to the set
					for face in solid.boundaryFaces:  # Access boundary faces in the solid
						mesh_faces.add(face.id)  # Add face ID to the set
						for edge in face.boundaryEdges:  # Access boundary edges in the face
							mesh_edges.add(edge.id)  # Add edge ID to the set
							for node in edge.nodes:  # Access nodes in the edge
								mesh_nodes.add(node.id)  # Add node ID to the set

print('The nodes are:')
print(mesh_nodes)

print('The edges are:')
print(mesh_edges)

print('The faces are:')
print(mesh_faces)

print('The solids are:')
print(mesh_solids)