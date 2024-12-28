from PyMpc import App, IO

class STKOMeshExtractor:
    """
    A mixin class to provide functionality for extracting geometry and mesh data 
    (e.g., node IDs) from a selection set in STKO.
    """
    def run_extraction(self, doc, selection_set_id):
        """
        Execute the extraction of geometry IDs from the selection set and map them to 
        OpenSees node IDs in the meshed geometries.

        :param doc:              The STKO CAE document (App.caeDocument()).
        :param selection_set_id: The ID of the selection set to extract from.
        """
        # These dictionaries will store final results, keyed by geometry_id
        self.node_ids_by_geom = {}
        self.edge_nodes_by_geom = {}
        self.face_nodes_by_geom = {}
        self.solid_nodes_by_geom = {}

        # Check if the selection set exists
        if selection_set_id not in doc.selectionSets:
            raise ValueError(f"ERROR: No selection set found at ID = {selection_set_id}")

        selection_set = doc.selectionSets[selection_set_id]
        print(f"[STKOMeshExtractor] Processing selection set ID = {selection_set_id}, Name = {selection_set.name}")

        stko_vertices=set()
        stko_edges=set()
        stko_faces=set()
        stko_solids=set()
        
        for geometry_id, geometry_subset in selection_set.geometries.items():
            print(f"\nProcessing Geometry ID: {geometry_id}")

            # Extract STKO IDs
            
            stko_vertices = list(geometry_subset.vertices)
            stko_edges = list(geometry_subset.edges)
            stko_faces = list(geometry_subset.faces)
            stko_solids = list(geometry_subset.solids)

            # Check if the geometry is meshed
            if geometry_id not in doc.mesh.meshedGeometries:
                print(f"WARNING: Geometry ID {geometry_id} not found in meshedGeometries. Skipping.")
                continue

            # Access the meshed geometry
            mesh_of_geometry = doc.mesh.meshedGeometries[geometry_id]
            mesh_vertices = mesh_of_geometry.vertices
            max_index = len(mesh_vertices) - 1

            # Map each geometry ID -> node ID
            self.node_ids_by_geom[geometry_id] = [
                mesh_vertices[stko_id].id for stko_id in stko_vertices if 0 <= stko_id <= max_index
            ]
            self.edge_nodes_by_geom[geometry_id] = [
                mesh_vertices[stko_id].id for stko_id in stko_edges if 0 <= stko_id <= max_index
            ]
            self.face_nodes_by_geom[geometry_id] = [
                mesh_vertices[stko_id].id for stko_id in stko_faces if 0 <= stko_id <= max_index
            ]
            self.solid_nodes_by_geom[geometry_id] = [
                mesh_vertices[stko_id].id for stko_id in stko_solids if 0 <= stko_id <= max_index
            ]

        self._print_summary()

    def _print_summary(self):
        """
        Print a summary of all geometry IDs mapped to node IDs.
        """
        print("\n================== Final Results ==================")
        for geometry_id in sorted(self.node_ids_by_geom.keys()):
            print(f"Geometry ID = {geometry_id}")
            print("  - Vertex-based node IDs:", self.node_ids_by_geom[geometry_id])
            print("  - Edge-based node IDs:  ", self.edge_nodes_by_geom[geometry_id])
            print("  - Face-based node IDs:  ", self.face_nodes_by_geom[geometry_id])
            print("  - Solid-based node IDs: ", self.solid_nodes_by_geom[geometry_id])
        print("\n[STKOMeshExtractor] Extraction completed.\n")
