# __init__.py
def classFactory(iface):
    # Import the class from your main python file
    from .cell_grid_creator import CellGridCreatorPlugin
    return CellGridCreatorPlugin(iface)