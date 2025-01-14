from PyMpc import *
import math
import os
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
	QApplication,
	QDialog,
	QVBoxLayout,
	QProgressBar,
	QMessageBox,
	QInputDialog,
	QFileDialog,
	)

# define some variables here so that they can
# be used by other function defined below
#
# get the post-document
App.clearTerminal()
doc = App.postDocument()
# the active STKO window
win = QApplication.activeWindow()
# The title for this script windows
wtitle = 'Extract Results From Selection'

# progress dialog.
# this is used to monitor the progress of a lengthy operation
class ProgressDialog(QDialog):
	def __init__(self, title='Progress', barmin=0, barmax=100, parent=None):
		super().__init__(parent=parent)
		l = QVBoxLayout()
		bar = QProgressBar(self)
		self.barmin = barmin
		self.barmax = barmax
		bar.setRange(self.barmin, self.barmax)
		bar.setValue(self.barmin)
		bar.setTextVisible(True)
		bar.setAlignment(Qt.AlignCenter)
		l.addWidget(bar)
		self.bar = bar
		self.setLayout(l)
		self.setModal(True)
		self.setWindowTitle(title)
	def setPercentage(self, p):
		self.bar.setValue(self.barmin + (self.barmax-self.barmin)*p)

# utility function: get a database
def AskForDatabase():
	data = {}
	database = None
	for id, db in doc.databases.items():
		key = '[{}] {}'.format(id, os.path.basename(db.fileName))
		data[key] = id
	if len(data) > 0:
		items = list(data.keys())
		result, ok = QInputDialog.getItem(
			win, wtitle, 'Select DB', items, editable=False)
		if ok:
			db_id = data[result]
			database = doc.getDatabase(db_id)
	if database is None:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo Database selected')
	return database

# utility function: get a nodal result
def AskForNodalResult(db):
	res_map = {}
	for id in db.getNodalResultIds():
		result = db.getNodalResult(id)
		if result is None:
			continue
		key = '[{}] {}'.format(id, result.displayName())
		res_map[key] = id
	selection = QInputDialog.getItem(win, wtitle, 
		'Select the nodal results to extract', list(res_map.keys()), 
		editable=False)
	if not selection[1]:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo Result selected')
		return None
	return res_map[selection[0]]

# utility function: get a element result
def AskForElementalResult(db):
	res_map = {}
	for id in db.getElementalResultIds():
		result = db.getElementalResult(id)
		if result is None:
			continue
		key = '[{}] {}'.format(id, result.displayName())
		res_map[key] = id
	selection = QInputDialog.getItem(win, wtitle, 
		'Select the element results to extract', list(res_map.keys()), 
		editable=False)
	if not selection[1]:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo Result selected')
		return None
	return res_map[selection[0]]

# utility function: ask for result type
def AskForResultType():
	# return true if node-based result, false if element-based result
	res_map = {'Node-Result':True, 'Element-Result':False}
	selection = QInputDialog.getItem(win, wtitle, 
		'Select the Result Type', list(res_map.keys()), 
		editable=False)
	if not selection[1]:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo Result Type selected')
		return None
	return res_map[selection[0]]

# utility function: check selection
def GetSelectedNodes():
	nodes = []
	for plot_id, selection in doc.scene.plotSelection.items():
		for node_id in selection.info.nodes:
			nodes.append(node_id)
	return list(set(nodes))

# utility function: check selection
def GetSelectedElements():
	elements = []
	for plot_id, selection in doc.scene.plotSelection.items():
		for ele_id in selection.info.elements:
			elements.append(ele_id)
	return list(set(elements))

# do a first evaluation at the last stage to get the mesh
def GetMesh(db, result):
	all_stages = db.getStageIDs()
	if len(all_stages) == 0: return None
	last_stage = all_stages[-1]
	all_steps = db.getStepIDs(last_stage)
	if len(all_steps) == 0: return None
	last_step = all_steps[-1]
	opt = MpcOdbVirtualResultEvaluationOptions()
	opt.stage = last_stage
	opt.step = last_step
	field = result.evaluate(opt)
	if field is None: return None
	return field.mesh

# The main function to run
def PerformExtraction():

	# get the database
	db = AskForDatabase()
	if db is None:
		return None
	
	# ask for result type
	is_nodal = AskForResultType()
	is_ele_gauss = False
	is_ele_fiber = False
	
	# get the result
	if is_nodal:
		result_id = AskForNodalResult(db)
		if result_id is None:
			return None
		result = db.getNodalResult(result_id)
	else:
		result_id = AskForElementalResult(db)
		if result_id is None:
			return None
		result = db.getElementalResult(result_id)
	if result is None:
		return None
	
	# get selection
	if is_nodal:
		selection = GetSelectedNodes()
	else:
		selection = GetSelectedElements()
	
	# if the selection is element-based we need to understand what type
	# it is: ele-node? gauss? fiber?.
	if is_nodal:
		first_label = "Node"
	else:
		first_label = "Element"
		if "material." in result.displayName() or "section." in result.displayName():
			first_label += "-Gauss"
			is_ele_gauss = True
			if "fiber." in result.displayName():
				first_label += "-Fiber"
				is_ele_fiber = True
		else:
			first_label += "-Node"
	
	# get the mesh
	mesh = GetMesh(db, result)
	if mesh is None:
		return None
	
	# open a file for writing
	# format:
	# each row will contain results for a time step.
	# for each node/element there will be 1 column with the ID, followed by all components
	# at that time step for that node/element
	ofile_name, ok = QFileDialog.getSaveFileName(win, 'Output File', '.')
	if not ok:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo file selected')
		return None
	# some formats
	fmt_str = '{:>12s}'
	fmt_num = '{:>12.4g}'
	# some trial max number of iterations to guess number of gauss or fibers
	max_num_fiber = 100000
	with open(ofile_name, 'w+') as ofile:
		# result.componentLabels()
		header_done = False
		# make the dialog
		dialog = ProgressDialog(parent=win, title=wtitle)
		the_exception = None
		try:
			dialog.show()
			# create the evaluation option
			# evaluate all the results for each stage, for each step, and for each node.
			opt = MpcOdbVirtualResultEvaluationOptions()
			all_stages = db.getStageIDs()
			for stage_id in all_stages:
				all_steps = db.getStepIDs(stage_id)
				opt.stage = stage_id
				increment = 0
				for step_id in all_steps:
					print('Processing step {}'.format(step_id))
					dialog.setPercentage(float(increment+1)/float(len(all_steps)))
					increment += 1
					App.processEvents()
					opt.step = step_id
					field = result.evaluate(opt)
					# first write the header
					if not header_done:
						# step
						ofile.write(fmt_str.format('STEP_ID'))
						if is_nodal:
							# process all nodes
							for node_id in selection:
								ofile.write(fmt_str.format('NODE'))
								for comp in result.componentLabels():
									ofile.write(fmt_str.format(comp))
						else:
							# elements...
							if is_ele_gauss:
								if is_ele_fiber:
									# process all element gauss and fibers
									for ele_id in selection:
										ele = mesh.getElement(ele_id)
										for gauss_id in range(ele.numberOfIntegrationPoints()):
											for fiber_id in range(max_num_fiber):
												try:
													field[MpcOdbResultField.fiber(ele_id, gauss_id, fiber_id)] # dummy call
													ofile.write(fmt_str.format('ELE-GP-FIB'))
													for comp in result.componentLabels():
														ofile.write(fmt_str.format(comp))
												except:
													break
								else:
									# process all element gauss
									for ele_id in selection:
										ele = mesh.getElement(ele_id)
										for gauss_id in range(ele.numberOfIntegrationPoints()):
											ofile.write(fmt_str.format('ELE-GP'))
											for comp in result.componentLabels():
												ofile.write(fmt_str.format(comp))
							else:
								# process all element nodes
								for ele_id in selection:
									ele = mesh.getElement(ele_id)
									for node_id in range(ele.numberOfNodes()):
										ofile.write(fmt_str.format('ELE-NODE'))
										for comp in result.componentLabels():
											ofile.write(fmt_str.format(comp))
						# next line
						ofile.write('\n')
						# write the header only once
						header_done = True
					# then evaluate all objects (nodes/elements/gauss/fibers)
					# step
					ofile.write(fmt_num.format(step_id))
					if is_nodal:
						# process all nodes
						for node_id in selection:
							ofile.write(fmt_num.format(node_id))
							row = MpcOdbResultField.node(node_id) 
							value = field[row]
							for j in range(len(value)):
								ofile.write(fmt_num.format(value[j]))
					else:
						# elements...
						if is_ele_gauss:
							if is_ele_fiber:
								# process all element gauss and fibers
								for ele_id in selection:
									ele = mesh.getElement(ele_id)
									for gauss_id in range(ele.numberOfIntegrationPoints()):
										for fiber_id in range(max_num_fiber):
											try:
												row = MpcOdbResultField.fiber(ele_id, gauss_id, fiber_id)
												value = field[row]
												ofile.write(fmt_str.format('{}-{}-{}'.format(ele_id, gauss_id, fiber_id)))
												for j in range(len(value)):
													ofile.write(fmt_num.format(value[j]))
											except:
												break
							else:
								# process all element gauss
								for ele_id in selection:
									ele = mesh.getElement(ele_id)
									for gauss_id in range(ele.numberOfIntegrationPoints()):
										row = MpcOdbResultField.gauss(ele_id, gauss_id)
										value = field[row]
										ofile.write(fmt_str.format('{}-{}'.format(ele_id, gauss_id)))
										for j in range(len(value)):
											ofile.write(fmt_num.format(value[j]))
						else:
							# process all element nodes
							for ele_id in selection:
								ele = mesh.getElement(ele_id)
								for node_id in range(ele.numberOfNodes()):
									row = MpcOdbResultField.element(ele_id, node_id)
									value = field[row]
									ofile.write(fmt_str.format('{}-{}'.format(ele_id, node_id)))
									for j in range(len(value)):
										ofile.write(fmt_num.format(value[j]))
					# next line
					ofile.write('\n')
		except Exception as ex:
			the_exception = ex
		finally:
			dialog.accept()
			dialog.deleteLater()
		# check
		if the_exception:
			raise the_exception

# run the function to perform extraction
PerformExtraction()