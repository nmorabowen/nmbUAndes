from PyMpc import App, IO

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

def write_in_terminal(string:str):
    IO.write_cout(string+'\n')

def write_in_terminal_blue(string:str):
    IO.write_clog(string+'\n')
    
def write_in_terminal_red(string:str):
    IO.write_cerr(string+'\n')
