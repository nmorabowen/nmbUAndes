from PyMpc import *
from STKO_APE import modelAPE
from STKO_APE import write_in_terminal_blue, write_in_terminal_red, write_in_terminal

file=modelAPE()

print('---------------------------------------')
selection_set_id=2
ss_results=file.extract_mesh_data_selectionSet(selection_set_id=selection_set_id)

print(ss_results)
print(ss_results['nodes'])

print('---------------------------------------')
selection_set_id=2
ss_results=file.extract_mesh_elements_selectionSet(selection_set_id=selection_set_id)

print('Nodes')
print(ss_results['nodes'])

print('Edges')
print(ss_results['edges'])

print('Faces')
print(ss_results['faces'])

from baseUnits import N, tf, kN
print(1*tf)