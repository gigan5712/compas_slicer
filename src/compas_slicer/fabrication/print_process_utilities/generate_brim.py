import pyclipper

from pyclipper import scale_from_clipper, scale_to_clipper

from compas_slicer.geometry import Layer
from compas_slicer.geometry import Path
from compas_slicer.geometry import PrintPoint
from compas.geometry import Point

__all__ = ['generate_brim']


def generate_brim(printpoints_dict, layer_width, number_of_brim_layers):
    """Creates a brim around the bottom contours of the print.

    Parameters
    ----------
    printpoints_dict : dict
        A dict of lists with compas_slicer.geometry.PrintPoint instances
    layer_width : float
        A number representing the distance between brim contours 
        (typically the width of a layer)
    number_of_brim_layers : int
        Number of brim layers to add.
    """
    # TODO: Add functionality for merging several contours when the brims overlap.  

    # uses the default scaling factor of 2**32
    # see: https://github.com/fonttools/pyclipper/wiki/Deprecating-SCALING_FACTOR
    SCALING_FACTOR = 2 ** 32

    xy_coords_for_clipper = []

    for path_key in printpoints_dict['layer_0']:
        for printpoint in printpoints_dict['layer_0'][path_key]:
            # gets the X and Y coordinate since Clipper only does 2D offset operations
            xy_coords = [printpoint.pt[0], printpoint.pt[1]]
            xy_coords_for_clipper.append(xy_coords)

    # initialise Clipper
    pco = pyclipper.PyclipperOffset()
    pco.AddPath(scale_to_clipper(xy_coords_for_clipper, SCALING_FACTOR), pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)

    clipper_printpoints = []

    for i in range(number_of_brim_layers):
        clipper_points_per_brim_layer = []

        # gets result
        result = scale_from_clipper(pco.Execute((i + 1) * layer_width * SCALING_FACTOR), SCALING_FACTOR)

        for xy in result[0]:
            # gets the X and Y coordinate from the Clipper result
            x = xy[0]
            y = xy[1]
            z = printpoints_dict['layer_0']['path_0'][0].pt[2] # get the Z coordinate from the previous slicing result

            clipper_points_per_brim_layer.append(Point(x, y, z))

        # adds first point again to form a closed polygon since clipper removes this point
        clipper_points_per_brim_layer = clipper_points_per_brim_layer + [clipper_points_per_brim_layer[0]]
        # create new contours for the Clipper offsets
        for pt in clipper_points_per_brim_layer:
            pp = PrintPoint(pt, layer_height=printpoints_dict['layer_0']['path_0'][0].layer_height)
            pp.extruder_toggle = True
            clipper_printpoints.append(pp)

        printpoints_dict['layer_0']['path_0'] = clipper_printpoints + printpoints_dict['layer_0']['path_0']



if __name__ == "__main__":
    pass
