from PyMpc import App, MpcMesh, IO
from .selectionSet import selectionSet
import numpy as np

class mesh:
    """
    This is a mixin class to work with the PyMpc.MpcMesh object
    This class function as a wrapper
    """
    
    def _check_mesh_object(self):
        """
        Check if the mesh object is initialized.
        """
        if self.mesh_object is None:
            raise ValueError("ERROR: The mesh object is not initialized.")
    
    def _get_mesh_geometries_ids(self):
        """
        Get the geometry IDs of the mesh object.
        """
        self._check_mesh_object()
        
        geometry_ids = set()
        for geometry_id in self.mesh_object.meshedGeometries:
            geometry_ids.add(geometry_id)
        
        return geometry_ids
    
    def _solid_extraction(self, geometry_id):
        """
        Retrieves solid information for a given geometry ID from a mesh object.
        
        Args:
            mesh_object (PyMpc.MpcMesh): The mesh object containing meshed geometries.
            geometry_id (int): The ID of the geometry to retrieve solid information for.  
        """
        self._check_mesh_object()
        
        mesh_subset=self.mesh_object.meshedGeometries[geometry_id] #PyMpc.MpcMeshOfGeometry
        solids_collection=mesh_subset.solids #PyMpc.MpcMeshDomainCollection
        
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
        
        return results
                
    def _face_extraction(self, geometry_id):
        """
        Retrieves face information for a given geometry ID from a mesh object.
        
        Args:
            mesh_object (PyMpc.MpcMesh): The mesh object containing meshed geometries.
            geometry_id (int): The ID of the geometry to retrieve face information for.  
        """
        self._check_mesh_object()
        
        mesh_subset=self.mesh_object.meshedGeometries[geometry_id] #PyMpc.MpcMeshOfGeometry
        faces_collection=mesh_subset.faces #PyMpc.MpcMeshDomainCollection
        
        face_id_set = set()
        nodes_id_set = set()
        
        if faces_collection.__len__() != 0:
            
            for face in faces_collection:
                face_element=face.elements
                for face_element in face_element:
                    face_id_set.add(face_element.id)
                    for node in face_element.nodes:
                        nodes_id_set.add(node.id)
                
        results = {
            'face_id': face_id_set,
            'nodes_id': nodes_id_set
        }
        
        return results
    
    def _edge_extraction(self, geometry_id):
        """
        Retrieves edge information for a given geometry ID from a mesh object.
        
        Args:
            mesh_object (PyMpc.MpcMesh): The mesh object containing meshed geometries.
            geometry_id (int): The ID of the geometry to retrieve edge information for.  
        """
        self._check_mesh_object()
        
        mesh_subset=self.mesh_object.meshedGeometries[geometry_id] #PyMpc.MpcMeshOfGeometry
        edges_collection=mesh_subset.edges #PyMpc.MpcMeshDomainCollection
        
        edge_id_set = set()
        nodes_id_set = set()
        
        if edges_collection.__len__() != 0:
            
            for edge in edges_collection:
                edge_element=edge.elements
                for edge_element in edge_element:
                    edge_id_set.add(edge_element.id)
                    for node in edge_element.nodes:
                        nodes_id_set.add(node.id)
                
        results = {
            'edge_id': edge_id_set,
            'nodes_id': nodes_id_set
        }
        
        return results
    
    def _node_extraction(self, geometry_id):
        """
        Retrieves node information for a given geometry ID from a mesh object.
        
        Args:
            mesh_object (PyMpc.MpcMesh): The mesh object containing meshed geometries.
            geometry_id (int): The ID of the geometry to retrieve node information for.  
        """
        self._check_mesh_object()
        
        mesh_subset=self.mesh_object.meshedGeometries[geometry_id] #PyMpc.MpcMeshOfGeometry
        vertices=mesh_subset.vertices #PyMpc.MpcElementConnectivityCollection
        
        node_id_set = set()
        
        if vertices.__len__() != 0:
            for vertex in vertices:
                node_id_set.add(vertex.id)
                
        results = {
            'node_id': node_id_set
        }
        
        return results

    @staticmethod
    def _get_STKO_ids_per_geometry_id(geometry_id, selection_set_results):
        """Helper function to get the STKO IDs per geometry ID.

        Args:
            geometry_id (_type_): _description_
            selection_set_results (dict): _description_

        Returns:
            set: The different STKO IDs for the geometry ID.
        """
        stko_vertices=selection_set_results['stko_geometries'][geometry_id]['vertices'] #Set of all the vertuces in the selection set
        stko_edges=selection_set_results['stko_geometries'][geometry_id]['edges'] #Set of all the vertuces in the selection set
        stko_faces=selection_set_results['stko_geometries'][geometry_id]['faces'] #Set of all the vertuces in the selection set
        stko_solids=selection_set_results['stko_geometries'][geometry_id]['solids'] #Set of all the vertuces in the selection set

        return stko_vertices, stko_edges, stko_faces, stko_solids
    
    def extract_mesh_data_selectionSet(self, selection_set_id):
        # mesh geometry results for the selection set items, it return the selected elements and the components that made up the selection
        # TO DO: For faces and solids there is an issue with the components thata make up the element, the edges and nodes are not being extracted correctly
        
        mesh_nodes=set()
        mesh_edges=set()
        mesh_faces=set()
        mesh_solids=set()
        
        # Get the selection set items
        selection_set_results=self._get_selection_set_items(selection_set_id=selection_set_id) #this returns a dictionary with the geometries ids and the stko geometries
        
        geometries_ids=selection_set_results['geometries_ids']
        
        if geometries_ids: #if there are geometries in the selection set
            for geometry_id in geometries_ids:
                mesh_geometry=self.preprocessor.mesh.meshedGeometries[geometry_id]
                
                mesh_geometry_vertices=mesh_geometry.vertices #PyMpc.MpcElementConnectivityCollection
                mesh_geometry_edges=mesh_geometry.edges #PyMpc.MpcMeshDomainCollection
                mesh_geometry_faces=mesh_geometry.faces #PyMpc.MpcMeshDomainCollection
                mesh_geometry_solids=mesh_geometry.solids #PyMpc.MpcMeshDomainCollection
                
                stko_vertices, stko_edges, stko_faces, stko_solids=self._get_STKO_ids_per_geometry_id(geometry_id, selection_set_results)
                
                if stko_vertices: #Check if the set is not empty
                    for geometry_vertices in stko_vertices:
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
                                        
        results = {
            'nodes': mesh_nodes,
            'edges': mesh_edges,
            'faces': mesh_faces,
            'solids': mesh_solids
        }
                
        return results
    
    def extract_mesh_elements_selectionSet(self, selection_set_id):
        # mesh geometry results for the selection set items, it only consider the selected elements, not the components that made up the selection
        # ie dor a face, the face is made up of edges, and the edges of nodes; tthis function returns only the selected faces.
        
        mesh_nodes=set()
        mesh_edges=set()
        mesh_faces=set()
        mesh_solids=set()
        
        # Get the selection set items
        selection_set_results=self._get_selection_set_items(selection_set_id=selection_set_id) #this returns a dictionary with the geometries ids and the stko geometries
        
        geometries_ids=selection_set_results['geometries_ids']
        
        if geometries_ids: #if there are geometries in the selection set
            for geometry_id in geometries_ids:
                mesh_geometry=self.preprocessor.mesh.meshedGeometries[geometry_id]
                
                mesh_geometry_vertices=mesh_geometry.vertices #PyMpc.MpcElementConnectivityCollection
                mesh_geometry_edges=mesh_geometry.edges #PyMpc.MpcMeshDomainCollection
                mesh_geometry_faces=mesh_geometry.faces #PyMpc.MpcMeshDomainCollection
                mesh_geometry_solids=mesh_geometry.solids #PyMpc.MpcMeshDomainCollection
                
                stko_vertices, stko_edges, stko_faces, stko_solids=self._get_STKO_ids_per_geometry_id(geometry_id, selection_set_results)
                
                if stko_vertices: #Check if the set is not empty
                    for geometry_vertices in stko_vertices:
                        node_id=mesh_geometry_vertices.__getitem__(geometry_vertices)
                        mesh_nodes.add(node_id.id)
                        
                if stko_edges: #Check if the set is not empty
                    stko_edges_list=list(stko_edges)
                    for geometry_edges in stko_edges_list:
                        mesh_domain=mesh_geometry_edges.__getitem__(geometry_edges)
                        for edge in mesh_domain.elements:
                            mesh_edges.add(edge.id)


                if stko_faces:  # Check if the set is not empty
                    stko_faces_list = list(stko_faces)
                    for geometry_faces in stko_faces_list:
                        mesh_domain = mesh_geometry_faces.__getitem__(geometry_faces)  # Get the face domain
                        for face in mesh_domain.elements:  # Iterate over elements in the face
                            mesh_faces.add(face.id)
                                    
                if stko_solids:  # Check if the set is not empty
                    stko_solids_list = list(stko_solids)
                    for geometry_solids in stko_solids_list:
                        mesh_domain = mesh_geometry_solids.__getitem__(geometry_solids)  # Get the solid domain
                        for solid in mesh_domain.elements:  # Iterate over elements in the solid
                            mesh_solids.add(solid.id)  # Add the solid ID to the set

                                        
        results = {
            'nodes': mesh_nodes,
            'edges': mesh_edges,
            'faces': mesh_faces,
            'solids': mesh_solids
        }
                
        return results