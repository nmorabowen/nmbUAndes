#Import the PyMpc package to interact with STKO
from PyMpc import *

#Call the open .scd document
doc = App.caeDocument()

#Call the mesh
mesh = doc.mesh


"""Function to find the nearest node given a specific position."""
def findNearestNode(pos):
	'''
	pos is a Math.vec3, a vector with 3 coordinates
	'''
	
	#define a minimum distant for your search
	min_dist = 1.0e16
	
	#initialize a variable to store your nearest element
	nearest = None
	
	#iterate over the nodes if they are positioned within the defined minimum distance
	for _, node in mesh.nodes.items():
		#position of the nodes
		d = (pos - node.position).norm()
		#condition to be within the min_dist
		if d < min_dist:
			min_dist = d
			#save the node 
			nearest = node
	#return the node and it's distance from the reference position
	return (nearest, min_dist)


"""Function to find the nearest element given a specific position. The search is operated in reference to the element barycenter position.
You can specify if the element is of a specific topology, for example to exclude edges or faces from the search.""" 
def findNearestElement(pos, only_topology = None):
	'''
	pos is a Math.vec3, a vector with 3 coordinates
	'''
	
	#define a minimum distant for your search
	min_dist = 1.0e16
	
	#initialize a variable to store your nearest element
	nearest = None
	
	#iterate over the elements if they are positioned within the defined minimum distance
	for _, elem in mesh.elements.items():
	
		#if you did define the topology
		if only_topology is not None:
		
			#skip over the elements with topologies different from the one specified
			if elem.topologyType() != only_topology:
				continue
		
		#position of the barycenter of the element
		d = (pos - elem.computeCenter()).norm()
		
		#condition to be within the min_dist
		if d < min_dist:
			min_dist = d
			#save the element
			nearest = elem
	
	#return the node and it's distance from the reference position
	return (nearest, min_dist)

#Let's search for the id and position of Node 3
N,D = findNearestNode(Math.vec3(0,0,0))
print('Node = ', N.id)
print('Distance = ', D)

#Let's search for the id and position of element 47
E,D = findNearestElement(Math.vec3(0,0,0), only_topology=MpcElementTopologyType.Face)
print('Element = ', E.id, E.geometryFamilyType(), E.topologyType())
print('Distance = ', D)


