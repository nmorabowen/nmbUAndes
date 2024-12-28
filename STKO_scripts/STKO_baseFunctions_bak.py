from PyMpc import *

def clearCharts():
    # Function to delete all charts and chart data
    # Access the post-processor document
    doc = App.postDocument()
    
    # Clear all charts, chart data, and plot groups
    doc.clearCharts()
    doc.clearChartData()
    
    # Commit changes and mark the document as dirty
    doc.commitChanges()
    doc.dirty = True
    
    # Clear the terminal to indicate that the process is complete
    App.clearTerminal()
    print("All elements (charts, chart data, plot groups) have been cleared.")
    
    # Log a custom message
    IO.write_clog('LARGA VIDA AL LADRUÑO!!!')

class STKOMeshExtractor:
    """
    A helper class to extract geometry and mesh data (node IDs, etc.) from a selection set in STKO.
    
    In short, if STKO is “skipping” geometry, it usually means that geometry is not contributing any
    elements to the final mesh—either by design (mesh settings or merges) or due to degeneracy 
    (zero-size or overlaps). Once you fix or intentionally exclude those geometry items, the 
    “index out of range” warnings should disappear, and your script will have a consistent 
    mapping between STKO geometry IDs and the meshed nodes/elements.
    """

    def __init__(self, doc, selection_set_id):
        """
        :param doc:              The STKO CAE document (App.caeDocument()).
        :param selection_set_id: The ID of the selection set to extract from.
        """
        self.doc = doc
        self.selection_set_id = selection_set_id

        # These dictionaries will store final results, keyed by geometry_id
        self.node_ids_by_geom   = {}
        self.edge_nodes_by_geom = {}
        self.face_nodes_by_geom = {}
        self.solid_nodes_by_geom= {}

    def run_extraction(self):
        """
        Execute the extraction of geometry IDs from the selection set and map them to 
        OpenSees node IDs in the meshed geometries.
        """
        # 1) Check if the selection set exists
        if self.selection_set_id not in self.doc.selectionSets:
            msg = f"ERROR: No selection set found at ID = {self.selection_set_id}"
            print(msg)
            raise ValueError(msg)

        selection_set = self.doc.selectionSets[self.selection_set_id]
        print(f"[STKOMeshExtractor] Processing selection set ID = {self.selection_set_id}, Name = {selection_set.name}")

        # 2) Loop over each geometry in the selection set
        for geometry_id, geometry_subset in selection_set.geometries.items():
            print("------------------------------------------------------------")
            print(f"Geometry ID: {geometry_id}")
            print(f"Geometry Subset: {geometry_subset}")

            # Gather STKO geometry IDs
            stko_vertices = list(geometry_subset.vertices)
            stko_edges    = list(geometry_subset.edges)
            stko_faces    = list(geometry_subset.faces)
            stko_solids   = list(geometry_subset.solids)

            print("\nSTKO vertex IDs:", stko_vertices)
            print("STKO edge IDs:", stko_edges)
            print("STKO face IDs:", stko_faces)
            print("STKO solid IDs:", stko_solids)

            # 3) Check if this geometry is meshed
            if geometry_id not in self.doc.mesh.meshedGeometries:
                print(f"WARNING: geometry_id {geometry_id} not found in meshedGeometries. Skipping.")
                continue

            # 4) Access the meshed geometry (and its node collection)
            mesh_of_geometry = self.doc.mesh.meshedGeometries[geometry_id]
            mesh_vertices = mesh_of_geometry.vertices  # MpcElementConnectivityCollection
            max_index = len(mesh_vertices) - 1

            # 5) Safely map each geometry ID -> node ID
            # Vertex-based
            opensees_node_ids = []
            for stko_id in stko_vertices:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Vertex stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                opensees_node_ids.append(mesh_vertices[stko_id].id)
            self.node_ids_by_geom[geometry_id] = opensees_node_ids

            # Edge-based
            edge_node_ids = []
            for stko_id in stko_edges:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Edge stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                edge_node_ids.append(mesh_vertices[stko_id].id)
            self.edge_nodes_by_geom[geometry_id] = edge_node_ids

            # Face-based
            face_node_ids = []
            for stko_id in stko_faces:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Face stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                face_node_ids.append(mesh_vertices[stko_id].id)
            self.face_nodes_by_geom[geometry_id] = face_node_ids

            # Solid-based
            solid_node_ids = []
            for stko_id in stko_solids:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Solid stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                solid_node_ids.append(mesh_vertices[stko_id].id)
            self.solid_nodes_by_geom[geometry_id] = solid_node_ids

            print("\n--- Mapping from geometry to meshed nodes ---")
            print(f"Opensees node IDs: {opensees_node_ids}")
            print(f"Opensees Edge node IDs:   {edge_node_ids}")
            print(f"Opensees Face node IDs:   {face_node_ids}")
            print(f"Opensees Solid node IDs:  {solid_node_ids}")
            print("------------------------------------------------------------\n")

        # 6) Optionally print a summary of all gathered data
        self._print_summary()

    def _print_summary(self):
        """
        Print a summary of all geometry IDs mapped to node IDs.
        Called at the end of run_extraction().
        """
        print("\n================== Final Results ==================")
        all_geom_ids = sorted(self.node_ids_by_geom.keys())
        for geometry_id in all_geom_ids:
            print(f"\nGeometry ID = {geometry_id}")
            print("  - Vertex-based node IDs:", self.node_ids_by_geom[geometry_id])
            print("  - Edge-based node IDs:  ", self.edge_nodes_by_geom[geometry_id])
            print("  - Face-based node IDs:  ", self.face_nodes_by_geom[geometry_id])
            print("  - Solid-based node IDs: ", self.solid_nodes_by_geom[geometry_id])
        print("\n[STKOMeshExtractor] Extraction completed.\n")
        
        
class STKOMeshExtractor:
    """
    A helper class to extract geometry and mesh data (node IDs, etc.) from a selection set in STKO.
    
    In short, if STKO is “skipping” geometry, it usually means that geometry is not contributing any
    elements to the final mesh—either by design (mesh settings or merges) or due to degeneracy 
    (zero-size or overlaps). Once you fix or intentionally exclude those geometry items, the 
    “index out of range” warnings should disappear, and your script will have a consistent 
    mapping between STKO geometry IDs and the meshed nodes/elements.
    """

    def __init__(self, doc, selection_set_id):
        """
        :param doc:              The STKO CAE document (App.caeDocument()).
        :param selection_set_id: The ID of the selection set to extract from.
        """
        self.doc = doc
        self.selection_set_id = selection_set_id

        # These dictionaries will store final results, keyed by geometry_id
        self.node_ids_by_geom   = {}
        self.edge_nodes_by_geom = {}
        self.face_nodes_by_geom = {}
        self.solid_nodes_by_geom= {}

    def run_extraction(self):
        """
        Execute the extraction of geometry IDs from the selection set and map them to 
        OpenSees node IDs in the meshed geometries.
        """
        # 1) Check if the selection set exists
        if self.selection_set_id not in self.doc.selectionSets:
            msg = f"ERROR: No selection set found at ID = {self.selection_set_id}"
            print(msg)
            raise ValueError(msg)

        selection_set = self.doc.selectionSets[self.selection_set_id]
        print(f"[STKOMeshExtractor] Processing selection set ID = {self.selection_set_id}, Name = {selection_set.name}")

        # 2) Loop over each geometry in the selection set
        for geometry_id, geometry_subset in selection_set.geometries.items():
            print("------------------------------------------------------------")
            print(f"Geometry ID: {geometry_id}")
            print(f"Geometry Subset: {geometry_subset}")

            # Gather STKO geometry IDs
            stko_vertices = list(geometry_subset.vertices)
            stko_edges    = list(geometry_subset.edges)
            stko_faces    = list(geometry_subset.faces)
            stko_solids   = list(geometry_subset.solids)

            print("\nSTKO vertex IDs:", stko_vertices)
            print("STKO edge IDs:", stko_edges)
            print("STKO face IDs:", stko_faces)
            print("STKO solid IDs:", stko_solids)

            # 3) Check if this geometry is meshed
            if geometry_id not in self.doc.mesh.meshedGeometries:
                print(f"WARNING: geometry_id {geometry_id} not found in meshedGeometries. Skipping.")
                continue

            # 4) Access the meshed geometry (and its node collection)
            mesh_of_geometry = self.doc.mesh.meshedGeometries[geometry_id]
            mesh_vertices = mesh_of_geometry.vertices  # MpcElementConnectivityCollection
            max_index = len(mesh_vertices) - 1

            # 5) Safely map each geometry ID -> node ID
            # Vertex-based
            opensees_node_ids = []
            for stko_id in stko_vertices:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Vertex stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                opensees_node_ids.append(mesh_vertices[stko_id].id)
            self.node_ids_by_geom[geometry_id] = opensees_node_ids

            # Edge-based
            edge_node_ids = []
            for stko_id in stko_edges:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Edge stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                edge_node_ids.append(mesh_vertices[stko_id].id)
            self.edge_nodes_by_geom[geometry_id] = edge_node_ids

            # Face-based
            face_node_ids = []
            for stko_id in stko_faces:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Face stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                face_node_ids.append(mesh_vertices[stko_id].id)
            self.face_nodes_by_geom[geometry_id] = face_node_ids

            # Solid-based
            solid_node_ids = []
            for stko_id in stko_solids:
                if not (0 <= stko_id <= max_index):
                    print(f"WARNING: Solid stko_id {stko_id} out of range (0..{max_index}). Skipping.")
                    continue
                solid_node_ids.append(mesh_vertices[stko_id].id)
            self.solid_nodes_by_geom[geometry_id] = solid_node_ids

            print("\n--- Mapping from geometry to meshed nodes ---")
            print(f"Opensees node IDs: {opensees_node_ids}")
            print(f"Opensees Edge node IDs:   {edge_node_ids}")
            print(f"Opensees Face node IDs:   {face_node_ids}")
            print(f"Opensees Solid node IDs:  {solid_node_ids}")
            print("------------------------------------------------------------\n")

        # 6) Optionally print a summary of all gathered data
        self._print_summary()

    def _print_summary(self):
        """
        Print a summary of all geometry IDs mapped to node IDs.
        Called at the end of run_extraction().
        """
        print("\n================== Final Results ==================")
        all_geom_ids = sorted(self.node_ids_by_geom.keys())
        for geometry_id in all_geom_ids:
            print(f"\nGeometry ID = {geometry_id}")
            print("  - Vertex-based node IDs:", self.node_ids_by_geom[geometry_id])
            print("  - Edge-based node IDs:  ", self.edge_nodes_by_geom[geometry_id])
            print("  - Face-based node IDs:  ", self.face_nodes_by_geom[geometry_id])
            print("  - Solid-based node IDs: ", self.solid_nodes_by_geom[geometry_id])
        print("\n[STKOMeshExtractor] Extraction completed.\n")