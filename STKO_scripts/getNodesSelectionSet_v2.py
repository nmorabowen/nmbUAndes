from PyMpc import *
from STKO_baseFunctions_bak import STKOMeshExtractor

App.clearTerminal()
doc = App.caeDocument()

# Create an instance of the extractor
extractor = STKOMeshExtractor(doc, selection_set_id=14)
# Run the extraction
extractor.run_extraction()



