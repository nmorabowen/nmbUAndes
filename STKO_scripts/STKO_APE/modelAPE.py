from PyMpc import App, MpcMesh, IO
# Mixins classes
from .STKOMeshExtractor import STKOMeshExtractor
from .mesh import mesh
from .selectionSet import selectionSet
# Functions
from .STKO_baseFunctions import write_in_terminal, write_in_terminal_blue, write_in_terminal_red


class modelAPE(STKOMeshExtractor, mesh, selectionSet):
    def __init__(self, verbose=False):
        """
        Initialize the main modelAPE class.
        """
        self.preprocessor = App.caeDocument()  # Main document instance
        self.mesh_object=self.preprocessor.mesh  # Mesh instance
        self.verbose=verbose
        
        if verbose is True:
            # Log a custom message
            IO.write_clog('LARGA VIDA AL LADRUÑO!!!\nModel object created')

    def extract_mesh_data(self, selection_set_id):
        """
        Wrapper to run the extraction process using the mixin's functionality.

        :param selection_set_id: The ID of the selection set to process.
        """
        print("[modelAPE] Starting mesh extraction...")
        self.run_extraction(self.preprocessor, selection_set_id)
       
    def get_name(self, verbose=False):
        """Return the file name and document name of the model.

        Returns:
            name_dict (dict): A dictionary containing the file name and document name.
        """
        
        name_dict = {
            'file_name': self.preprocessor.fileName,
            'document_name': self.preprocessor.documentName,
        }
        
        if self.verbose is True:
            verbose = True
        
        if verbose is True:
            write_in_terminal_blue(f"\nModel name information:")
            write_in_terminal(f"\nFile name: {name_dict['file_name']}")
            write_in_terminal(f"\nDocument name: {name_dict['document_name']}")
        
        return name_dict
