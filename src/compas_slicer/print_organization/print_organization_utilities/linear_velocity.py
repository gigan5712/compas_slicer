import logging
import math

logger = logging.getLogger('logger')

__all__ = ['set_linear_velocity']


def set_linear_velocity(printpoints_dict, velocity_type, v=25, per_layer_velocities=None):
    """ Sets the linear velocity parameter of the printpoints depending on the selected type.

    Parameters
    ----------
    printpoints_dict: dictionary of :class:`compas.slicer.geometry.PrintPoint`
        Dictionary of PrintPoints
    v: float
        Velocity value to set for printpoints.
    velocity_type: str
        Determines how to add linear velocity to the printpoints.

        constant:              one value used for all printpoints
        per_layer:             different values used for every layer
        matching_layer_height: set velocity in accordance to layer height
        matching_overhang:     set velocity in accordance to the overhang
    per_layer_velocities: list of floats
        If setting velocity per layer, provide a list of floats with equal length to the number of layers.

    """
    if not (velocity_type == "constant"
            or velocity_type == "per_layer"
            or velocity_type == "matching_layer_height"
            or velocity_type == "matching_overhang"):
        raise ValueError("Velocity method doesn't exist")

    for i, layer_key in enumerate(printpoints_dict):
        for path_key in printpoints_dict[layer_key]:
            path_printpoints = printpoints_dict[layer_key][path_key]
            for printpoint in path_printpoints:

                if velocity_type == "constant":
                    printpoint.velocity = v

                elif velocity_type == "per_layer":
                    assert per_layer_velocities, "You need to provide one velocity value per layer"
                    assert len(per_layer_velocities) == printpoints_dict, \
                        'Wrong number of velocity values. You need to provide one velocity value per layer, ' \
                        'on the "per_layer_velocities" list.'
                    printpoint.velocity = per_layer_velocities[i]

                elif velocity_type == "matching_layer_height":
                    printpoint.velocity = calculate_linear_velocity(printpoint)

                elif velocity_type == "matching_overhang":
                    raise NotImplementedError


#############################
#  Nozzle linear velocity

motor_omega = 2 * math.pi  # 1 revolution / sec = 2*pi rad/sec
motor_r = 4.0  # 4.25 #mm
motor_linear_speed = motor_omega * motor_r
D_filament = 2.75  # mm
filament_area = math.pi * (D_filament / 2.0) ** 2  # pi*r^2

multiplier = 0.25  # arbitrary value! You might have to change this


def calculate_linear_velocity(printpoint):  # path_area * robot_linear_speed = filament_area * motor_linear_speed
    layer_width = max(printpoint.layer_height, 0.4)
    path_area = layer_width * printpoint.layer_height
    linear_speed = (filament_area * motor_linear_speed) / path_area
    return linear_speed * multiplier
