from PyMpc import *
from STKO_APE import modelAPE
from STKO_APE import write_in_terminal_blue, write_in_terminal_red, write_in_terminal

def get_mesh_entities_from_selection_set(selection_set_id, geometry_id, file, preprocessor):
    """
    Retrieves mesh entities (nodes, edges, faces, solids) associated with a given selection set.

    Args:
        selection_set_id (int): The ID of the selection set.
        geometry_id (int): The ID of the geometry to process.
        file (modelAPE): An instance of the modelAPE class.
        preprocessor (App.caeDocument): An instance of the STKO preprocessor.

    Returns:
        dict: A dictionary containing sets of mesh entity IDs (nodes, edges, faces, solids).
    """

    selection_set_results = file._get_selection_set_items(selection_set_id=selection_set_id)
    mesh_geometry = preprocessor.mesh.meshedGeometries[geometry_id]

    mesh_entities = {
        'nodes': set(),
        'edges': set(),
        'faces': set(),
        'solids': set()
    }

    stko_geometries = selection_set_results['stko_geometries'].get(geometry_id, {})

    def add_nodes_from_elements(elements):
        """Helper function to add nodes from a collection of elements."""
        for element in elements:
            for node in element.nodes:
                mesh_entities['nodes'].add(node.id)

    if 'vertices' in stko_geometries:
        for vertex_id in stko_geometries['vertices']:
            mesh_entities['nodes'].add(mesh_geometry.vertices[vertex_id].id)

    if 'edges' in stko_geometries:
        for edge_id in stko_geometries['edges']:
            edge = mesh_geometry.edges[edge_id]
            mesh_entities['edges'].update(element.id for element in edge.elements)
            add_nodes_from_elements(edge.elements)

    if 'faces' in stko_geometries:
        for face_id in stko_geometries['faces']:
            face = mesh_geometry.faces[face_id]
            mesh_entities['faces'].update(element.id for element in face.elements)
            add_nodes_from_elements(face.elements)
            mesh_entities['edges'].update(edge.id for edge in face.boundaryEdges)

            
    if 'solids' in stko_geometries:
        for solid_id in stko_geometries['solids']:
            solid = mesh_geometry.solids[solid_id]
            mesh_entities['solids'].update(element.id for element in solid.elements)
            add_nodes_from_elements(solid.elements)
            for face in solid.boundaryFaces:
                mesh_entities['faces'].add(face.id)
                mesh_entities['edges'].update(edge.id for edge in face.boundaryEdges)
    
    

    return mesh_entities

# Example Usage:
file = modelAPE()
selection_set_id = 9
geometry_id = 9
preprocessor = App.caeDocument()

mesh_entities = get_mesh_entities_from_selection_set(selection_set_id, geometry_id, file, preprocessor)

print('The nodes are:')
print(mesh_entities['nodes'])

print('The edges are:')
print(mesh_entities['edges'])

print('The faces are:')
print(mesh_entities['faces'])

print('The solids are:')
print(mesh_entities['solids'])