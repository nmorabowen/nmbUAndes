from PyMpc import *
import numpy as np
from time import sleep

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

# Get the pre processor object
doc = App.caeDocument()
print('==========================================================')
print('For the CAE Document object, the available methods are:')
print(dir(doc))

# Get the timeseries object
timeSeries = doc.getDefinition(3)

print('==========================================================')
print('For the timeseries object, the available methods are:')
print(dir(timeSeries))

print(timeSeries.componentId)

# Get the timeseries XObject
xobj_timeS = timeSeries.XObject

print('==========================================================')
print('For the timeseries XObject, the available methods are:')
print(dir(xobj_timeS))

print('==========================================================')

values=xobj_timeS.getAttribute('list_of_values')
time=xobj_timeS.getAttribute('list_of_times')

print(type(xobj_timeS))

print('==========================================================')
print('For the time object, the available methods are:')
print(dir(time))
print(type(time))

# Create plot from time series
doc = App.postDocument()
cdata = MpcChartData()
cdata.id = doc.genNextIdForChartData()
cdata.name = "TimeSeries Plot"
cdata.xLabel = "Time"
cdata.yLabel = "Values"
cdata.x=Math.double_array(time)
cdata.y=Math.double_array(values)
doc.addChartData(cdata)
doc.commitChanges()
doc.dirty = True
doc.select(cdata)
App.processEvents()


    
#clearCharts()