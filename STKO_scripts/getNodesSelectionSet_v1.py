from PyMpc import *

# Access the current CAE document
doc = App.caeDocument()
if doc is None:
    raise Exception('No active CAE document found.')

# Specify the selection set ID
selection_set_id = 3  # Replace with your selection set ID

# Retrieve the selection set
if selection_set_id not in doc.selectionSets:
    raise Exception(f'Selection set with ID {selection_set_id} not found.')
selection_set = doc.selectionSets[selection_set_id]

# Initialize a list to store node IDs
node_ids = []

# Iterate over geometries in the selection set
for geom_id, selection_item in selection_set.geometries.items():
    print(geom_id)
    # Access the meshed geometry
    if geom_id not in doc.mesh.meshedGeometries:
        continue
    meshed_geom = doc.mesh.meshedGeometries[geom_id]
    print(meshed_geom)

    # Retrieve nodes from selected vertices
    for vertex_index in selection_item.vertices:
        print(vertex_index)
        if vertex_index in meshed_geom.vertices:
            node = meshed_geom.vertices[vertex_index]
            print(node)
            node_ids.append(node.id)

    # Retrieve nodes from selected edges
    for edge_index in selection_item.edges:
        if edge_index in meshed_geom.edges:
            edge = meshed_geom.edges[edge_index]
            for node in edge.nodes:
                node_ids.append(node.id)

    # Retrieve nodes from selected faces
    for face_index in selection_item.faces:
        if face_index in meshed_geom.faces:
            face = meshed_geom.faces[face_index]
            for node in face.nodes:
                node_ids.append(node.id)

    # Retrieve nodes from selected solids
    for solid_index in selection_item.solids:
        if solid_index in meshed_geom.solids:
            solid = meshed_geom.solids[solid_index]
            for node in solid.nodes:
                node_ids.append(node.id)

# Remove duplicate node IDs
node_ids = list(set(node_ids))

# Output the list of node IDs
print('Extracted Node IDs:', node_ids)
