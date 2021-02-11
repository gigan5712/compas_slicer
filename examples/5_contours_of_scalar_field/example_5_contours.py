import logging
from compas.geometry import Plane, Point, Vector, distance_point_plane
from compas.datastructures import Mesh
import os
import compas_slicer.utilities as slicer_utils
from compas_slicer.post_processing import simplify_paths_rdp
from compas_slicer.slicers import ScalarFieldSlicer
import compas_slicer.utilities as utils
from compas_slicer.print_organization import ScalarFieldPrintOrganizer
from compas_slicer.print_organization import set_extruder_toggle

logger = logging.getLogger('logger')
logging.basicConfig(format='%(levelname)s-%(message)s', level=logging.INFO)

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_PATH = slicer_utils.get_output_directory(DATA_PATH)
MODEL = '_mesh.obj'

if __name__ == '__main__':
    # load mesh
    mesh = Mesh.from_obj(os.path.join(DATA_PATH, MODEL))

    # Create scalar field
    plane = Plane(Point(0, 0, -30), Vector(0.0, 0.5, 0.5))
    v_coords = [mesh.vertex_coordinates(v_key, axes='xyz') for v_key in mesh.vertices()]
    u = [distance_point_plane(v, plane) for v in v_coords]

    mesh.update_default_vertex_attributes({'scalar_field': 0.0})
    for i, (v_key, data) in enumerate(mesh.vertices(data=True)):
        data['scalar_field'] = u[i]

    # generate contours of scalar field
    slicer = ScalarFieldSlicer(mesh, u, no_of_isocurves=30)
    slicer.slice_model()
    slicer_utils.save_to_json(slicer.to_data(), OUTPUT_PATH, 'isocontours.json')
    simplify_paths_rdp(slicer, threshold=0.8)

    # create printpoints
    print_organizer = ScalarFieldPrintOrganizer(slicer, parameters={}, DATA_PATH=DATA_PATH)
    print_organizer.create_printpoints()

    set_extruder_toggle(print_organizer, slicer)

    print_organizer.printout_info()
    printpoints_data = print_organizer.output_printpoints_dict()
    utils.save_to_json(printpoints_data, OUTPUT_PATH, 'out_printpoints.json')

    # grad_norms = []
    # grads = []
    # for layer_key in print_organizer.printpoints_dict:
    #     for path_key in print_organizer.printpoints_dict[layer_key]:
    #         for ppt in print_organizer.printpoints_dict[layer_key][path_key]:
    #             grad_norm = ppt.attributes['gradient_norm']
    #             grad = ppt.attributes['gradient']
    #             grad_norms.append(grad_norm)
    #             grads.append(grad)
    #
    # utils.save_to_json(grad_norms, OUTPUT_PATH, 'reconstructed_gradient_norm.json')
    # utils.save_to_json(utils.point_list_to_dict(grads), OUTPUT_PATH, 'reconstructed_gradient.json')


