import itertools
from compas.geometry import Point
from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
from progress.bar import Bar
import logging
import compas_slicer.utilities as utils
from compas.plugins import PluginNotInstalledError

packages = utils.TerminalCommand('conda list').get_split_output_strings()

if 'compas-cgal' in packages:
    from compas_cgal.slicer import slice_mesh

logger = logging.getLogger('logger')

__all__ = ['create_planar_paths_cgal']


def create_planar_paths_cgal(mesh, planes):
    """Creates planar contours using CGAL
    Considers all resulting paths as CLOSED paths.
    This is a very fast method.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        A compas mesh.
    planes: list, compas.geometry.Plane
    """
    if 'compas-cgal' not in packages:
        raise PluginNotInstalledError("--------ATTENTION! ----------- \
                        Compas_cgal library is missing! \
                        You can't use this planar slicing method without it. \
                        Check the README instructions for how to install it, \
                        or use another planar slicing method.")

    # initializes progress_bar for measuring progress
    progress_bar = Bar('Slicing', max=len(planes), suffix='Layer %(index)i/%(max)i - %(percent)d%%')

    # prepare mesh for slicing
    M = mesh.to_vertices_and_faces()

    # slicing operation
    contours = slice_mesh(M, planes)

    def get_grouped_list(item_list, key_function):
        # first sort, because grouping only groups consecutively matching items
        sorted_list = sorted(item_list, key=key_function)
        # group items, using the provided key function
        grouped_iter = itertools.groupby(sorted_list, key_function)
        # return reformatted list
        return [list(group) for _key, group in grouped_iter]

    def key_function(item):
        return item[0][2]

    cgal_layers = get_grouped_list(contours, key_function=key_function)

    layers = []
    for layer in cgal_layers:
        paths_per_layer = []
        for path in layer:
            points_per_contour = []
            for point in path:
                pt = Point(point[0], point[1], point[2])
                points_per_contour.append(pt)
            # compute contours
            # TODO: add a check for is_closed
            path = Path(points=points_per_contour, is_closed=True)
            paths_per_layer.append(path)

        # compute layers
        layer = Layer(paths_per_layer)
        layers.append(layer)

        # advance progressbar
        progress_bar.next()

    # finish progressbar
    progress_bar.finish()
    return layers


if __name__ == "__main__":
    pass