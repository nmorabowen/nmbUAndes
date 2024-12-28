import os
import math
import itertools
import numpy as np
import time
import traceback
import sys
from PyMpc import *
from PyMpc import MpcOdbVirtualResult as vr
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
	QApplication,
	QMessageBox,
	QInputDialog,
	QLineEdit,
	QProgressBar,
	QDialog,
	QVBoxLayout,
	QListWidget,
	QListWidgetItem,
	QLabel,
	QDialogButtonBox,
	)

# get document and active window
# App.clearTerminal()
doc = App.postDocument()
win = QApplication.activeWindow()
wtitle = 'Section Cut'

# globals
class _globals:
	# an absolute tolerance
	length_tolerance = 1.0e-5
	angle_tolerance = 1.0e-10
	oop_tol = 0.03 # in gloabl coord!!!
	# a list of tuples for computing angles in 4-node polygons
	q4_angle_indices = ((1,3), (2,0), (3,1), (0,2))
	# sub-triangles of a quad
	qsubs = ((0,1,2),(0,2,3))

# the extraction type
class extraction_type:
	end = 'End'
	end_of_each_stage = 'End of each stage'
	all = 'All Steps'
	step = '1000'
	options = [end, end_of_each_stage, all, step]

# progress dialog
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

# multiple input dialog
class ListMultipleInputDialog(QDialog):
	def __init__(self, title='Select Results', label=None, names = [], parent=None):
		super().__init__(parent=parent)
		l = QVBoxLayout()
		if label:
			l.addWidget(QLabel(label))
		listwidget = QListWidget(self)
		for item in names:
			listitem = QListWidgetItem(item,  listwidget)
			listitem.setCheckState(Qt.Unchecked)
			listwidget.addItem(listitem)
		l.addWidget(listwidget)
		bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		bbox.accepted.connect(self.accept)
		bbox.rejected.connect(self.reject)
		l.addWidget(bbox)
		self.listwidget = listwidget
		self.setLayout(l)
		self.setModal(True)
		self.setWindowTitle(title)
	def getItems(parent, title, label, names):
		d = ListMultipleInputDialog(title, label, names,parent)
		if d.exec_() != QDialog.Accepted:
			return []
		results = []
		for i in range(d.listwidget.count()):
			item = d.listwidget.item(i)
			if item.checkState() == Qt.Checked:
				results.append(item.text())
		d.deleteLater()
		return results

# geom utils
def point_in_triangle(nodes, trial, lch):
	G = np.asarray([[trial.x],[trial.y], [trial.z]])
	# position matrix
	n = len(nodes)
	X = np.zeros((3,n))
	for i in range(n):
		inode = nodes[i]
		X[0, i] = inode.x
		X[1, i] = inode.y
		X[2, i] = inode.z
	dN = np.asarray([
		[-1.0, -1.0, 0.0],
		[1.0, 0.0, 0.0],
		[0.0, 1.0, 0.0]])
	J = np.matmul(X,dN)
	vx = J[:,0]
	vy = J[:,1]
	vz = np.cross(vx, vy)
	vz /= max(np.linalg.norm(vz), 1.0e-16)
	J[:,2] = vz
	iJ = np.linalg.inv(J)
	J[:,2] = 0.0
	x,y = 0.0, 0.0
	N = np.asarray([[1.0-x-y],[x],[y]])
	P = np.matmul(X,N)
	D = G-P
	L = np.matmul(iJ,D)
	# result
	x,y,z = L[0,0], L[1,0], L[2,0]
	# check for negative values as an error measure
	N = np.asarray([[1.0-x-y],[x],[y]])
	distance = 0.0
	for i in range(3):
		iN = N[i][0]
		if iN < 0.0:
			distance = max(distance, -iN)
	return distance < 1.0e-2 and abs(z) < _globals.oop_tol

# get database
def get_database():
	data = {}
	db = None
	for id, db in doc.databases.items():
		key = '[{}] {}'.format(id, os.path.basename(db.fileName))
		data[key] = id
	if len(data) == 1:
		db_id = list(data.values())[0]
		db = doc.getDatabase(db_id)
	elif len(data) > 1:
		items = list(data.values())
		result, ok = QInputDialog.getItem(
			win, wtitle, 'Select DB', items, editable=False)
		if ok:
			db_id = data[result]
			db = doc.getDatabase(db_id)
	if db is None:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo Database selected')
	return db

# get a mesh
def get_mesh(db):
	U = db.getNodalResult('Displacement')
	if U is None: return None
	all_stages = db.getStageIDs()
	if len(all_stages) == 0: return None
	last_stage = all_stages[-1]
	all_steps = db.getStepIDs(last_stage)
	if len(all_steps) == 0: return None
	last_step = all_steps[-1]
	opt = MpcOdbVirtualResultEvaluationOptions()
	opt.stage = last_stage
	opt.step = last_step
	field = U.evaluate(opt)
	if field is None: return None
	return field.mesh

# get selection
def get_selection(mesh):
	# get nodes from selection
	selection = doc.scene.plotSelection
	node_ids = []
	for _, data in selection.items():
		for i in data.info.nodes:
			node_ids.append(i)
	node_ids = list(set(node_ids))
	nodes = [None]*len(node_ids)
	for i in range(len(node_ids)):
		inode = mesh.getNode(node_ids[i])
		if inode is None:
			QMessageBox.critical(win, wtitle, 'Abort:\nNull Node Found')
		nodes[i] = inode
	n = len(nodes)
	if n == 0:
		QMessageBox.critical(win, wtitle, 'Abort:\nNo node selected')
	elif n == 2:
		print('Found 2 points: Line Cut')
		distance = (nodes[1].position - nodes[0].position).norm()
		if distance < _globals.length_tolerance:
			QMessageBox.critical(win, wtitle, 
				'Abort:\nThe 2 selected nodes coincide (distance = {:.2g})'.format(distance))
			nodes = []
	elif n == 3:
		print('Found 3 points: Triangular Surface Cut')
		a = nodes[1].position - nodes[0].position
		b = nodes[2].position - nodes[0].position
		area = a.cross(b).norm()/2.0
		if math.sqrt(2.0*area) < _globals.length_tolerance:
			QMessageBox.critical(win, wtitle, 
				'Abort:\nThe 3 selected nodes form a collapsed triangle (area = {:.2g})'.format(area))
			nodes = []
	elif n == 4:
		print('Found 4 points: Quadrilateral Surface Cut')
		asum = 0.0
		q = [nodes[0], None, None, None]
		others = [1,2,3]
		found = False
		for perm in itertools.permutations(others):
			for i in range(3): q[perm[i]] = nodes[i+1]
			# check this permutation
			asum = 0.0
			for i in range(4):
				aux = _globals.q4_angle_indices[i]
				a = q[aux[0]].position - q[i].position
				b = q[aux[1]].position - q[i].position
				an = a.norm()
				if an < _globals.length_tolerance: continue
				bn = b.norm()
				if bn < _globals.length_tolerance: continue
				a /= an
				b /= bn
				asum += math.acos(a.dot(b))
			error = abs(2.0*math.pi - asum)
			if error < _globals.angle_tolerance:
				found = True
				nodes = q
				break
		if not found:
			QMessageBox.critical(win, wtitle, 
				'Abort:\nThe 4 selected nodes do not form a convex quadrilateral'.format(n))
			nodes = []
	else:
		QMessageBox.critical(win, wtitle, 
			'Abort:\nInvalid number of nodes ({}).\nOnly 2, 3 or 4 nodes are allowed'.format(n))
	# done
	center = Math.vec3(0.0,0.0,0.0)
	lch = 0.0
	if len(nodes) > 0:
		bbox = FxBndBox()
		for node in nodes:
			bbox.add(node.position)
		center = (bbox.minPoint + bbox.maxPoint)/2.0
		lch = (bbox.maxPoint - bbox.minPoint).norm()
	return nodes, center, lch

# compute triad
def get_orientation(nodes, center, lch):
	n = len(nodes)
	dx = Math.vec3(1.0,0.0,0.0)
	dy = Math.vec3(0.0,1.0,0.0)
	dz = Math.vec3(0.0,0.0,1.0)
	if n == 2:
		p1 = nodes[0].position
		p2 = nodes[1].position
		dy = (p2-p1).normalized()
		if abs(dy[2]) < 0.99:
			# not aligned with global Z
			dx = Math.vec3(0.0, 0.0, 1.0)
			dz = dx.cross(dy).normalized()
			dx = dy.cross(dz).normalized()
		else:
			dx = Math.vec3(1.0, 0.0, 0.0)
			dz = dx.cross(dy).normalized()
			dx = dy.cross(dz).normalized()
	elif n > 2:
		p1 = nodes[0].position
		p2 = nodes[1].position
		p3 = nodes[2].position
		dy = (p2-p1).normalized()
		dz = (p3-p1).normalized()
		dx = dy.cross(dz).normalized()
		dz = dx.cross(dy).normalized()
	# print and update ...
	vrep = None
	def make_vrep(vrep):
		if vrep:
			doc.removeCustomDrawableEntity(vrep)
		vrep = FxShape()
		for dir,col in zip( (dx,dy,dz), 
				(Math.vec3(0.8,0.0,0.0), Math.vec3(0.0,0.8,0.0), Math.vec3(0.0,0.0,0.8)) ):
			edge = FxShapeEdge()
			edge.indices.append(0)
			edge.indices.append(1)
			edge.vertices.append(Math.vertex(center, col))
			edge.vertices.append(Math.vertex(center + dir * lch/4.0, col))
			vrep.edges.append(edge)
		mat = FxMaterial()
		mat.lineWidth = 4.0
		mat.coloringMode = FxColoringMode.ColorizeUsingNormals
		mat.lighting = False
		vrep.material = mat
		vrep.commitChanges()
		doc.addCustomDrawableEntity(vrep)
		App.updateActiveView()
		return vrep
	vrep = make_vrep(vrep)
	axes = {'X':dx, 'Y':dy, 'Z':dz}
	while True:
		answer, ok = QInputDialog.getItem(win, wtitle,
			'Do you want to rotate about an axis?\nIf Yes, please select the axis',
			['X','Y','Z'], editable=False)
		if not ok:
			break
		dir = axes[answer]
		answer, ok = QInputDialog.getDouble(win, wtitle,
			'Please enter the rotation angle in degrees',
			0.0, -360.0, 360.0, 2, Qt.WindowFlags(), 90.0)
		if not ok:
			break
		angle = answer*math.pi/180.0
		qvec = dir.normalized() * math.sin(angle/2.0)
		qang = math.cos(angle/2.0)
		quat = Math.quaternion(qang, qvec.x, qvec.y, qvec.z)
		quat.normalize()
		dx = quat.rotate(dx)
		dy = quat.rotate(dy)
		dz = quat.rotate(dz)
		vrep = make_vrep(vrep)
	# done
	return dx,dy,dz

# element info
class element_info_t:
	def __init__(self, ele, node_pos, nodes):
		# the MpcElement object
		self.element = ele
		# a list of positions (0 to len(ele.nodes)-1)
		# of the nodes on the section cut
		self.node_positions = node_pos
		# and the nodes
		self.nodes = nodes

# expand selection
def expand_selection(poly_nodes, mesh, center, lch):
	nodes = []
	n = len(poly_nodes)
	if n == 2:
		# get all nodes along line
		p1 = poly_nodes[0].position
		p2 = poly_nodes[1].position
		dx = p2-p1
		L2 = dx.dot(dx)
		tol = L2*1.0e-6
		for _, node in mesh.nodes.items():
			if node.id==poly_nodes[0].id or node.id==poly_nodes[1].id:
				nodes.append(node)
			else:
				p3 = node.position
				dy = p3-p1
				if dx.cross(dy).norm() < tol:
					dp = dy.dot(dx)
					if dp > -tol and dp < L2+tol:
						nodes.append(node)
	elif n == 3:
		# get all nodes in triangle
		for _, node in mesh.nodes.items():
			if (node.position - center).norm() <= lch/2.0 + _globals.length_tolerance:
				if point_in_triangle(poly_nodes, node, lch):
					nodes.append(node)
	elif n == 4:
		# get all nodes in quad
		T1 = [poly_nodes[i] for i in _globals.qsubs[0]]
		T2 = [poly_nodes[i] for i in _globals.qsubs[1]]
		for _, node in mesh.nodes.items():
			if (node.position - center).norm() <= lch/2.0 + _globals.length_tolerance:
				if point_in_triangle(T1, node, lch) or point_in_triangle(T2, node, lch):
					nodes.append(node)
	# vrep
	vrep = FxShape()
	counter = 0
	for node in nodes:
		vrep.vertices.indices.append(counter)
		vrep.vertices.vertices.append(Math.vertex(node.position))
		counter += 1
	mat = FxMaterial()
	mat.pointColor = FxColor(0.0, 0.4, 1.0)
	mat.pointSize = 5.0
	vrep.material = mat
	vrep.commitChanges()
	doc.addCustomDrawableEntity(vrep)
	# done
	return nodes

# process selection
def process_selection(selected_nodes, mesh, center, lch, dx, scale):
	t1 = time.time()
	# find all elements sharing nodes with selected_nodes
	ele_infos = {}
	for _, ele in mesh.elements.items():
		cc0 = ele.computeCenter()-center
		if cc0.dot(dx)*scale < -1.0e-8*lch and cc0.norm() <= lch*0.55:
			node_positions = []
			nodes = []
			for node in selected_nodes:
				for node_position in range(len(ele.nodes)):
					if node.id == ele.nodes[node_position].id:
						nodes.append(node)
						node_positions.append(node_position)
			if len(node_positions) > 0:
				ele_infos[ele.id] = element_info_t(ele, node_positions, nodes)
	# select elements for checking
	if doc.activePlotGroup and len(doc.activePlotGroup.plots) > 0:
		pid = list(doc.activePlotGroup.plots.keys())[0]
		seldata = doc.scene.plotSelection.get(pid, None)
		if seldata is None:
			seldata = MpcOdpSelectionData()
			doc.scene.plotSelection[pid] = seldata
		for id, _ in ele_infos.items():
			seldata.info.elements.insert(id)
		doc.scene.updateSelectionVisualRepresentationAndGraphics()
		App.updateActiveView()
	# check time... this seems expensive
	t2 = time.time()
	dt = t2-t1
	print('Expand selection - elapsed: {:.3g} seconds.'.format(dt))
	# done
	return ele_infos

# integrate
def integrate(db, ele_infos, center, dx, dy, dz, scale):
	# fake mesh
	sub_mesh = MpcMesh()
	for _, info in ele_infos.items():
		ele = info.element
		for node in ele.nodes:
			sub_mesh.addNode(node)
		sub_mesh.addElement(ele)
	# spatial dimension
	dim = db.info.spatialDimension
	# get all results and map them to their name
	results = {}
	for id in db.getElementalResultIds():
		result = db.getElementalResult(id)
		name = '[{}] {}'.format(id, result.displayName())
		if len(name) > 50:
			name = name[:35] + ' ... ' + name[-15:]
		results[name] = result
	# choose results
	selection = ListMultipleInputDialog.getItems(win, wtitle, 
		'Select the results to integrate', list(results.keys()))
	if len(selection) == 0:
		return None
	# choose extraction type
	extraction, ok = QInputDialog.getItem(win, wtitle, 
		'Select the extraction method',
		extraction_type.options, editable=False)
	if not ok:
		return None
	print('Extraction method: {}'.format(extraction))
	# stage-step pairs for evaluation
	stage_and_steps = []
	all_stages = db.getStageIDs()
	if extraction == extraction_type.end:
		last_stage = all_stages[-1]
		all_steps = db.getStepIDs(last_stage)
		last_step = all_steps[-1]
		stage_and_steps.append((last_stage, last_step))
	if extraction == extraction_type.step:
		last_stage = all_stages[-1]
		step = 1000
		stage_and_steps.append((last_stage, step))
	elif extraction == extraction_type.end_of_each_stage:
		for stage in all_stages:
			all_steps = db.getStepIDs(stage)
			last_step = all_steps[-1]
			stage_and_steps.append((stage, last_step))
	else:
		for stage in all_stages:
			all_steps = db.getStepIDs(stage)
			for step in all_steps:
				stage_and_steps.append((stage, step))
	NUM_OUT = len(stage_and_steps)
	# open the progress bar
	dialog = ProgressDialog(parent=win, title=wtitle)
	the_exception = None
	try:
		dialog.show()
		# some variables to store temporaries
		F = Math.vec3(0.0, 0.0, 0.0)
		M = Math.vec3(0.0, 0.0, 0.0)
		LF = Math.vec3(0.0, 0.0, 0.0)
		LM = Math.vec3(0.0, 0.0, 0.0)
		X = Math.vec3(0.0, 0.0, 0.0)
		R = (dx, dy, dz)
		OUT = np.zeros((NUM_OUT, 6))
		# make the evaluation option
		opt = MpcOdbVirtualResultEvaluationOptions()
		opt.mesh = sub_mesh
		for increment in range(NUM_OUT):
			opt.stage, opt.step = stage_and_steps[increment]
			# for each result
			for ith_selection in selection:
				result = results[ith_selection]
				#print('Result = {}'.format(result))
				ncomp = result.size()
				if ncomp < 2: continue
				# evaluate result
				field = result.evaluate(opt)
				# integrate
				for _, info in ele_infos.items():
					elid = info.element.id
					for node_pos, node in zip(info.node_positions, info.nodes):
						# get node-forces in global coordinates
						try:
							eleForces = field[MpcOdbResultField.element(elid, node_pos)]
						except:
							continue
						F[0] = eleForces[0]
						F[1] = eleForces[1]
						if dim == MpcOdbSpatialDimension.D2:
							F[2] = 0.0
							M[0] = 0.0
							M[1] = 0.0
							if ncomp > 2:
								M[2] = eleForces[2]
							else:
								M[2] = 0.0
						else:
							if ncomp > 2:
								F[2] = eleForces[2]
								if ncomp > 5:
									M[0] = eleForces[3]
									M[1] = eleForces[4]
									M[2] = eleForces[5]
							else:
								F[2] = 0.0
								M[0] = 0.0
								M[1] = 0.0
								M[2] = 0.0
						# get forces and location in local coordinates
						delta = node.position - center
						for i in range(3):
							iR = R[i]
							LF[i] = F.dot(iR)*scale
							LM[i] = M.dot(iR)*scale
							X[i] = delta.dot(iR)
						# integrate them
						for i in range(3):
							OUT[increment, i] += LF[i]
							OUT[increment, i+3] += LM[i]
						OUT[increment, 3] += LF[2]*X[1] - LF[1]*X[2] # Mx = Fz * dy - Fy * dz
						OUT[increment, 4] += LF[0]*X[2] - LF[2]*X[0] # My = Fx * dz - Fz * dx
						OUT[increment, 5] += LF[1]*X[0] - LF[0]*X[1] # Mz = Fy * dx - Fx * dy
			# update
			dialog.setPercentage(float(increment+1)/float(NUM_OUT))
			App.processEvents()
	except Exception as ex:
		the_exception = ex
	finally:
		dialog.accept()
		dialog.deleteLater()
	# check
	if the_exception:
		raise the_exception
	# done
	return OUT

# main function
def make_section_cut():
	# start
	doc.clearCustomDrawableEntities()
	# get database
	db = get_database()
	if db is None:
		return False
	# get info
	dimension = db.info.spatialDimension
	if dimension != MpcOdbSpatialDimension.D2 and dimension != MpcOdbSpatialDimension.D3:
		QMessageBox.critical(win, wtitle, 
			'Abort:\nInvalid dimension {}. Only 2D and 3D allowed'.format(dimension))
		return False
	# get a mesh
	mesh = get_mesh(db)
	if mesh is None:
		QMessageBox.critical(win, wtitle, 'Abort:\nCannot obtain the mesh')
		return False
	# get selection
	nodes, center, lch = get_selection(mesh)
	if len(nodes) == 0:
		return False
	# get orientation
	dx,dy,dz = get_orientation(nodes, center, lch)
	# expand selection
	nodes = expand_selection(nodes, mesh, center, lch)
	if len(nodes) == 0:
		return False
	# process selection
	scale = 1.0
	ele_infos = process_selection(nodes, mesh, center, lch, dx, scale)
	if len(ele_infos) == 0:
		print('Cannot find elements in the -dX direction. Try other side (scale = -1)')
		scale = -1.0
		ele_infos = process_selection(nodes, mesh, center, lch, dx, scale)
		if len(ele_infos) == 0:
			QMessageBox.critical(win, wtitle, 'Abort:\nNo Elements connected to the cut nodes')
			return False
	# check integration orientation
	answer, ok = QInputDialog.getItem(win, wtitle,
		'Choose the orientation of results (Default=Local)',
		['Local','Global'], editable=False)
	if not ok:
		return False
	if answer == 'Global':
		dx = Math.vec3(1.0,0.0,0.0)
		dy = Math.vec3(0.0,1.0,0.0)
		dz = Math.vec3(0.0,0.0,1.0)
	
	# integrate
	forces = integrate(db, ele_infos, center, dx, dy, dz, scale)
	if forces is None:
		return False
	# print
	fmt_str = '{:>14s}'*6
	fmt_flt = '{:14.4g}'*6
	print(fmt_str.format('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'))
	for i in range(forces.shape[0]):
		print(fmt_flt.format(*forces[i,:]))
# run
make_section_cut()
doc.clearCustomDrawableEntities()