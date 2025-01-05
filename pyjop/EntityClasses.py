
import json
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple
)


from pyjop.EntityBase import (
    BaseEventData,
    EntityBase,
    EntityBaseStub,
    JoyfulException,
    NPArray,
    _is_custom_level_runner,
    _stack_size,
    await_receive,
    _parse_color,
    _parse_vector,
    _dispatch_events
)
from pyjop.Enums import *
import numpy as np
import time
from io import BytesIO
from matplotlib import colormaps
import matplotlib.cbook
from pyjop.Vector import Rotator3, Vector3


class ConveyorBelt(EntityBase["ConveyorBelt"]):
    """Conveyor Belt with variable belt speed for transporting objects. Can move objects forwards or backwards. Also has a sensor to check if it is transporting any objects."""

    def set_target_speed(self, speed: float):
        """Set the conveyor's target belt speed to the specified value.

        Args:
            speed (float): [-5,5] m/s, where negative numbers are backwards

        Example:
            >>>
            #get first conveyor in the current level
            conv = ConveyorBelt.first()
            #check if transporting
            if conv.get_is_transporting():
                #set to go backwards with speed -2.5
                conv.set_target_speed(-2.5)
            else: #not transporting, so stop moving
                conv.set_target_speed(0)
        """
        self._set_float("setTargetSpeed", float(speed))

    def get_is_transporting(self) -> bool:
        """Returns True if the belt is currently transporting something, else False

        Example:
            >>>
            conv = ConveyorBelt.first()
            if conv.get_is_transporting():
                print("conveyor belt is transporting something")
            else:
                print("conveyor belt is empty")
        """
        return self._get_bool("IsTransporting")

    def get_current_speed(self) -> float:
        """Get the current speed of the conveyor belt.

        Example:
            >>>
            speed = ConveyorBelt.first().get_current_speed()
            if speed > 0:
                print("forwards")
            elif speed < 0:
                print("backwards")
            else:
                print("stopped")
        """
        return self._get_float("CurrentSpeed")

    def editor_set_max_speed(self, max_speed:float):
        """Sets the maximum speed of the conveyor belt that the player can set it to. Defaults to 5. Maximum available speed is 25.
        """
        self._set_float("setMaxSpeed", max_speed)


    # def getTargetPistonHeight(self, pistonLocation:Piston) -> float:
    #     """get the target height for the selected piston (in meters)
    #     """
    #     if pistonLocation == ConveyorBelt.Piston.Front:
    #         return self.__get_float__("TargetFrontPistonHeight")
    #     elif pistonLocation == ConveyorBelt.Piston.Back:
    #         return self.__get_float__("TargetBackPistonHeight")
    #     raise Exception("invalid piston location selected")
    # def getCurrentPistonHeight(self, pistonLocation:Piston) -> float:
    #     """set the current height for the selected piston (in meters)
    #     """
    #     if pistonLocation == ConveyorBelt.Piston.Front:
    #         return self.__get_float__("CurrentFrontPistonHeight")
    #     elif pistonLocation == ConveyorBelt.Piston.Back:
    #         return self.__get_float__("CurrentBackPistonHeight")
    #     raise Exception("invalid piston location selected")
    # def setTargetPistonHeight(self, pistonLocation:Piston, height:float):
    #     """set the target height for the selected piston to [0,2] (in meters)
    #     """
    #     if pistonLocation == ConveyorBelt.Piston.Front:
    #         self.__set_float__("TargetFrontPistonHeight",height)
    #     elif pistonLocation == ConveyorBelt.Piston.Back:
    #         self.__set_float__("TargetBackPistonHeight",height)
    #     else:
    #         raise Exception("invalid piston location selected")


class LargeConveyorBelt(EntityBaseStub["LargeConveyorBelt"], ConveyorBelt):
    """large conveyor belt. same functions as the regular conveyor belt."""

    pass


class TurnableConveyorBelt(EntityBaseStub["TurnableConveyorBelt"], ConveyorBelt):
    """Conveyor Belt with variable belt speed for transporting objects that can be turned around its central axis."""

    # def getCurrentRotation(self) -> float:
    #     """Get the current rotation in [-180°,180°]"""
    #     return self.__get_float__("BeltRotationCurrentFloat")
    def set_target_rotation(self, rot: float):
        """Set the rotation angle of the conveyor belt from -180° to 180°

        Args:
            rot (float): Rotation angle in the range [-180,180]

        Example:
            >>>
            turnconv = TurnableConveyorBelt.first()
            #turn 90 degree clockwise
            turnconv.set_target_rotation(90)
        """
        self._set_float("setTargetRotation", _parse_vector(rot)[0])


class MovablePlatform(EntityBase["MovablePlatform"]):
    """Slow moving platform that can position and rotate itself within its boundaries. All attached objects on top of it will move along."""
    
    def editor_set_location_limits(self, box_limits:Vector3, *args:float):
        """[Level Editor only] Set the depth, width and height limits (in meters) along the three axes within wich the platform can be moved. The z-dimension (height) is from 0 to the specified value, the other axes from -value to +value.
        """
        self._set_vector3d("setLocationLimits", box_limits, add_args=args)

    def editor_set_rotation_limits(self, rot_limits:Rotator3, *args:float):
        """[Level Editor only] Set the half-rotation limits (roll, pitch, yaw) for the platform in degrees, meaning rotation for each component will be possible within -value to +value.
        """
        self._set_vector3d("setRotationLimits", rot_limits, add_args=args)

    def editor_set_block_collisions(self, is_enabled:bool):
        """[Level Editor only] Enable or disable blocking collisions on movement. Default is enabled. Disabled allows clipping through walls.
        """
        self._set_bool("setBlockCollisions", is_enabled)

    def editor_set_movement_speed(self, new_speed:float):
        """[Level Editor only] Change the movement speed of the platform in [0,100].
        """
        self._set_float("setMovementSpeed", new_speed)

    def editor_set_rotation_speed(self, new_speed:float):
        """[Level Editor only] Change the rotation speed of the platform in [0,50].
        """
        self._set_float("setRotationSpeed", new_speed)

    def attach_entities(self):
        """Attach all entities currently on top of the platform.

        Example:
            >>>
            MovablePlatform.first().attach_entities()
        """
        self._set_void("AttachEntities")

    def release_entities(self):
        """Release all entities currently on top of the platform

        Example:
            >>>
            MovablePlatform.first().release_entities()
        """
        self._set_void("ReleaseEntities")

    def set_target_location(self, loc:Vector3, *args:float):
        """Set the relative target location of the platform in meters. Will be clamped to platform movement limits.

        Args:
            loc (Vector3): xyz (forward,right,up) vector with relative location (meters in local space)

        Example:
            >>>
            mover = MovablePlatform.first()
            mover.set_target_location([0.5,-0.5,0])
        """
        self._set_vector3d("setTargetLocation", loc, add_args=args)
        
    def set_target_rotation(self, new_rotation:Rotator3, *args:float):
        """Set the relative target rotation as roll, pitch, yaw of the platform in degrees. Will be clamped to platform rotation limits.

        Args:
            roll (float, optional): roll rotation angel in degrees. Defaults to 0.0.
            pitch (float, optional): pitch rotation angel in degrees. Defaults to 0.0.
            yaw (float): yaw rotation angle in degrees.

        Example:
            >>>
            mover = MovablePlatform.first()
            #rotate 40° to the right
            mover.set_target_rotation(40,0,0)
        """
        self._set_vector3d("setTargetRotation", new_rotation, add_args=args)
        

    def get_current_location(self) -> Vector3:
        """Get the current relative location of the platform in meters.

        Example:
            >>>
            mover = MovablePlatform.first()
            print(mover.get_current_location())
        """
        return self._get_vector3d("CurrentLocation")
    def get_current_rotation(self) -> Rotator3:
        """Get the current relative rotation of the platform in degrees.

        Example:
            >>>
            mover = MovablePlatform.first()
            print(mover.get_current_rotation())
        """
        return self._get_rotator3d("CurrentRotation")

    def get_is_moving(self) -> bool:
        """Check whether the platform is currently moving (True) or not (False).

        Example:
            >>>
            mover = MovablePlatform.first()
            if mover.get_is_moving():
                print("is moving!")
        """
        return self._get_bool("IsMoving")

    #editor set translation and rotation speed?

class RailConveyorBelt(EntityBaseStub["RailConveyorBelt"], ConveyorBelt):
    """Conveyor Belt with variable belt speed for transporting objects that can be moved along a railway-track."""

    def get_current_position(self) -> float:
        """Get the current position on the railway-track in meters from 0 to length of track

        Example:
            railconv = RailConveyorBelt.first()
            print(railconv.get_current_position())
        """
        return self._get_float("CurrentPosition")

    def set_target_position(self, pos: float):
        """set the target position on the railway-track in meters from 0 to length of track.

        Example:
            >>>
            railconv = RailConveyorBelt.first()
            length = railconv.get_rail_track_length()
            #move to center position
            railconv.set_target_position(0.5*length)
        """
        self._set_float("setTargetPosition", pos)

    def get_rail_track_length(self) -> float:
        """Get the total length of the track (in meters) this conveyor belongs to.

        Example:
            >>>
            railconv = RailConveyorBelt.first()
            length = railconv.get_rail_track_length()
            print(length)
            #move to center position
            railconv.set_target_position(0.5*length)
        """
        return self._get_float("RailTrackLength")

    def get_is_moving(self) -> bool:
        """True if the conveyor belt is currently moving along its railway track, else False.

        Example:
            >>>
            railconv = RailConveyorBelt.first()
            railconv.set_target_position(20.5)
            while railconv.get_is_moving():
                sleep(0.1) # wait for move to complete
            print("target location reached")
        """
        return self._get_bool("IsMoving")


class ServiceDrone(EntityBase["ServiceDrone"]):
    """Service Drone that can quickly move around. Has a low resolution camera for visual inspection and accurate laser range scanner to detect obstacles."""

    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255]). If the camera is unavailable this will return a blank image.

        Example:
            >>>
            drone = ServiceDrone.first()
            img = drone.get_camera_frame()
            #show the drone's camera footage in-game
            print(img)
        """
        return self._get_image("CameraFrame")

    def get_distance_left(self) -> float:
        """Get the value of the left distance sensor in meters. Will return 0 if distance sensor is unavailable.

        Example:
            >>>
            drone = ServiceDrone.first()
            ldist = drone.get_distance_left()
            rdist = drone.get_distance_right()
            print(f"left {ldist:.2f}m, right {rdist:.2f}m")
        """
        return self._get_float("DistanceLeft")

    def get_distance_right(self) -> float:
        """Get the value of the right distance sensor in meters. Will return 0 if distance sensor is unavailable.

        Example:
            >>>
            drone = ServiceDrone.first()
            ldist = drone.get_distance_left()
            rdist = drone.get_distance_right()
            print(f"left {ldist:.2f}m, right {rdist:.2f}m")
        """
        return self._get_float("DistanceRight")

    # def setLightIntensity(self, intensity:float):
    #     """set the intensity of the drones front light.

    #     Args:
    #         intensity (float): intensity in range [0,50000] lumen
    #     """
    #     self.__set_float__("setLightIntensity", float(np.clip(intensity,0,50000)))

    def set_thruster_force_right(self, force: float):
        """Set the continuous force of the right thruster to the specified value in [-200,200] Newton (kg*m/s^2) but mass is ignored. Will be applied proportionally every frame.

        Example:
            >>>
            drone = ServiceDrone.first()
            #turn left around center axis
            drone.set_thruster_force_right(100)
            drone.set_thruster_force_left(-100)
        """
        force = float(np.clip(force, -200, 200))
        self._set_float("setThrusterForceRight", force)

    def set_thruster_force_left(self, force: float):
        """Set the continuous force of the left thruster to the specified value in [-200,200] Newton (kg*m/s^2) but mass is ignored. Will be applied proportionally every frame.

        Example:
            >>>
            drone = ServiceDrone.first()
            #turn right around center axis
            drone.set_thruster_force_right(-100)
            drone.set_thruster_force_left(100)
        """
        force = float(np.clip(force, -200, 200))
        self._set_float("setThrusterForceLeft", force)

    def apply_thruster_impulse_right(self, impulse: float):
        """Apply a one-time impulse with the right thruster in [-500,500] Newton-seconds (kg*m/s) but mass is ignored. The total force applied is equal to calling set_thruster_force over a period of 1 second.

        Example:
            >>>
            drone = ServiceDrone.first()
            #do emergency break
            drone.apply_thruster_impulse_right(-200)
            drone.apply_thruster_impulse_left(-200)
        """
        impulse = float(np.clip(impulse, -500, 500))
        self._set_float("ApplyThrusterImpulseRight", impulse)

    def apply_thruster_impulse_left(self, impulse: float):
        """Apply a one-time impulse force with the left thruster in [-500,500] Newton-seconds (kg*m/s) but mass is ignored. The total force applied is equal to calling set_thruster_force over a period of 1 second.

        Example:
            >>>
            drone = ServiceDrone.first()
            #do emergency break
            drone.apply_thruster_impulse_right(-500)
            drone.apply_thruster_impulse_left(-500)
        """
        impulse = float(np.clip(impulse, -500, 500))
        self._set_float("ApplyThrusterImpulseLeft", impulse)

    def set_fov(self, fov: float):
        """Set the field-of-view of the camera to the specified angle in [20,160] degrees. Note: Depending on its configuration, the Drone's camera might be disabled.

        Example:
            >>>
            drone = ServiceDrone.first()
            #zoom in
            drone.set_fov(40)
            #zoom out
            drone.set_fov(160)
        """
        fov = float(np.clip(fov, 20, 160))
        self._set_float("SetFOV", fov)

class LaserTracer(EntityBase["LaserTracer"]):
    """Reflective laser tracer that will calculate the relative impact positions of up to 10 laser bounces.
    """

    def get_impacts(self) -> np.ndarray:
        """Return up to 10 laser bounces as relative xyz coordinates in a n x 3 matrix
        """
        return self._get_array_raw("Impacts",[0,0,0])

    def set_enabled(self, is_enabled:bool):
        """Turn the LaserTracer on or off immediately.

        Args:
            enabled (bool): True to turn the LaserTracer on or False to turn it off.

        Example:
            >>>
            LaserTracer.first().set_enabled(False)
        """
        self._set_bool("setEnabled", is_enabled)


class DeliveryContainer(EntityBase["DeliveryContainer"]):
    """DeliveryBox that takes objects inside and "sends" them off the map to wherever they should go. Yeah, it just works."""

    def get_num_inside(self) -> int:
        """Returns number of objects currently inside the delivery box.

        Example:
            >>>
            container = DeliveryContainer.first()
            is_empty = container.get_num_inside()==0
            if is_empty:
                container.open_door()
            else:
                container.close_door()
        """
        return self._get_uint8("NumInside")

    def deliver(self):
        """Delivers all objects currently inside the delivery box. Door must be closed for this to work.

        Example:
            >>>
            container = DeliveryContainer.first()
            if container.get_num_inside()>0 and container.get_is_door_closed():
                container.deliver()
        """
        self._set_void("Deliver")

    def open_door(self):
        """opens the door.

        Example:
            >>>
            container = DeliveryContainer.first()
            container.open_door() #Sesame open
        """
        self._set_void("OpenDoor")

    def close_door(self):
        """closes the door.

        Example:
            >>>
            container = DeliveryContainer.first()
            if container.get_num_inside()>0:
                container.close_door()
        """
        self._set_void("CloseDoor")

    def get_is_door_closed(self):
        """Returns True if the door is fully closed, False if not fully closed.

        Example:
            >>>
            container = DeliveryContainer.first()
            #print this container's name and door state
            print(f"{container.get_entity_name()}'s door is {'CLOSED' if container.get_is_door_closed() else 'OPEN'}")
        """

        return self._get_bool("IsDoorClosed")

    def on_delivered(self, handler:Callable[["DeliveryContainer",float, BaseEventData],None]):
        """Event called when one or more objects inside the delivery are successfully delivered.

        Args:
            handler (Callable[[DeliveryContainer,float, BaseEventData],None]): Event handler function that takes sender, simtime, BaseEventData as arguments.
        """
        def wrapper(sender:DeliveryContainer, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            dat = None
            try:
                js = json.loads(raw)
                dat = BaseEventData(js)
            except:
                pass
            if dat is not None:
                handler(sender,gametime,dat)

        self._add_event_listener("_eventOnDelivered",wrapper)

    def editor_set_can_deliver_non_physics(self, is_enabled:bool):
        """[Level Editor Only] Enable or disable the possibility to deliver non physically simulated objects. Careful not to overlap anything that you do not want delivered / destroyed.
        """
        self._set_bool("setCanDeliverNonPhysics", is_enabled)


class ObjectSpawner(EntityBase["ObjectSpawner"]):
    """Spawns objects into the SimEnv. Behavior depends on SimEnv setup."""

    def spawn(self):
        """Try to spawn the next object. Only works if this spawner is not automated and not busy."""
        self._set_void("Spawn")


class SmartDoor(EntityBase["SmartDoor"]):
    """Remote controllable door that can be opened and closed programmatically."""

    def open(self):
        """Open the door."""
        self._set_void("Open")

    def close(self):
        """Close the door."""
        self._set_void("Close")

    def get_is_closed(self):
        """Returns True if the door is fully closed, else False."""
        return self._get_bool("IsClosed")

class SmartBlinds(EntityBase["SmartBlinds"]):
    """Remote controllable blinds / shutters that can be opened and closed programmatically."""

    def open(self):
        """Open the blinds."""
        self._set_void("Open")

    def close(self):
        """Close the blinds."""
        self._set_void("Close")

    def get_is_closed(self):
        """Returns True if the blinds are fully closed, else False."""
        return self._get_bool("IsClosed")

class RailwayBarrier(EntityBase["RailwayBarrier"]):
    """Remote controllable barrier that can be opened and closed programmatically."""

    def open(self):
        """Open the barrier."""
        self._set_void("Open")

    def close(self):
        """Close the barrier."""
        self._set_void("Close")

    def get_is_closed(self):
        """Returns True if the barrier is fully closed, else False."""
        return self._get_bool("IsClosed")

class RangeFinder(EntityBase["RangeFinder"]):
    """Multi-purpose laser range finder sensor that measures distances in meters, read RFID tags and more."""

    def get_distance(self) -> float:
        """Returns distance (in meters) as measured by this range finder. returns max distance if nothing was found.

        Example:
            >>>
            scanner = RangeFinder.first()
            print(scanner.get_distance())
        """
        distance = self._get_float("Distance")
        return distance

    def get_rfid_tag(self) -> str:
        """Returns the RFID tag of the entity currently hit by this range finder. Returns empty string if nothing is hit or target has no RFID tag.

        Example:
            >>>
            scanner = RangeFinder.first()
            tag = scanner.get_rfid_tag()
            if tag == "Box":
                print("It's box!")
            elif tag: #if tag is not empty
                print("it is a " + tag)
        """
        return self._get_string("RfidTag")

    def get_entity_type(self) -> str:
        """Returns the typename of the entity currently hit by this range finder. Returns empty string if nothing is hit or target type cannot be inferred or this range finder does not have this kind of sensor.

        Example:
            >>>
            print(RangeFinder.first().get_entity_type())
        """
        return self._get_string("EntityType")
    def get_entity_name(self) -> str:
        """Returns the unique name of the entity currently hit by this range finder. Returns empty string if nothing is hit or target has no name or this range finder does not have this kind of sensor.

        Example:
            >>>
            print(RangeFinder.first().get_entity_name())
        """
        return self._get_string("EntityName")
    def get_size(self) -> Vector3:
        """Get the size of the target entity currently hit by this range finder. Returns zero if nothing is hit or this range finder does not have this kind of sensor.

        Example:
            >>>
            print(RangeFinder.first().get_size())
        """
        return self._get_vector3d("Size")
    def get_speed(self) -> float:
        """Get the current speed (in m/s) of the target entity currently hit by this range finder. Returns zero if nothing is hit, the target cannot move or this range finder does not have this kind of sensor.

        Example:
            >>>
            print(RangeFinder.first().get_speed())
        """
        return self._get_float("Speed")

    def get_mass(self) -> float:
        """Get the mass (in kg) of the target entity currently hit by this range finder. Returns zero if nothing is hit, the target does not have a mass or this range finder does not have this kind of sensor.

        Example:
            >>>
            print(RangeFinder.first().get_mass())
        """
        return self._get_float("Mass")

    def set_rfid_tag(self, rfid_tag:str):
        """Write an RFID tag to the entity currently hit by this range finder. Replaces any other rfid tag.

        Args:
            rfid_tag (str): the new tag to set

        Example:
            >>>
            rf = RangeFinder.first()
            if rf.Distance < 5:
                rf.set_rfid_tag("A")
        """
        self._set_string("setRfidTag", rfid_tag)

    def get_feature_data(self) -> dict[str, Any]:
        """Get any other features of the currently hit entity. Mostly used in machine learning levels.

        Example:
            >>>
            rf = RangeFinder.first()
            x = rf.get_feature_data()
            print(x)
        """
        return self._get_json("FeatureData")


    def editor_set_can_read_rfid_tags(self, enabled:bool):
        """[Level Editor only] Enable or disable the rfid reader on this device."""
        self._set_bool("setCanReadRfidTags", enabled)
    def editor_set_can_write_rfid_tags(self, enabled:bool):
        """[Level Editor only] Enable or disable the rfid writer on this device."""
        self._set_bool("setCanWriteRfidTags", enabled)
    def editor_set_can_read_entities(self, enabled:bool):
        """[Level Editor only] Enable or disable the entity reader on this device that can read type and name of most entities."""
        self._set_bool("setCanReadEntities", enabled)
    def editor_set_can_read_physics(self, enabled:bool):
        """[Level Editor only] Enable or disable the physics reader on this device that can read speed, mass and size of most entities."""
        self._set_bool("setCanReadPhysics", enabled)
    def editor_set_can_read_feature_data(self, enabled:bool):
        """[Level Editor only] Enable or disable feature data reader on this device."""
        self._set_bool("setCanReadFeatureData", enabled)
    def editor_set_max_range(self, max_range:float):
        """[Level Editor only] Set the max distance for the scanning range."""
        self._set_float("setMaxRange", max_range)
       


class SmartPictureFrame(EntityBase["SmartPictureFrame"]):
    """Picture display that can dynamically change its content."""

    def set_image_by_name(self, img_name: str):
        """sets the image to the specified image name."""
        self._set_string("SetImgByName", img_name)

    def set_image_by_bytes(self, img_bytes: np.ndarray):
        """sets the image to the specified image array"""
        k = self._build_name("SetImgByBytes")
        nparr = NPArray(k, img_bytes)
        self._set_out_data(k, nparr)
        self._post_API_call()


class PaintableCanvas(EntityBase["PaintableCanvas"]):
    """A 2D canvas that can be painted on"""

    def set_brush_color(self, color:Colors = Colors.Black):
        """Set the desired brush color"""
        self._set_vector3d("setBrushColor", _parse_color(color))

    def set_brush_size(self, radius:float):
        """Set the size of the brush. Set to 0 for invisible brush strokes.
        """
        self._set_float("setBrushSize", radius)

    def set_brush_location(self, target_location:Vector3, *args:float):
        """Set the desired target position of the brush. It will move to the new position automatically and paint a brush stroke along the way.  Set brush size to 0 to move without painting. Z coordinate is ignored."""
        self._set_vector3d("setBrushLocation", target_location, add_args=args)

class CarvingRobot(EntityBase["CarvingRobot"]):
    """ A rotating carving robot that can carve away material from a rotating cylinder"""

    def set_speed(self, target_speed:float):
        """Set the target rotating speed of the base. """
        self._set_float("SetSpeed", target_speed)

    def set_chisel(self, vertical_positon:float, depth_position:float, chisel_size:float = 0.1):
        """Set the target chisel position (vertical along the cylinder and depth into the cylinder) and chisel size. All values are relative in [0,1]."""
        self._set_vector3d("SetChisel", [vertical_positon,depth_position,chisel_size])
        #should work with boolean intersect https://docs.unrealengine.com/5.0/en-US/geometry-script-reference-in-unreal-engine/





    
class SimEnvManager(EntityBase["SimEnvManager"]):
    """Manage the current SimEnv with this class."""

    def reset(self, stop_code=False, await_reset=True):
        """Resets the current SimEnv to its initial state at time=0.

        Args:
            stop_code (bool, optional): Stop all python code. Defaults to False.
            await_reset (bool, optional): Wait until reset has been fully completed. Takes about 1 second. Set to false to continue immediately if you do not need to wait.

        Example:
            >>>
            SimEnvManager.first().reset()
        """
        if await_reset:
            sleep()
        t = self.get_sim_time()
        if stop_code:
            self._set_void("ResetSimEnv")
        else:
            self._set_void("ResetSimEnvNoStop")
            if not await_reset:
                return
            #  wait for next update loop
            for i in range(200):
                time.sleep(0.01)
                t2 = self.get_sim_time()
                if t2 >= 0 and (t2 < 2 or t2 < t):
                    break
            # wait for on_reset handler
            sleep()
            time.sleep(0.05)
            sleep()

    def get_sim_time(self) -> float:
        """Returns time in seconds that the current SimEnv has been running for (since last reset).

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_sim_time())
        """
        return self._get_float("SimTime")

    # @property
    # def sim_name(self) -> str:
    #     """Get the name of the currently active simenv
    #     """
    #     return self._get_string("SimName")

    # def get_time_remaining(self) -> float:
    #     """Returns time in seconds that is remaining to stay within the optional time-limit of the current SimEnv.

    #     Example:
    #         >>>
    #         lvl = SimEnvManager.first()
    #         print(lvl.get_time_remaining())
    #     """
    #     return self._get_float("TimeRemaining")

    def get_is_completed(self) -> bool:
        """True if all goals of the current SimEnv have been completed.

        Example:
            >>>
            lvl = SimEnvManager.first()
            if lvl.get_is_completed():
                print("done")
                SimEnv.disconnect()
        """
        return self._get_bool("IsCompleted")

    def get_completion_progress(self) -> float:
        """Returns the current completion percentage for all goals of this SimEnv.

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_completion_progress())
        """
        return self._get_float("CompletionProgress")

    def set_time_dilation(self, dilation: float):
        """slow-down or speed-up the simulation speed of the SimEnv. [0.05,5], values < 1 are slow-motion.

        Example:
            >>>
            #pause the game via Python
            lvl = SimEnvManager.first()
            lvl.set_time_dilation(0.05)
            sleep(1) # sleep 1 in-game second. since we paused (or actually slowed down to 0.05 = 1/20th this will take 20 real-time seconds)
            lvl.set_time_dilation(1) # resume normal speed
        """
        self._set_float("setTimeDilation", dilation)

    def get_time_dilation(self) -> float:
        """Returns the current simulation speed of the SimEnv.

        Example:
            >>>
            lvl = SimEnvManager.first()
            #prevent speed changes in-game
            if lvl.get_time_dilation() != 1:
                lvl.set_time_dilation(1)
        """
        val = self._get_float("TimeDilation")
        if val <= 0.00001:
            val = 0.00001
        return val

    def query_input(self, prompt: str):
        """Show a modal input dialog in the SimEnv and allow the user to enter some text value. Asynchronous, does not wait for the user to enter something. Recommended to use "input" command instead for synchronous querying.

        Args:
            prompt (str): The prompt to display to the user.

        Example:
            >>>
            lvl = SimEnvManager.first()
            lvl.query_input("What's 1+2?")
            sleep(10)
            res = lvl.get_last_input_response()
            if res.isnumeric() and int(res)==3:
                print("correct, 1+2 = 3)
            else:
                print("wrong")

        """
        self._set_string("QueryInput", prompt)

    def get_last_input_response(self) -> str:
        """Returns the response the user entered to the last query input. Recommended to use "input" command instead for synchronous querying.

        Example:
            >>>
            lvl = SimEnvManager.first()
            lvl.query_input("What's 1+2?")
            sleep(10)
            res = lvl.get_last_input_response()
            if res.isnumeric() and int(res)==3:
                print("correct, 1+2 = 3)
            else:
                print("wrong")
        """
        js = self._get_json("InputResponse")
        if "res" in js:
            return js["res"]
        return ""

    def quit_game(self, do_you_really_want_to_quit: bool):
        """Immediately quit the game and exit to the desktop.

        Args:
            do_you_really_want_to_quit (bool): Must confirm with True

        Example:
            >>>
            # much sad :(
            SimEnvManager.first().quit_game(True)
        """
        if do_you_really_want_to_quit == True:
            self._set_void("QuitGame")

    def set_verbosity_level(self, verbosity:VerbosityLevels):
        """Set the verbosity level of the pyjop interface. Higher values mean more verbose information.

        Args:
            verbosity (VerbosityLevels): 0 (Only Errors) to 3 (Debug, everything)
        """
        self._set_int("setVerbosityLevel", int(verbosity))

    def draw_debug_line(
        self,
        start: Vector3,
        end: Vector3,
        color: Colors = Colors.Red,
        thickness: float = 2.0,
        lifetime: float = 1.0,
        foreground: bool = False
    ):
        """Draw a single line for debugging purposes into the world.

        Args:
            start (Vector3): Start location in world space (in meters)
            end (Vector3): End location in world space (in meters)
            color (Colors, optional): Defaults to Colors.Red.
            thickness (float, optional): Defaults to 2.0 cm.
            lifetime (float, optional): Defaults to 1.0 seconds.
            foreground (bool, optional): True to draw on top of everything, False for normal depth occlusion.
        """
        self._set_json(
            "DrawDebugLine",
            {
                "Start": _parse_vector(start, True),
                "End": _parse_vector(end, True),
                "Color": _parse_color(color, True),
                "Thickness": float(thickness),
                "Lifetime": float(lifetime),
                "bForeground": bool(foreground)
            },
        )

    def draw_throw_prediction(
        self,
        start: Vector3,
        velocity: Vector3,
        radius: float = 0.05,
        color: Colors = Colors.Red,
        thickness: float = 2.0,
        lifetime: float = 1.0,
        foreground: bool = False,
        max_bounces: int = -1,
        elasticity: float = 0.5
    ):
        """Draw a throw prediction arc for debugging purposes into the world. Note that bounce prediction is an estimate.

        Args:
            start (Vector3): Start location in world space (in meters)
            velocity (Vector3): Velocity vector in world space (in meters / second)
            radius (float): Radius of the tracing sphere to check for collisions. Defaults to 0.05m.
            color (Colors, optional): Defaults to Colors.Red.
            thickness (float, optional): Defaults to 2.0 cm.
            lifetime (float, optional): Defaults to 1.0 seconds.
            foreground (bool, optional): True to draw on top of everything, False for normal depth occlusion.
            max_bounces (int, optional): Number of bounces the throw should be traced for.
            elasticity (float, optional): Assumed elasticity of each bounce in [0.01,0.99].
        """
        self._set_json(
            "DrawThrowPrediction",
            {
                "Start": _parse_vector(start, True),
                "Velocity": _parse_vector(velocity, True),
                "Radius": float(radius),
                "Color": _parse_color(color, True),
                "DrawThickness": thickness,
                "Lifetime": float(lifetime),
                "bForeground": bool(foreground),
                "MaxBounces": int(max_bounces),
                "Elasticity": float(elasticity)
            },
        )



    


def sleep(seconds: float = 0, ignore_time_dilation = False):
    """Delay execution for a given number of seconds. Is automatically scaled with SimEnv time dilation, unless you specify ignore_time_dilation=True.

    Example:
        >>>
        sleep(1.5) #sleeps for 1.5 SimEnv seconds
        sleep() #sleep until next simulation round trip tick
    """
    start = time.time()
    m = SimEnvManager.first()
    start_sim = m.get_sim_time()
    await_receive()
    _dispatch_events()
    if seconds is None or seconds <= 0.1:
        return
    
    if ignore_time_dilation:
        elapsed = time.time() - start
        if elapsed < seconds:
            time.sleep(seconds - elapsed)
        return

    if _is_custom_level_runner():
        while time.time() - start < seconds:
            time.sleep(0.03)
            _dispatch_events()
            if seconds > 0.19 and _stack_size() < 50:
                editor = LevelEditor.first()
                editor._check_goals()
                editor._run_dynamics()
        return

    if m.get_time_dilation() > 2:
        seconds = seconds-0.149 #offset
    elif m.get_time_dilation() > 0.9:
        seconds = seconds-0.099 #offset
            
   
    if start_sim < 0:
        start_sim = m.get_sim_time()
    while True:
        time.sleep(0.03)
        _dispatch_events()
        dtime = m.get_sim_time() - start_sim
        if dtime < 0:#reset fix
            start_sim = m.get_sim_time()
        if dtime >= seconds:
            break
            


import builtins


def print_all_entities():
    """Prints a list of all programmable entities currently in the SimEnv.

    Example:
        >>>
        print_all_entities() #literally print all entities
    """
    entities = EntityBase.find_all(True)
    print(f"found {len(entities)} entities")
    for entity in entities:
        print(entity._build_name())


def print(*args, col: Colors = Colors.White, log_level = VerbosityLevels.Important) -> None:
    """print the supplied message to the in-game log. Duplicate print messages directly after one another are ignored. Can also print images directly in-game. Takes optional color for the print message.


    Args:
        col (Colors, optional): RGB color or css color name of the print message. Defaults to white (1.0,1.0,1.0).
        log_level (VerbosityLevels, optional): The verbosity  level of this message. If log_level is below the configured verbosity level (Info=2 as default), it will not be printed.

    Example:
        >>>
        print("hello world")
        print("this is red", col = Colors.Red)
        #print(some_img_variable)
    """
    if len(args) == 1 and type(args[0]) == np.ndarray and len(args[0].shape) > 1:
        EntityBase._log_img_static(args[0])
        return
    if len(args) > 0:
        msg = " ".join(map(str, args))
        EntityBase._log_debug_static(msg, col=_parse_color(col), log_level=log_level)
        return builtins.print(*args)


def input(prompt="") -> str:
    """Show a modal input dialog in the SimEnv and allow the user to enter some text value. Synchronous, meaning calling this stops Python executing until the user entered and submitted a response.

    Args:
        prompt (str, optional): The prompt to display to the user. Defaults to "".

    Example:
        >>>
        name = input("What's your name?")
        print(f"Hello {name}! How are you?")
    """
    m = SimEnvManager.first()
    old_res = m._get_json("InputResponse")  # res and ts (real time)
    # m.set_time_dilation(0.05)
    m.query_input(prompt)
    while True:
        time.sleep(0.1)
        _dispatch_events()
        res = m._get_json("InputResponse")
        if res and res != old_res:
            # m.set_time_dilation(old_dilation)
            return res["res"]


def show_nicegui(title="My Nice GUI", width=800, height=600):
    """Show and load the current nicegui window. Blocking operation.

    Args:
        title (str): Title of the GUI window. Defaults to "My Nice GUI".
        width (int, optional): Width of the window in pixels. Defaults to 800.
        height (int, optional): Height of the window in pixels. Defaults to 600.

    Example:
        >>>
        from pyjop import *
        from nicegui import ui

        SimEnv.connect()

        #create gui
        ui.button('Hello', on_click=lambda: ui.notify("hello there!"))

        show_nicegui() #script blocks here
    """

    # nicegui running, show / refresh window
    m = SimEnvManager.first()
    m._set_json("ShowNiceGUI", {"Title": title, "SizeX": width, "SizeY": height})
    # TODO handle events on thread here or somehow open uvicorn asyncio.run loop here, or run nicegui on a thread https://stackoverflow.com/questions/62703083/is-it-possible-to-run-multiple-asyncio-in-the-same-time-in-python
    from nicegui import ui
    
    #workaround to get joy event dispatcher into nicegui main loop
    def upd(x):
        _dispatch_events()
        return '<div style="display: none">a<div>'
    bla = ui.html('<div style="display: none">a<div>')
    bla.bind_content_from(EntityBase,"last_receive_at",backward= upd)
    print("If nicegui does not show and you receive an error, please go the Pause Menu -> Options -> Game and click 'Fix NiceGUI'.", col=Colors.Yellow, log_level=VerbosityLevels.Important)
    ui.run(
        host="127.0.0.1",
        port=18085,
        show=False,
        dark=True,
        reload=False,
        viewport=f"width={width}, height={height}, initial-scale=1",
        title=title,
        uvicorn_logging_level='critical'
    )
    
    # ui.run(host="127.0.0.1",port=18085,show=False, dark=True, reload=False, viewport="width=800, height=600, initial-scale=1")


class Piano(EntityBase["Piano"]):
    """Piano sequencer you can program and automate to play piano sample sounds."""

    def play_note(self, note: MusicNotes) -> None:
        """play the specified note (from C1 to B7, with s for sharps and b for molls).

        Args:
            note (MusicNotes): Note to play as string or from MusicNotes Enum

        Example:
            >>>
            Piano.first().play_note(MusicNotes.Cs4)
        """
        self._set_string("PlayNote", str(note))

    def play_note_in_octave(self, base_note: str, octave: int) -> None:
        """play the specified note (from C to B, with s for sharps and b for flats) on the specified octave (1 to 7)

        Args:
            base_note (str): Note to play as string. Valid values [C,D,E,F,G,A,B], with suffix s or # for sharps and b for flats
            octave (int): Octave to play the note in. Valid values: [1,...,7]

        Example:
            >>>
            Piano.first().play_note_in_octave("Cs",4)
            sleep(1)
        """
        self._set_string("PlayNote", base_note + str(octave))

    def play_chord(self, chord_notes:Sequence[MusicNotes]):
        for n in chord_notes:
            self._set_string("PlayNote", str(n), True)

    # new method to choose instrument
    def set_instrument(self, new_instrument:MusicInstruments):
        """Set the instrument used by this electric piano / keyboard.

        Args:
            new_instrument (MusicInstruments): Choose from the available instruments
        """
        self._set_string("SetInstrument", str(new_instrument))


class SmartLight(EntityBase["SmartLight"]):
    """Smart light with controllable light color and intensity"""

    def set_color(self, color: Colors):
        """set the light's color to the specified RGP tuple or a css color name

        Example:
            >>>
            lights = SmartLight.find_all()
            #set color for all lights
            for l in lights:
                l.set_color((1,0,0)) #make them red
            sleep(4)
            for l in lights:
                l.set_color(Colors.Green) #make them green
        """
        self._set_vector3d("setColor", _parse_color(color))

    def set_intensity(self, intensity: float):
        """set the light's intensity to the specified value in candelas (from 0 to 50)

        Example:
            >>>
            lights = SmartLight.find_all()
            # set intensity for all lights to 50
            for l in lights:
                l.set_intensity(50) #max brightness
        """
        self._set_float("setIntensity", intensity)

    def set_enabled(self, is_enabled: bool):
        """Turn the light on or off immediately.

        Args:
            enabled (bool): True to turn the light on or False to turn it off.

        Example:
            >>>
            lights = SmartLight.find_all()
            #turn off all lights
            for l in lights:
                l.set_enabled(False)
        """
        self._set_bool("setEnabled", is_enabled)

    def toggle(self):
        """Toggle the light on or off depending on its current state.

        Example:
            >>>
            #blinking lights
            for i in range(10):
                SmartLight.first().toggle()
                sleep(1)
        """
        self._set_void("Toggle")


class SmartSpeaker(EntityBase["SmartSpeaker"]):
    """Controllable smart speaker that can play a selection of builtin songs or songs by url / filename."""

    def set_volume(self, volume: float):
        """Change the relative volume of this speaker.

        Args:
            volume (float): relative volume in [0,2]

        Example:
            >>>
            speaker = SmartSpeaker.first()
            #louder
            speaker.set_volume(1.5)
            #off
            speaker.set_volume(0)
        """
        self._set_float("setVolume", volume)

    def set_sound_by_name(self, name: BuiltinMusic):
        """Play one of builtin songs / playlists that come with this speaker.

        Args:
            name (str): name of the builtin song. Must be one of the names returned by get_builtin_sounds.

        Example:
            >>>
            speaker = SmartSpeaker.first()
            speaker.set_sound_by_name("Joy's Playlist")
        """
        if name:
            self._set_string("setSoundByName", str(name))


    def set_sound_by_url(self, url: str):
        """Play a local sound file (mp3, wav, ogg supported) or a sound file on a http server.

        Args:
            url: local file or http url. mp3, wav, ogg supported.

        Example:
            >>>
            s = SmartSpeaker.first()
            s.set_sound_by_url("https://www.kozco.com/tech/piano2-CoolEdit.mp3")
        """
        return self._set_string("setSoundByUrl", url)

    #def set_sound_by_bytes(self, wave_data:bytearray)


class SmartTracker(EntityBase["SmartTracker"]):
    """Tracker which you can query for its GPS location, velocity, acceleration and mass. Available data and noise levels differ by tracker model."""

    def get_location(self) -> Vector3:
        """Get tracker's location in XYZ (in world space meters).

        Example:
            >>>
            tracker = SmartTracker.first()
            loc = tracker.get_location()
            print(loc)
        """
        return self._get_vector3d("Location")

    def get_rotation(self) -> Rotator3:
        """Get tracker's rotation in roll,pitch,yaw in degrees in world space.

        Example:
            >>>
            tracker = SmartTracker.first()
            rot = tracker.get_rotation()
            print(rot)
        """
        return self._get_rotator3d("Rotation")

    def get_linear_velocity(self) -> Vector3:
        """Get tracker's velocity vector in XYZ in meters per second in world space.

        Example:
            >>>
            tracker = SmartTracker.first()
            vel = tracker.get_linear_velocity()
            print(vel.length) # print total speed in m/s
        """
        return self._get_vector3d("LinearVelocity")

    def get_angular_velocity(self) -> Vector3:
        """Get tracker's angular velocity  in roll,pitch,yaw in degrees per second in world space.

        Example:
            >>>
            tracker = SmartTracker.first()
            vel_deg = tracker.get_angular_velocity()
            print(vel_deg)
        """
        return self._get_vector3d("AngularVelocity")

    def get_linear_acceleration(self) -> Vector3:
        """Get tracker's acceleration vector in XYZ in meters per second squared in world space.

        Example:
            >>>
            tracker = SmartTracker.first()
            acc = tracker.get_linear_acceleration()
            print(acc)
        """
        return self._get_vector3d("LinearAcceleration")

    def get_angular_acceleration(self) -> Vector3:
        """Get tracker's angular acceleration  in roll,pitch,yaw in degrees per second squared in world space.

        Example:
            >>>
            tracker = SmartTracker.first()
            acc_deg = tracker.get_angular_acceleration()
            print(acc_deg)
        """
        return self._get_vector3d("AngularAcceleration")

    def get_mass(self) -> float:
        """Get the mass (in kg) of the whole entity the tracker is attached to.

        Example:
            >>>
            tracker = SmartTracker.first()
            m = tracker.get_mass()
            print(m)
        """
        return self._get_float("Mass")


    def editor_set_sensor_noise_level(self, new_noise:float):
        """Set the standard deviation of the gaussian noise added to the smart tracker's sensor readings.

        Args:
            new_noise (float): standard deviation of the gaussian noise
        """
        self._set_float("setSensorNoiseLevel", new_noise)

    def editor_set_available_sensors(self, location:Optional[bool] = None, rotation:Optional[bool] = None, linear_velocity:Optional[bool] = None, angular_velocity:Optional[bool] = None, linear_acceleration:Optional[bool] = None, angular_acceleration:Optional[bool] = None, mass:Optional[bool] = None):
        """[Level Editor Only] Specify what kind of sensors this smart tracker has.

        Args:
            location (Optional[bool], optional): _description_. Defaults to None.
            rotation (Optional[bool], optional): _description_. Defaults to None.
            linear_velocity (Optional[bool], optional): _description_. Defaults to None.
            angular_velocity (Optional[bool], optional): _description_. Defaults to None.
            linear_acceleration (Optional[bool], optional): _description_. Defaults to None.
            angular_acceleration (Optional[bool], optional): _description_. Defaults to None.
            mass (Optional[bool], optional): _description_. Defaults to None.
        """
        sensors:dict[str,bool] = {}
        if location is not None:
            sensors["location"] = location
        if rotation is not None:
            sensors["rotation"] = rotation
        if mass is not None:
            sensors["mass"] = mass
        if linear_velocity is not None:
            sensors["linearVelocity"] = linear_velocity
        if angular_velocity is not None:
            sensors["angularVelocity"] = angular_velocity
        if linear_acceleration is not None:
            sensors["linearAcceleration"] = linear_acceleration
        if angular_acceleration is not None:
            sensors["angularAcceleration"] = angular_acceleration
        if sensors:
            self._set_json("SetAvailableSensors", sensors)

class GPSWaypoint(EntityBase["GPSWaypoint"]):
    """GPS waypoint beacon that you can query for its precise location.
    """
    def get_location(self) -> Vector3:
        """Get this waypoints GPS location in XYZ (world space in meters).

        Example:
            >>>
            gps = GPSWaypoint.first()
            loc = gps.get_location()
            print(loc)
        """
        return self._get_vector3d("Location")
    
class FactBox(EntityBase["FactBox"]):
    """A small lootbox containing a collectible factsheet. Find it and collect all the factsheets!"""

    def get_distance_to_player(self) -> float:
        """Returns the distance from the player's current position to the FactBox in meters (rounded).

        Example:
            >>>
            box = FactBox.first()
            #check if there is a box
            if box:
                print(box.get_distance_to_player())
        """
        return self._get_float("DistanceToPlayer")

    def focus(self):
        """Just focusing the lootbox? Now that would be cheating wouldn't it? Try get_distance_to_player() instead"""
        print(
            "Just focusing the lootbox? Now that would be cheating wouldn't it? Try get_distance_to_player() instead.",
            Colors.Yellow,
        )


class DetectionData(BaseEventData):
    def __init__(self, new_vals: dict[str, Any]):
        super().__init__(new_vals)
        """Object detection data returned by a SmartCamera"""
        
        self.img_left: float = new_vals["imgLeft"]
        """The x position of the left of the bounding box around the entity in image coordinates."""
        self.img_top: float = new_vals["imgTop"]
        """The y position of the top of the bounding box around the entity in image coordinates."""
        self.img_width: float = new_vals["imgWidth"]
        """The width of the bounding box around the entity in image coordinates."""
        self.img_height: float = new_vals["imgHeight"]
        """The height of the bounding box around the entity in image coordinates."""
        self.real_distance: float = new_vals["realDistance"]
        """The distance to the detected object in meters."""
        self.real_width: float = new_vals["realWidth"]
        """The actual width of the objects in meters."""
        self.real_height: float = new_vals["realHeight"]
        """The actual height of the objects in meters."""


class SmartCamera(EntityBase["SmartCamera"]):
    """Camera with adjustable zoom that can return RGB images and optionally several other kinds of images (depends on SimEnv)."""

    def set_fov(self, fov: float):
        """Set the field-of-view (in degrees) of this camera to zoom in / out.

        Args:
            fov (float): FOV angle in degrees within [20,160]

        Example:
            >>>
            #zoom in
            SmartCamera.first().set_fov(30)
            #zoom out
            SmartCamera.first().set_fov(130)
        """
        self._set_float("SetFOV", fov)

    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array. Depending on the camera type this is either of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255]) or 256x256 for a depth camera.

        Example:
            >>>
            img = SmartCamera.first().get_camera_frame()
            #print the image size (HxWxC)
            print(img.shape)
            #print the image contents
            print(img)
            #print the image average color over all pixels
            print(img.mean(axis=(0,1)))
        """
        return self._get_image("CameraFrame")


    def get_object_detections(self):
        """Get a list of all objects (entityName, entityType, 2D bounding box) currently visible in the camera view. Not all cameras have integrated object detection.

        Example:
            >>>
            cam = SmartCamera.first()
            dects = cam.get_object_detections()
            for d in dects:
                print(f"{d.entity_type} detected at {d.real_distance}m")

        """
        return [DetectionData(d) for d in self._get_json("ObjectDetections")["items"]]

    def editor_set_camera_type(self, new_type:CameraType):
        """[Level Editor Only] Change the camera's operating type.

        Args:
            new_type (CameraType): New camera type.
        """
        self._set_uint8("SetCameraType", int(new_type))

    def set_segmentation_rules(self, by_class = False, by_name = False, by_class_dict:Dict[str,int] = dict(), by_name_dict:Dict[str,int] = dict()):
        """Set the segmentation rules. Only applicable if this operates as an image segmentation camera.

        Args:
            by_class (bool): True to segment by class/type name of each entity. Default behavior.
            by_name (bool): True to segment by the unique names of each entity. Unnamed entities will be considered background.
            by_class_dict (Dict[str,int]): Supply a custom dictionary of class name and segmentation id lookups. Segmentation id must be an integer within [2,255].
            by_name_dict (Dict[str,int]): Supply a custom dictionary of entity name and segmentation id lookups. Segmentation id must be an integer within [2,255].
        """
        if int(by_class) + int(by_name) + int(len(by_class_dict)>0) + int(len(by_name_dict)>0) != 1:
            raise JoyfulException("You must specificy exactly one of the four parameters.")

        segment_by = {
            "bClass":by_class,
            "bName":by_name,
            "ClassDict":by_class_dict,
            "NameDict":by_name_dict
        }
        self._set_json("SetSegmentationRules", segment_by)

class AirSupplyDrop(EntityBase["AirSupplyDrop"]):
    """An aerial based supply drop that can be called in."""
    
    def drop_supplies(self, target_location:Vector3, *args:float):
        """Drop a supply crate at the specified location. Target location is not guaranteed.

        Args:
            target_location (Vector3): Desired target location for the drop. Z coordinate is ignored. Location is not guaranteed.
        """
        self._set_vector3d("DropSupplies", target_location, add_args=args)

    def get_supplies_left(self) -> int:
        """Get the number of remaining supply drops."""
        return self._get_int("SuppliesLeft")

    def editor_set_supplies_left(self, new_supplies:int):
        """[Level Editor Only] Change the number of remaing supply drops.

        Args:
            new_supplies (int): new number of available drops
        """
        self._set_int("SetSuppliesLeft", new_supplies)

    def editor_set_drop_randomization(self, uniform_range:Vector3, *args:float):
        """Add the specified uniform random vector to each supply drop location the player specifies.

        Args:
            uniform_range (Vector3): A uniform random vector will be drawn from this range center around 0, Z is ignored so a (1,2,0) range would add a random vector between (-0.5, -1, 0) and (0.5, 1, 0) to the target drop location the player specifies.
        """
        self._set_vector3d("SetDropRandomization", uniform_range, add_args=args )

        


class Crate(EntityBase["Crate"]):
    """A crate that can be opened. Contents and consequences of opening a crate differ from crate to crate and depend on the current level."""
    def open(self):
        """Open this crate. Contents and consequences of opening a crate differ from crate to crate and depend on the current level."""
        self._set_void("Open")
           

class RobotArm(EntityBase["RobotArm"]):
    """Programmable robot arm with inverse kinematics control and a strong grabber to move items around."""

    def set_grabber_location(self, vec: Vector3, *args:float):
        """Set the relative location of the grabber endpoint (XYZ in meters).

        Args:
            vec (Vector3): relative XYZ location (forwards-right-up) in meters within [-2.5,2.5],[-2.5,2.5],[0,4]

        Example:
            >>>
            arm = RobotArm.first()
            #arms up
            arm.set_grabber_location([0,0,4])
        """
        self._set_vector3d("setGrabberLocation", vec, add_args=args)

    def get_is_grabbing(self) -> bool:
        """True if the grabber is currently grabbing something successfully, else False.

        Example:
            >>>
            arm = RobotArm.first()
            arm.pickup()
            sleep(1)
            if arm.get_is_grabbing():
                arm.release()
        """
        
        return self._get_bool("IsGrabbing")

    def get_is_moving(self) -> bool:
        """True if the arm is currently moving towards a target location, else False.

        Example:
            >>>
            arm = RobotArm.first()
            arm.set_grabber_location([0,0,4])
            while arm.get_is_moving():
                sleep(0.1) # wait for move to complete
            print("target location reached")
        """
        return self._get_bool("IsMoving")

    def pickup(self):
        """Pickup an object within range of the grabber endpoint.


        Example:
            >>>
            arm = RobotArm.first()
            arm.pickup()
            sleep(1)
            if arm.get_is_grabbing():
                arm.release()
        """
        self._set_void("Pickup")

    def release(self):
        """Release any grabbed objects.


        Example:
            >>>
            arm = RobotArm.first()
            arm.pickup()
            sleep(1)
            if arm.get_is_grabbing():
                arm.release()
        """
        self._set_void("Release")

    def editor_set_size_limit(self, max_size:float):
        """[Level Editor Only] Set the maximum size of objects this airlift can carry. Diameter in meters.

        Args:
            intensity (float): Diameter in meters. Defaults to 2m.
        """
        self._set_float("setSizeLimit", max_size)

    def editor_set_can_carry_non_physics(self, is_enabled:bool):
        """[Level Editor Only] Enable or disable the possibility to carry around non physically simulated objects. Careful, this means the player can lift up anything.
        """
        self._set_bool("setCanCarryNonPhysics", is_enabled)

    def editor_set_block_collisions(self, is_enabled:bool):
        """[Level Editor only] Enable or disable blocking collisions on movement. Default is enabled. Disabled allows clipping through walls.
        """
        self._set_bool("setBlockCollisions", is_enabled)

    def editor_set_carry_collisions(self, is_enabled:bool):
        """[Level Editor only] Enable or disable blocking collisions on movement for the carried object. Default is disabled. Disabled allows clipping of the carried object through walls.
        """
        self._set_bool("setCarryCollisions", is_enabled)

    



class TeleportEvent(BaseEventData):
    def __init__(self, new_vals: dict[str, Any]):
        super().__init__(new_vals)
        
        self.receiver:SmartPortal = SmartPortal.find(new_vals["receiver"])
        """Receiver portal where the teleported entity exited from."""



class SmartPortal(EntityBase["SmartPortal"]):
    """A portal that will teleport any entity that enters to another portal with the same channel_id. If more than two portals with the same channel_id exist a random one will be selected for each teleport."""

    def editor_set_channel(self, channel_id: int = 0):
        """[Level Editor Only] Set the channel this portal is operating on. Must be within [0...10]. Will teleport any entity that enters to another portal with the same channel_id. If more than two portals with the same channel_id exist a random one will be selected for each teleport.

        Args:
            channel_id (int, optional): Defaults to channel 0.
        """
        self._set_int("setChannel", clamp(channel_id, 0, 10))

    def on_teleport(self, handler:Callable[["SmartPortal",float, TeleportEvent],None]):
        """Event called when something enters / overlaps or exits this zone. 

        Args:
            handler (Callable[[SmartPortal,float, TeleportEvent],None]): Event handler function that takes sender, simtime, TeleportEvent data as arguments.

        Example:
            >>>
            portal = SmartPortal.first()

            def teleport_handler(sender, simtime, data):
                print(f"teleported {data.entity_name}")
                    
            portal.on_teleport(teleport_handler)
                    
            while SimEnv.run_main():
                pass
        """
        import json
        def wrapper(sender:SmartPortal, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            tele = None
            try:
                js = json.loads(raw)
                tele = TeleportEvent(js)
            except:
                pass
            if tele is not None:
                handler(sender,gametime,tele)
        self._add_event_listener("_eventOnTeleport",wrapper)


class Killzone(EntityBase["Killzone"]):
    """A kill-zone that removes any entity that enters it / overlaps it."""

    def get_kill_count(self):
        """Get the number of entities that were removed by this kill-zone.

        Example:
            >>>
            count = Killzone.first().get_kill_count()
            print(count)
        """
        return self._get_int("KillCount")

    def set_filter_tags(self, rfid_tags: Sequence[str]|str):
        """Filter entities that enter the kill-zone and remove only those that contain one of the specified rfid tags. Tags are case-sensitive.
        
        Args:
            rfid_tags (Sequence[str]): list of rfid tags

        Example:
            >>>
            zone = Killzone.first()
            zone.set_filter_tags(["Box","Barrel"])
        """
        if type(rfid_tags) is not str:
            rfid_tags = ",".join([str(t) for t in rfid_tags])
        self._set_string("setFilterTags", rfid_tags)

    def set_autokill_enabled(self, is_enabled:bool):
        """Enable or disable automatic removal of objects on overlap. If disabled, you need to manually call "kill()" to trigger removal of all overlapping objects.

        Args:
            is_enabled (bool): True to automatically remove all objects on begin overlap (default behavior). If disabled, you need to manually call "kill()" to trigger removal of all overlapping objects.

        Example:
            >>>
            Killzone.first().set_autokill_enabled(False)
            sleep(2) #wait for objects to arrive
            Killzone.first().kill() #remove them
        """
        self._set_bool("setAutokillEnabled", is_enabled)

    def kill(self):
        """Remove all overlapping objects in this killzone immediately.

        Example:
            >>>
            Killzone.first().set_autokill_enabled(False)
            sleep(2) #wait for objects to arrive
            Killzone.first().kill() #remove them
        """
        self._set_void("Kill")

    def editor_allow_custom_filter(self, is_allowed:bool):
        """[Level Editor Only] Allow to change the custom entity filters or not. Does not reset the filter once it is set."""
        self._set_bool("AllowCustomFilter", is_allowed)

    

    def on_kill(self, handler:Callable[["Killzone",float, BaseEventData],None]):
        """Event called when something enters this kill-zone and is destroyed. 

        Args:
            handler (Callable[[KillZone,float, BaseEventData],None]): Event handler function that takes sender, simtime, BaseEventData as arguments.

        Example:
            >>>
            zone = Killzone.first()
            #define kill event handler function
            def handle_kill(s,simtime,event_dat):
                print(f"destroyed object with tag {event_dat.rfid_tag}")

            #register event handler
            zone.on_kill(handle_kill)

            while SimEnv.run_main():
                pass #do nothing but wait for event
        """
        #wrap and dispatch event
        def wrapper(sender:Killzone, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            dat = None
            try:
                js = json.loads(raw)
                dat = BaseEventData(js)
            except:
                pass
            if dat is not None:
                handler(sender,gametime,dat)
            
        self._add_event_listener("_eventOnKill",wrapper)




class AirstrikeControl(EntityBase["AirstrikeControl"]):
    """Satellite guided airstrike launcher. Provide 2D coordinates in range [0,1] as the target launch position."""

    def hide_coordinates(self, hidden=True):
        """Show or hide the coordinate system of the target area.

        Args:
            hidden (bool, optional): True to hide, False to show. Defaults to True.

        Example:
            >>>
            AirstrikeControl.first().hide_coordinates(True)
        """
        self._set_bool("HideCoordinates", hidden)

    def launch(self, x: float, y: float, z=0.0):
        """Launch an airstrike at the provided target location. Time to target is approximately 3 seconds.

        Args:
            x (float): normalized x coordinate from 0 to 1
            y (float): normalized y coordinate from 0 to 1
            z (float, optional): ignored.

        Example:
            >>>
            airstrike = AirstrikeControl.first()
            #launch rocket at center position of target area
            airstrike.launch(0.5,0.5)
        """
        self._set_vector3d("Launch", (x, y, z))

    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255]).

        Example:
            >>>
            airstrike = AirstrikeControl.first()
            img = airstrike.get_camera_frame()
            # highlight center in red and show in-game
            img[120:134,120:134,0] = 255
            print(img)
        """
        return self._get_image("CameraFrame")


class Artillery(EntityBase["Artillery"]):
    """Artillery launcher."""

    def set_target_rotation(self, rotation:Rotator3, *args:float):
        """Set the target launch rotation in roll,pitch,yaw. roll is ignored. pitch is degrees within [5,80] and yaw is degrees within [-360,360].

        Args:
            rotation (Rotator3): launch rotation as roll, pitch, yaw. roll is ignored. pitch is degrees within [5,80] and yaw is degrees within [-360,360].

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_rotation((0,60,30))
            #wait until target reached
            sleep(10)
            arty.fire(400)
        """
        self._set_vector3d("setTargetRotation", rotation, add_args=args)

    def get_is_moving(self) -> bool:
        """True if the artillery is currently moving towards a target location, else False.

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_rotation((0,60,30))
            while arty.get_is_moving():
                sleep() # wait for move to complete
            print("target location reached")
        """
        return self._get_bool("IsMoving")

    def fire(self, muzzle_velocity: float):
        """Fire a 3kg shell with the specified exit muzzle velocity in [2,100] m/s.

        Args:
            muzzle_velocity (float): exit muzzle velocity in [2,100] m/s.

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_rotation((0,60,30))
            #wait until target reached
            sleep(10)
            arty.fire(10)
        """
        self._set_float("Fire", muzzle_velocity)

    def editor_set_reload_time(self, new_reload_time:float):
        """[Level Editor Only] Adjust the reload time (cooldown) of this artillery after every shell fired.

        Args:
            new_reload_time (float): Reload time in seconds.
        """
        self._set_float("setReloadTime", new_reload_time)

    # def editor_set_target_vis_enabled(self, is_enabled:bool):
    #     """Enable or disable a target indicator, that shows the arc / parabola the shell will 

    #     Args:
    #         is_enabled (bool): _description_
    #     """

    # def set_shell_type(self, shell_type:AmmunitionTypes):
    #     """Change the shell ammunition type used by this artillery.

    #     Args:
    #         shell_type (AmmunitionTypes): Ammo type
    #     """
    #     self._set_string("setShellType", str(shell_type))

    # def editor_set_can_change_shell_type(self, new_enabled:bool):
    #     """[Level Editor Only] Set wether the player can change the ammo type of this artillery or not."""
    #     self._set_bool("SetCanChangeShellType", new_enabled)


class MoonLander(EntityBase["MoonLander"]):
    pass#https://www.unrealengine.com/marketplace/en-US/product/moon-landing-zone


class DigitalScale(EntityBase["DigitalScale"]):
    """A digital scale to measure the weight of objects and also count them.
    """

    def get_weight(self) -> float:
        """Get the total mass (in kg) of all object currently being weighed.

        Returns:
            float: Total weight in kg

        Example:
            >>>
            scale = DigitalScale.first()
            w = scale.get_weight()
            c = scale.get_count()
            print(f"avg weight of {w/c} kg")
        """
        return self._get_float("Weight")

    def get_count(self) -> float:
        """Get the number of objects currently on the scale.

        Returns:
            int: number of objects

        Example:
            >>>
            scale = DigitalScale.first()
            w = scale.get_weight()
            c = scale.get_count()
            print(f"avg weight of {w/c} kg")
        """
        return self._get_float("Count")


class PinHacker(EntityBase["PinHacker"]):
    """Brute force hacking device for PIN numbers."""

    def enter_pin(self, pin: int):
        """Enter a candidate PIN into the hacking device.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct():
                print(str(p) + " is correct!")
            elif hacker.get_is_greater():
                print(str(p) + " is greater than the real pin!")
            else:
                print(str(p) + " is smaller than the real pin!")
        """
        self._set_int("EnterPin", pin)

    def get_is_correct(self) -> bool:
        """Check whether the last entered pin was correct or not.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct():
                print(str(p) + " is correct!")
            elif hacker.get_is_greater():
                print(str(p) + " is greater than the real pin!")
            else:
                print(str(p) + " is smaller than the real pin!")
        """
        return self._get_bool("IsCorrect")

    def get_is_greater(self) -> bool:
        """Check whether the last entered pin is greater than the real pin.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct():
                print(str(p) + " is correct!")
            elif hacker.get_is_greater():
                print(str(p) + " is greater than the real pin!")
            else:
                print(str(p) + " is smaller than the real pin!")
        """
        return self._get_bool("IsGreater")

    def check_pin(self, pin: int) -> str:
        """Check if the supplied pin is correct, greater than or less than the real pin. Convenience synchronous blocking operation.

        Example:
            >>>
            hacker = PinHacker.first()
            #enter candidate pin
            p = 123
            # check pin, this takes a one round-trip
            # (at 2 Hz it's 0.5 seconds )
            res = hacker.check_pin(p)
            print(res)
        """
        self.enter_pin(pin)
        sleep(1.1)
        if self.get_is_correct():
            return "correct"
        elif self.get_is_greater():
            return "greater"
        else:
            return "less"


class VoxelBuilder(EntityBase["VoxelBuilder"]):
    """Spawn voxels / cubes / boxes at the specified location and the specified color."""

    def build_voxel(self, location:Vector3|Sequence[float] = (0.0, 0.0, 0.0), color=Colors.Grey, simulate_physics=False):
        """Spawn voxels / cubes / boxes at the specified location and the specified color. Asynchronous, so you need to call sleep() in-between calls to build()

        Args:
            location: tuple x (forward), y (right), z (up) in meters.
            color: RGB color to apply to the mesh. Either RGB tuple or Colors name.
            simulate_physics (bool): True to simulate physics, false to make the object stationary.

        Example:
            >>>
            builder = VoxelBuilder.first()
            builder.build_voxel((1,1,5))
            sleep(3)
            builder.build_voxel((1,1,6),Colors.Red)
        """
        loc = _parse_vector(location, True)

        color = _parse_color(color, True)

        self._set_json(
            "BuildVoxel",
            {"Location": loc, "Color": color, "bPhysics": simulate_physics},
            False,
        )



def _get_kwargs(kwargs: Dict[str, Any]):
    loc = _parse_vector(kwargs.get("location", (0.0, 0.0, 0.0)), True)
    scale = _parse_vector(kwargs.get("scale", (1.0, 1.0, 1.0)), True)
    rot = _parse_vector(kwargs.get("rotation", (0.0, 0.0, 0.0)), True, ("roll","pitch","yaw"))
    mcol = _parse_color(kwargs.get("color", ""), True)
    set_color = len(mcol) > 2
    duration = kwargs.get("duration", -1.0)
    rfid_tag = kwargs.get("rfid_tag", "")
    is_temp = kwargs.get("is_temp", False)
    adjust_z = kwargs.get("adjust_z", False)
    lifetime = kwargs.get("lifetime", -1.0)
    adjust_coll = kwargs.get("adjust_coll", False)
        
    return {
        "Location": loc,
        "Rotation": rot,
        "Scale": scale,
        "Duration": duration,
        "Color": mcol,
        "bSetColor": set_color,
        "RfidTag":rfid_tag,
        "LineNumber": EntityBase._get_line_number(),
        "bTemp":is_temp,
        "bAdjustZ":adjust_z,
        "Lifetime":lifetime,
        "bAdjustColl":adjust_coll
    }
    

class CameraWaypoint:
    def __init__(self, location:Vector3, rotation = Rotator3(0), duration = 1.0) -> None:
        self.location = _parse_vector(location, True)
        """Location (in world-space meters) of this camera waypoint."""
        self.rotation = _parse_vector(rotation, True, ("roll","pitch","yaw"))        
        """Optional rotation (in degrees) of this next camera waypoint relative to its forwards direction."""
        self.duration = duration
        """Duration (in seconds) it takes for the camera sequence to transition from this waypoint to the next."""

    def _to_dict(self):
        return {
            "Location":self.location,
            "Rotation":self.rotation,
            "Duration":self.duration
            }

class BuildingEntry:
    def __init__(self, entity:SpawnableEntities, count:int=0) -> None:
        self.entity = entity
        self.count = count

    def _to_dict(self):
        return {
            "Entity":str(self.entity),
            "Count":self.count
            }

class LevelEditor(EntityBase["LevelEditor"]):
    """Interface to the level editor. Only accessible in the Level Editor View."""

    __is_initialized = False
    
    def __init__(self, entity_name: str, **kwargs) -> None:
        super().__init__(entity_name, **kwargs)
        self._goal_funcs: Dict[str, Callable[[str], None]] = {}
        self._optional_goal_funcs: Dict[str, Callable[[str], None]] = {}
        self._dynamic_funcs: Dict[str, Callable[[float, float], bool]] = {}
        
        self._last_tick = 0.0
        self._current_tick = 0.0

        self._running_dynamics: Set[str] = set()
        self._running_goals: Set[str] = set()

    @classmethod
    def first(cls) -> "LevelEditor":
        #set tickrate for editor
        if LevelEditor.__is_initialized:
            all = cls._find_all_internal()
            if len(all) > 0:
                return all[0]
        k = "LevelEditor.Current.setTickRate"
        nparr = NPArray(k, np.asarray([5.0], dtype=np.float32))
        super()._set_out_data(k, nparr, False)
        if LevelEditor._is_construct_only():
            print("initializing level editor...")
        for i in range(6):
            time.sleep(1)
            all = cls._find_all_internal()
            if len(all) > 0:
                LevelEditor.__is_initialized = True
                return all[0]
            

        print("no level editor found, exiting")
        await_receive(2)
        from pyjop.Network import SimEnv

        SimEnv.disconnect()
        exit()
        return None

    @staticmethod
    def _is_construct_only() -> bool:
        import sys

        if len(sys.argv) > 1:
            return "construct_only" in sys.argv
        return False

    def select_map(self, map_name: SpawnableMaps):
        """Select the specified map for the current custom level.

        Example:
            >>>
            editor.select_map(SpawnableMaps.MinimalisticIndoor)
        """
        self._set_string("SelectMap", str(map_name))
        sleep(1)
        #add wait time for complex maps
        if map_name in ["Bridge"]:
            sleep(2)

    # build functions:

    def spawn_entity(self, entity_type: SpawnableEntities, unique_name="", location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1), rfid_tag = "", is_temp = False, adjust_z = False, lifetime = -1.0, adjust_coll = False, spawn_effect = False, is_clickable = True, is_readable = True, is_controllable = True):
        """Spawns a smart entity of the given type with the specified parameters.

        Args:
            entity_type: type name, e.g. SpawnableEntities.ConveyorBelt
            unique_name (str, optional): entity name, empty for automatic. must be unique among all entities.
            location (Vector3, optional): Location vector with x (forward), y (right), z (up) in meters
            rotation (Rotator3, optional): Rotation with roll, pitch, yaw in degree.
            scale (Vector3, optional): Size scaling factor with x (forward), y (right), z (up) as factor. Defaults to 1.
            rfid_tag (str, optional): Directly assign the supplied string as the RFID tag for this entity. Defaults to "". See also set_rfid_tag.
            is_temp (bool, optional): Make this entity temporary, meaning it will be destroyed automatically on level reset. Defaults to False.
            adjust_z (bool, optional): Automatically snap the entity down to the ground upon spawning. Defaults to False.
            lifetime (float, optional): Automatically destroy this entity after the specified amount of seconds. Values <= 0 mean unlimited lifetime. Defaults to -1.0.
            adjust_coll (bool, optional): Try to automatically adjust spawn position to prevent collisions. Defaults to False.
            spawn_effect (bool, optional): Show a VFX / SFX when spawning this entity. Defaults to False.
            is_clickable (bool, optional): Allow or disallow the player to click this entity and see its details. Defaults to True. See also set_clickable.
            is_readable (bool, optional): Allow or disallow the player to read sensor values from this entity. Defaults to True. See also set_readable.
            is_controllable (bool, optional): Allow or disallow the player to give commands to this entity. Defaults to True. See also set_controllable.

        Example:
            >>>
            editor.spawn_entity(SpawnableEntities.ConveyorBelt,"belt2",location = (5.5,0,0))
        """

        args = _get_kwargs(locals())
        self._set_json(
            "SpawnEntity",
            args |
            {
                "EntityClass": str(entity_type),
                "UniqueName": unique_name,
                "bSpawnEffect":spawn_effect,
                "bClickable":is_clickable,
                "bControllable": is_controllable,
                "bReadable": is_readable
            },
            True,
        )

    def spawn_static_mesh(
        self,
        mesh: SpawnableMeshes,
        unique_name="",
        location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1),
        material=SpawnableMaterials.Default,
        simulate_physics=False,
        texture = SpawnableImages.Blank,
        weight = -1.0,
        spawn_effect = False,
        color:Optional[Colors] = None,
        rfid_tag = "", is_temp = False, adjust_z = False, lifetime = -1.0, adjust_coll = False
    ):
        """Spawns the specified static mesh with the optional material

        Args:
            mesh (str): the mesh to spawn, e.g. SpawnableMeshes.Cube
            unique_name (str): optional unique name for the mesh. Should only be non-empty if you need access to this mesh via script later
            material (str): name of material to apply to the mesh, SpawnableMaterials.Default keeps default material
            color (tuple): RGB color to apply to the material. Either RGB tuple or Colors name
            simulate_physics (bool): True to simulate physics
            texture: image texture to apply to the material.
            weight: overwrite the default weight of this object
            spawn_effect: Show a dissolve / appear effect (True) or not (False)
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor
            rfid_tag (str, optional): Directly assign the supplied string as the RFID tag for this mesh. Defaults to "". See also set_rfid_tag.
            is_temp (bool, optional): Make this mesh temporary, meaning it will be destroyed automatically on level reset. Defaults to False.
            adjust_z (bool, optional): Automatically snap the mesh down to the ground upon spawning. Defaults to False.
            lifetime (float, optional): Automatically destroy this mesh after the specified amount of seconds. Values <= 0 mean unlimited lifetime. Defaults to -1.0.
            adjust_coll (bool, optional): Try to automatically adjust spawn position to prevent collisions. Defaults to False.
        """

        args = _get_kwargs(locals())

        self._set_json(
            "SpawnEntity",
            args
            | {
                "EntityClass": "StaticMesh",
                "UniqueName": unique_name,
                "Mesh": str(mesh),
                "Material": str(material),
                "bPhysics": simulate_physics,
                "Image": str(texture),
                "Weight": float(weight),
                "bSpawnEffect":spawn_effect
            },
            True,
        )  # mark as placement spawn in-game


    def spawn_destructible(self,
        unique_name="",
        location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1),
        color:Colors = Colors.Darkgray,
        rfid_tag = ""
    ):
        """Spawn a destructible cube. Will burst into small pieces upon receiving damage from physical impacts. Note that destructibles are always consider temporary objects and will be cleaned up on reset. Re-spawn them after reset if required.

        Args:
            unique_name (str): optional unique name for the destructible. Should only be non-empty if you need access to this via script later, e.g. to query destruction status.
            color (tuple): RGB color to apply to the material. Either RGB tuple or Colors name
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor. Scales != 1 might cause weird physics behavior, particularly non-uniform scales.
            rfid_tag (str, optional): Directly assign the supplied string as the RFID tag for this destructible. Defaults to "". See also set_rfid_tag.
        """
        args = _get_kwargs(locals())

        self._set_json(
            "SpawnDestructible",
            args
            | {
                "EntityClass": "StaticMesh",
                "UniqueName": unique_name,
            },
            True,
        )  # mark as placement spawn in-game

    # def set_level_metadata(self, name:str, description:str, category:str, )

    def specify_goal(
        self,
        unique_name: str,
        display_text: str,
        update_func: Optional[Callable[[str], None]] = None,
        goal_value: float = 1.0,
        is_resettable: bool = True,
        is_optional: bool = False,
        hide_next: Optional[bool] = None
    ):
        """Specify a goal for this level and how it should be evaluated

        Args:
            unique_name (str): unique name of the goal
            display_text (str): The text as displayed to the player in-game
            update_func (Callable[[str],None]): function to evaluate the current goal. must have a single parameter which will be filled with the unique name of this goal. should call set_goal_progress or set_goal_state internally.
            goal_value (float): The relative value of this goal. If the sum of all completed goals is >1, then the level is completed. Ignored for optional goals (see below).
            is_resettable (bool): DEPRECATED. Always True. Please manually adjust goals on_reset if required.
            is_optional (bool): Whether this is a mandatory goal or one of the optional goals
            hide_next (bool): Hide the next goal or not. Defaults to None which causes mandatory goals to hide the next goal, but not optional goals.


        Example:
            >>>
            def move_it_goal(goal_name:str):
                if ConveyorBelt.find("belt2").get_is_transporting():
                    editor.set_goal_state(goal_name,GoalState.Success)
                elif ConveyorBelt.find("belt1").get_is_transporting()==False:
                    editor.set_goal_state(goal_name,GoalState.Fail,"Better reset the level!")

            editor.specify_goal("moveit", "move the box from one to the other conveyor belt", move_it_goal, 1)
        """
        
        self._set_json(
            "SpecifyGoal",
            {
                "UniqueName": unique_name,
                "DisplayText": display_text,
                "GoalValue": 0.0 if is_optional else goal_value,
                "bResettable": True,
                "bOptional": is_optional,
                "bHideNext": not is_optional if hide_next is None else hide_next
            },
            True,
        )
        if update_func is not None:
            if is_optional:
                self._optional_goal_funcs[unique_name] = update_func
            else:
                self._goal_funcs[unique_name] = update_func

    def set_goals_intro_text(self, new_text:str):
        """Set / update intro text before the goals display.

        Args:
            new_text (str): Text with ExpressiveText markup.
        """
        self._set_string("SetGoalsIntroText", new_text)

    def set_optional_goals_intro_text(self, new_text:str):
        """Set / update intro text before the optional goals display.

        Args:
            new_text (str): Text with ExpressiveText markup.
        """
        self._set_string("SetOptionalIntroText", new_text)

    def set_goal_progress(
        self, unique_name: str, new_progress: float, new_text: str = ""
    ):
        """update the progress of the specified goal, optionally changing the display text as well.

        Args:
            unique_name (str): unique name of the goal as initially specified with the specify_goal function.
            new_progress (float): The new relative progress (0.0 to 1.0) to set. If progress >= 1, the state changes to Completed automatically.
            new_text (str, optional): Optionally change the display text of the goal.

        Example:
            >>>
            def survive_goal(goal_name:str):
            m = SimEnvManager.first()
            prog = m.get_sim_time() / 300
            editor.set_goal_progress(goal_name, prog)
        editor.specify_goal("survive", "Survive for at least 300 seconds!",1, True, False, survive_goal)
        """
        self._set_json(
            "UpdateGoal",
            {
                "UniqueName": unique_name,
                "DisplayText": new_text,
                "CurrentValue": new_progress,
                "CurrentState": str(GoalState.Unknown),
            },
            True,
        )

    

    def set_goal_state(
        self, unique_name: str, new_state: GoalState, new_text: str = ""
    ):
        """update the state of the specified goal, optionally changing the display text as well.

        Args:
            unique_name (str): unique name of the goal as initially specified with the specify_goal function.
            new_state (GoalState): The state to set the goal to.
            new_text (str, optional):  Optionally change the display text of the goal.

        Example:
            >>>
            def move_it_goal(goal_name:str):
                if ConveyorBelt.find("belt2").get_is_transporting():
                    editor.set_goal_state(goal_name,GoalState.Success)
                elif ConveyorBelt.find("belt1").get_is_transporting()==False:
                    editor.set_goal_state(goal_name,GoalState.Fail,"Better reset the level!")

            editor.specify_goal("moveit", "move the box from one to the other conveyor belt", 1, True, False,  move_it_goal)
        """
        self._set_json(
            "UpdateGoal",
            {
                "UniqueName": unique_name,
                "DisplayText": new_text,
                "CurrentValue": -1,
                "CurrentState": str(new_state),
            },
            True,
        )


    def on_level_reset(self, func: Callable[[], None]):
        """register a function that fires every time the level is reset

        Args:
            func (Callable[[],None]): the function to register

        Example:
            >>>
            data.num_resets = 0
            def my_reset_func():
                data.num_resets += 1
                print(f"level resets: {data.num_resets}")
            editor.on_level_reset(my_reset_func)
        """
        def wrapper(gametime: float, deltatime: float):
            if self._last_tick > self._current_tick:
                time.sleep(0.04)
                func()
            return False

        self._dynamic_funcs["on_level_reset_84654"] = wrapper
        #self._on_level_reset_handler = func

    def on_begin_play(self, func: Callable[[], None]):
        """register a function that executes once on begin play after the level has been fully constructed

        Args:
            func (Callable[[],None]): the function to register

        Example:
            >>>
            def my_beginplay_func():
                print("level has started, let's go")
            editor.on_begin_play(my_beginplay_func)
        """

        def wrapper(gametime: float, deltatime: float):
            if LevelEditor._is_construct_only() == False and gametime < 1:
                return False
            func()
            sleep()
            return True

        self._dynamic_funcs["on_begin_play_84654"] = wrapper

    def on_tick(self, func: Callable[[float, float], None]):
        """register a function that executes on every data exchange with the SimEnv. Provides current gametime and time since last tick call (both in seconds) as two parameters.

        Args:
            func (Callable[[float,float], None]): the function to register. Provides current gametime and  time since last tick call (both in seconds) as two parameters.

        Example:
            >>>
            data.mytime = 0.0
            def on_tick(simtime:float, deltatime:float):
                if data.mytime > 5:
                    print("hello every 5 seconds")
                    data.mytime = 0.0
                else:
                    data.mytime += deltatime

            editor.on_tick(on_tick)
        """

        def wrapper(gametime: float, deltatime: float):
            if gametime < 1.5:
                return False
            func(gametime, deltatime)
            return False

        self._dynamic_funcs["on_tick_84654"] = wrapper

    def on_player_command(self, handler:Callable[[float, str, str, str, NPArray],None]):
        """Register an event that gets fired anytime the player sends an api command to the game.
        """
        def wrapper(sender:LevelEditor, gametime:float, nparr:NPArray):
            #print(f"_eventOnPlayerCommand: {nparr.array_data}")
            nparr_inner = NPArray.from_msg(nparr.array_data.squeeze().tobytes())
            nameparts = nparr_inner.unique_name.split(".")
            entity_type = nameparts[0]
            entity_name = nameparts[1]
            command_name = nameparts[2]
            handler(gametime,entity_type,entity_name,command_name,nparr_inner)
        self._add_event_listener("_eventOnPlayerCommand", wrapper, True)

    # run / inference functions
    def show_vfx(self, vfx: SpawnableVFX, location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1), color:Optional[Colors] = None):
        """Shows the specified vfx effect at run-time

        Args:
            vfx (str): the vfx effect to play
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor
            color (tuple): optional RGB color to apply to the vfx. Either RGB tuple or Colors name

        Example:
            >>>
            editor.show_vfx(SpawnableVFX.Explosion)
        """

        args = _get_kwargs(locals())

        self._set_json(
            "SpawnEntity", args | {"EntityClass": "VFX", "VFX": str(vfx)}, True
        )

    def play_sound(self, sfx: SpawnableSounds, volume=1.0, is_ui=False, location = Vector3(0)):
        """Plays the specified one-shot sound effect at run-time

        Args:
            sfx (str): the sound effect to play
            volume (float): relative volume of the sound, between 0 and 1
            is_ui (boolean): is it a UI sound (2D), then True, else (3D sound) False
            location: tuple x (forward), y (right), z (up) in meters (only for non UI sounds)

        Example:
            >>>
            editor.play_sound(SpawnableSounds.Explosion, is_ui=True)
        """

        args = _get_kwargs(locals())

        self._set_json(
            "SpawnEntity",
            args
            | {"EntityClass": "SFX", "SFX": str(sfx), "Volume": volume, "bUI": is_ui},
            True,
        )

    def show_image(self, image: SpawnableImages):
        """Shows the specified image at run-time.

        Args:
            image (SpawnableImages): Image to show on the player's HUD

        Example:
            >>>
            editor.show_image(SpawnableImages.JoyOfProgrammingLogo)
        """
        args = _get_kwargs(locals())
        self._set_json(
            "SpawnEntity",
            args
            | {
                "EntityClass": "Image",
                "Image": str(image),
                "bUI": True,
            },
            True,
        )

    def show_video(self, video: SpawnableVideos, is_ui=True, should_loop=False, location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1)):
        """Shows the specified video at run-time.

        Args:
            video (SpawnableVideos): video to show.
            is_ui (bool, optional): True to show directly on top of the UI / HUD of the player, False to show as a 3D object in the world. Defaults to True. Note: You can only show 1 video as UI and 1 other video in 3D.
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor

        Example:
            >>>
            editor.show_image(SpawnableVideos.JoyOfProgrammingIntro)
        """
        args = _get_kwargs(locals())
        self._set_json(
            "SpawnEntity",
            args
            | {
                "EntityClass": "Video",
                "Video": str(video),
                "bUI": is_ui,
                "Duration": -1.0 if should_loop else 2.0
            },
            True,
        )

    def show_text(self, text: str, is_ui=True, duration=0.0, location = Vector3(0), rotation = Rotator3(0), scale = Vector3(1)):
        """Shows the supplied text on-screen with a typewriter effect.

        Args:
            text (str): text to display. Supports expressive text markup as documented here: https://expressivetext.com/docs
            is_ui (bool, optional): True to show directly on top of the UI / HUD of the player, False to show as a 3D object in the world. Defaults to True.
            duration: duration in seconds. Defaults to 0, which is automatic depending on text length. Negative values are infinite duration (until player clicks).
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor
        """
        raise NotImplementedError()
        args = _get_kwargs(locals())
        self._set_json(
            "SpawnEntity",
            args
            | {"EntityClass": "Text", "Text": text, "bUI": is_ui, "Duration": duration},
            True,
        )


    def get_goal_progress(self, unique_name: str) -> float:
        """get the relative progress (0.0 to 1.0) of the specified goal.

        Args:
            unique_name (str): unique name of the goal, as initially defined in the specify_goal function
        """
        return self._get_float("GoalProgress" + unique_name)

    def get_goal_state(self, unique_name: str) -> GoalState:
        """get the state of the specified goal.
        
        Args:
            unique_name (str): unique name of the goal, as initially defined in the specify_goal function
        """
        val = self._get_string("GoalState" + unique_name)
        if val in GoalState:
            return GoalState[val]
        return GoalState.Unknown

    #get goal visible function?

    def get_all_spawns(self) -> Sequence[str]:
        """get a list of all the uniquely named spawns created with the level editor."""
        return self._get_string("AllSpawns").split(";")

    def get_location(self, unique_name: str) -> Vector3:
        """get the current location of the named entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_vector3d("Location" + unique_name)

    def get_rotation(self, unique_name: str) -> Rotator3:
        """get the current rotation of the named entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_rotator3d("Rotation" + unique_name)

    def get_velocity(self, unique_name: str) -> Vector3:
        """get the current linear velocity (in m/s) of the named entity/mesh that you spawned from the level editor. Only works on physically simulated entities.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_vector3d("Velocity" + unique_name)

    def get_angular_velocity(self, unique_name: str) -> Vector3:
        """get the current angular velocity (in deg/s) of the named entity/mesh that you spawned from the level editor. Only works on physically simulated entities.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_vector3d("AngularVelocity" + unique_name)

    def get_mass(self, unique_name: str) -> float:
        """get the mass in kg of the named entity/mesh that you spawned from the level editor. Only works on physically simulated entities.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_float("Mass" + unique_name)

    def get_bounds(self, unique_name: str) -> np.ndarray:
        """get the current axis aligned bounding box (AABB) of the named entity/mesh that you spawned from the level editor. Returns min and max vectors in a 2x3 numpy array in meters
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_array_raw("Bounds" + unique_name, [2,3,1])

    def get_destruction(self, unique_name: str) -> Vector3:
        """get the current destruction amount (in [0,1]) of the named destructible that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        return self._get_vector3d("Destruction" + unique_name)

    def set_location(self, unique_name: str, new_location: Tuple[float, float, float], duration:float = 0.0):
        """set the current location of the named entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            new_location (vector): XYZ coordinates in meters.
            duration (float): Defaults to 0 for instant location change / teleport. Values > 0 cause the entity to move to the target location
        """
        self._set_json(
            "SetLocation", {"UniqueName": unique_name, "Location": _parse_vector(new_location), "Duration": duration}, True
        )

    def set_rotation(self, unique_name: str, new_rotation: Tuple[float, float, float], duration:float = 0.0):
        """rotate the named entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            new_rotation (Rotator3): roll,pitch,yaw angles in degrees.
            duration (float): Defaults to 0 for instant rotation change. Values > 0 cause the entity to rotate to the target rotation
        """
        self._set_json(
            "SetRotation", {"UniqueName": unique_name, "Rotation": _parse_vector(new_rotation), "Duration": duration}, True
        )
    def set_scale(self, unique_name: str, new_scale: Tuple[float, float, float], duration:float = 0.0):
        """the the new size / scale of the named entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            new_scale (vector): XYZ scale factor.
            duration (float): Defaults to 0 for instant scale change. Values > 0 cause the entity to grow/shrink to the target scale
        """
        self._set_json(
            "SetScale", {"UniqueName": unique_name, "Scale": _parse_vector(new_scale), "Duration": duration}, True
        )
    def set_color(self, unique_name: str, color: Colors, duration:float = 0.0):
        """the the new color of the named entity/mesh that you spawned from the level editor. Not all entities / meshes / materials support custom colors.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            color (Colors): new color to set.
        """
        self._set_json(
            "SetColor", {"UniqueName": unique_name, "Color": _parse_color(color), "Duration": duration}, True
        )

    def set_clickable(self, unique_name: str, is_clickable: bool):
        """set the entity that you spawned from the level editor to be clickable by the player or not.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity function.
            is_clickable (bool): True for clickable, False for non-clickable
        """
        self._set_json(
            "SetClickable",
            {"UniqueName": unique_name, "bClickable": is_clickable},
            True,
        )

    def set_controllable(self, unique_name: str, is_controllable: bool):
        """set the entity that you spawned from the level editor to be controllable by the player or not.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity function.
            is_controllable (bool): True for controllable, False for non_controllable
        """
        self._set_json(
            "SetControllable",
            {"UniqueName": unique_name, "bControllable": is_controllable},
            True,
        )

    def set_readable(self, unique_name: str, is_readable: bool):
        """set the entity that you spawned from the level editor to be readable by the player or not.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity function.
            is_readable (bool): True for readable, False for readable
        """
        self._set_json(
            "SetReadable",
            {"UniqueName": unique_name, "bReadable": is_readable},
            True,
        )

    #def set_temperature() TODO: temperature system

    def set_rfid_tag(self, unique_name: str, rfid_tag: str):
        """Set or add the rfid tag to the entity that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            rfid_tag (str): Set the rfid tag to this value.
        """
        self._set_json(
            "SetRfidTag",
            {"UniqueName": unique_name, "Tag": rfid_tag},
            True,
        )


    def set_enabled(self, unique_name: str, is_enabled: bool, component_name=""):
        """completely enable or disable the named entity that you spawned from the level editor. if component_name is specified, only enable or disable that component.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity function.
            is_enabled (bool): True for enabled, False for disabled
            component_name (str, optional): The name of the component to disable.
        """
        self._set_json(
            "SetEnabled",
            {
                "UniqueName": unique_name,
                "bEnabled": is_enabled,
                "ComponentName": component_name,
            },
            True,
        )

    def set_hidden(self, unique_name: str, is_hidden: bool):
        """hide or show the named entity that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            is_hidden (bool): True for hidden, False for visible
        """
        self._set_json(
            "SetHidden", {"UniqueName": unique_name, "bHidden": is_hidden}, True
        )

    def set_collision_enabled(self, unique_name: str, is_enabled: bool):
        """Enable or disable collision for the named entity that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            is_enabled (bool): True for collision enabled, False for no collision
        """
        self._set_json(
            "SetCollisionEnabled", {"UniqueName": unique_name, "bEnabled": is_enabled}, True
        )

    def set_lifetime(self, unique_name: str, lifetime: float):
        """Set the remaining lifetime for an object and destroy it afterwards. Setting to <= 0 disables the lifetime counter.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            lifetime (float): Seconds remaining.
        """
        self._set_json(
            "SetLifetime", {"UniqueName": unique_name, "Lifetime": lifetime}, True
        )

    
    def get_dataset_file(self, dataset_name:str) -> str:
        """Get the full path to the included dataset."""
        csvs = self._get_json("DatasetPaths")
        if dataset_name in csvs:
            return csvs[dataset_name]
        print(f"Dataset not found: {dataset_name}", col=Colors.Yellow)
        return ""
    
    def set_feature_data(self, unique_name:str, features:dict[str,Any], target:str|int|float):
        """Assign features and a target to an entity for machine learning challenges.
        """
        self._set_json("SetFeatureData", {"UniqueName": unique_name, "Features":features, "Target": target}, True)

    def get_feature_target(self, unique_name:str) -> str:
        """The the target label or target value from the feature data as assigned by set_feature_data()."""
        return self._get_string("FeatureTarget" + unique_name)

    def apply_impulse(self, unique_name:str, impulse:Vector3, ignore_mass = True):
        """Apply a physical impulse to the specified named entity. Entity must be simulating physics for this to have an effect.

        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
            impulse (Vector3): Impulse vector (direction and magnitude)
            ignore_mass (bool, optional): True to ignore mass and apply the impulse as a change in acceleration. Defaults to True.
        """
        self._set_json(
            "ApplyImpulse", {"UniqueName": unique_name, "Impulse": impulse, "bIgnoreMass":ignore_mass}, True
        )

    def set_weather_scenario(self, weather:WeatherScenario):
        """Set the current weather scenario. Only available for some outdoor levels.
        """
        self._set_int("SetWeatherScenario", int(weather))

    def set_time_of_day(self, hours_since_midnight:float):
        """Set the current time within the simulation to change the natural lighting. Only available for some outdoor levels.

        Args:
            hours_since_midnight (float): Time of day in hours, e.g. 16.5 for 4:30 p.m.
        """
        self._set_float("SetTimeOfDay", hours_since_midnight)

    def set_month_of_year(self, month:int):
        """Set the current month of the year. This influences the current weather scenario (rain or snow for example) and the time dependent lighting situation. Only available for some outdoor levels.

        Args:
            month (int): Month from January (1) to December (12)
        """
        self._set_int("SetMonthOfYear", month)

        

    def create_joint(self, name_child:str, name_parent:str, location:Optional[Vector3] = None, rotation:Optional[Rotator3] = None, angular_limits:Optional[Rotator3] = None, dampening:float = 5.0, stiffness:float = 50.0):
        """Attach named entity child to entity parent with the given joint constraint.

        Args:
            name_child (str): Unique name of the child entity that is being attached
            name_parent (str): Unique name of the parent entity to attach the child to
            location (Vector3, optional): Relative offset in meters where to create the joint.
            rotation (Rotator3, optional): Rotation offset for the joint.
            angular_limits (Rotator3, optional): Rotation half-limits in roll, pitch, yaw.
            dampening (float, optional): Angular dampening of the joint. Defaults to 5.0.
            stiffness (float, optional): Angular stiffness of the joint. Defaults to 50.0.

        """
        if name_child == name_parent:
            raise Exception("Entities child and parent cannot the same")
        json_dict = {
                "NameChild":name_child,
                "NameParent":name_parent,
                "Dampening":dampening,
                "Stiffness":stiffness
            }
        if location is not None:
            json_dict["Location"] = _parse_vector(location)
        if rotation is not None:
            json_dict["Rotation"] = _parse_vector(rotation)
        if angular_limits is not None:
            json_dict["AngularLimits"] = _parse_vector(angular_limits)
        self._set_json("AttachEntities", json_dict ,True)

    def create_spring(self, name_child:str, name_parent:str, location:Optional[Vector3] = None, rotation:Optional[Rotator3] = None, length_limits:Optional[Vector3] = None, dampening:float = 5.0, stiffness:float = 50.0):
        """Attach named entity child to entity parent with the given spring constraint.

        Args:
            name_child (str): Unique name of the child entity that is being attached
            name_parent (str): Unique name of the parent entity to attach the child to
            location (Vector3, optional): Relative offset in meters where to create the spring.
            rotation (Rotator3, optional): Rotation offset for the spring.
            length_limits (Vector3, optional): Maximum length of the fully extended spring in meters in x (forward-backward), y (right-left), z (up-down)
            dampening (float, optional): Linear dampening of the spring. Defaults to 5.0.
            stiffness (float, optional): Linear stiffness of the spring. Defaults to 50.0.
        """
        if name_child == name_parent:
            raise Exception("Entities child and parent cannot the same")
        json_dict = {
                "NameChild":name_child,
                "NameParent":name_parent,
                "Dampening":dampening,
                "Stiffness":stiffness
            }
        if location is not None:
            json_dict["Location"] = _parse_vector(location)
        if rotation is not None:
            json_dict["Rotation"] = _parse_vector(rotation)
        if length_limits is not None:
            json_dict["LengthLimits"] = _parse_vector(length_limits)
        self._set_json("AttachEntities", json_dict ,True)

    def weld_entities(self, name_child:str, name_parent:str):
        """Weld entity child to entity parent, keeping their current relative location offset. 

        Args:
            name_child (str): child entity
            name_parent (str): parent entity
        """
        if name_child == name_parent:
            raise Exception("Entities child and parent cannot the same")
        json_dict:dict[str,Any] = {
                "NameChild":name_child,
                "NameParent":name_parent
            }
            
        self._set_json("WeldEntities", json_dict ,True)

    def destroy(self, unique_name: str):
        """destroy / remove the entity/mesh that you spawned from the level editor.
        
        Args:
            unique_name (str): unique name of the entity, as initially defined in the spawn_entity or spawn_static_mesh function.
        """
        self._set_string("Destroy", unique_name, True)

    def destroy_temporaries(self):
        """destroy / remove all entities / meshes that you spawned with the flag "is_temp=True" """
        self._set_void("DestroyTemporaries")

    def clear_all(self):
        """Clears the entire level, removing all spawned objects."""
        self._set_void("ClearAll")

    def fade_out(self, duration=1.0):
        """Fade the current level to black within the specified duration.
        
        Args:
            duration (float): fade duration in seconds.
        """
        self._set_float("FadeOut", duration)

    def fade_in(self, duration=1.0):
        """Fade the current level into view within the specified duration.
        
        Args:
            duration (float): fade duration in seconds.
        """
        self._set_float("FadeIn", duration)

    def ping(self, location = Vector3(0), target_entity="", color:Colors = Colors.Red, duration=-1.0):
        """Ping a location or a uniquely named entity by creating a flashing indicator arrow on top of it. Disappears upon player click or after duration if > 0.

        Args:
            location (Vector3): Location in world coordinates in meters to ping. Either this or target_entity must be specified.
            target_entity (str): unique name of an entity (as spawned with spawn_entity or spawn_static_mesh) on top of which to create the indicator. Either this or location must be specified.
            color (Colors): Color of the indicator. Defaults to red.
            duration (float, optional): Duration to show the ping for. Defaults to -1.0 which means until the player clicks (the indicator or if entity is specified the entity).
        """
        self._set_json("Ping", {
            "Location": _parse_vector(location),
            "TargetEntity": target_entity,
            "Duration": duration,
            "Color": _parse_color(color)
        }, True)

    def play_camera_sequence(self, camera_waypoints:Sequence[CameraWaypoint]):
        """Play a camera sequence to show the player something in the level.

        Args:
            camera_waypoints (Sequence[CameraWaypoint]): List of CameraWaypoints to specific location, rotation and duration for each waypoint.

        Example:
            >>>
            print("camera roll")
            editor.play_camera_sequence([CameraWaypoint([0,10,1],[0,-20,0],3),CameraWaypoint([0,0,5],[0,-80,0],2)])
        """
        self._set_json("PlayCameraSequence", {
            "Waypoints": [w._to_dict() for w in camera_waypoints]
        })


    def get_player_code(self) -> str:
        """Get the complete python code the player has currently entered. Useful to provide tutorials, interactive code help or hints.
        """
        code = self._get_json("PlayerCode")
        return code["value"] if "value" in code else ""

    def add_player_code_hint(self, hint_text:str, line_number = -1):
        """Add a code hint directly in the player's python code. will be prepended with a comment #HINT: sign for security reasons. So you can only provide code hints, not working code to the player. They have to integrate your code hints themselves.
        """
        self._set_json("PlayerCodeHint", {"hint":hint_text, "line":line_number}, True)

    def add_hint(self,num:int, questions:List[str], answer:str = "", on_reveal:Optional[Callable[[float, int, int], None]] = None):
        """Set a hint / tip for this level accessible to the player via the Assistant window.

        Args:
            num (int): ID / Number of hint. Must be within [0,255]. Consecutive hints are hidden in auto-completion until the the predecessor has been revealed.
            questions (List[str]): List of synonymous questions that all lead to the same result.
            answer (str, optional): Optional static answer. Supply dynamic answers via the change_hint function within the on_reveal handler.
            on_reveal (Optional[Callable[[float, int, int], None]], optional): Event handler that will be called once the player asked one of the specified questions. Handler function must take three args, the current gametime (float), the question_num (int), the current number of times this hint was revealed (int >= 1).

        """
        if num < 0 or num > 255:
            raise JoyfulException(f"Hint num must be between 0 and 255, yours was f{num}")

        if type(questions) is str:
            questions = [questions]

            
        # def wrapper(gametime: float, deltatime: float):
        #     if num in self.get_revealed_hints():
        #         #print(f"Hint {num} revealed")
        #         if on_reveal is not None: #default handler
        #             on_reveal(num, gametime)
        #         return True #done, remove it
        #     return False

        # self._dynamic_funcs["on_reveal_" + str(num)] = wrapper

        
        def wrapper(sender:LevelEditor, gametime:float, nparr:NPArray):
            num_reveals = int.from_bytes(
                nparr.array_data.squeeze().tobytes(), "little"
            )
            if on_reveal is None:
                self._set_json("SetHint", {"Num":num, "Answer":answer}, True)
            else:
                if answer:
                    self.change_hint(num, answer)
                on_reveal(gametime,num, num_reveals)
                

        self._add_event_listener("_eventOnRevealHint" + str(num), wrapper, True)
        self._set_json("SetHint", {"Num":num, "Questions":questions, "Answer":answer}, True)

    def change_hint(self, num:int, answer:str = ""):
        if num < 0 or num > 255:
            raise Exception(f"Hint num must be between 0 and 255, yours was f{num}")
        self._set_json("SetHint", {"Num":num, "Answer":answer}, True)

    # def remove_hint(self, num:int):
    #     """Remove the hint with the specified number. Useful to remove obsolete tips that are not useful to the player anymore because of progress.

    #     Args:
    #         num (int): hint to remove
    #     """
    #     self._set_int("RemoveHint", num, True)

    # def get_revealed_hints(self) -> List[int]:
    #     """Get a list of all the hints the player revealed thus far."""
    #     return self._get_array_raw("RevealedHints", [1,0,1]).tolist()


    def set_map_bounds(self, center = Vector3(0), extends = Vector3(32,32,16)):
        """Change the map bounds (the area the player can move within) to the specified center and extends (in meters).

        Args:
            center (Vector3, optional): Center of the map bounds in meters. Defaults to [0,0,0].
            extends (Vector3, optional): Extends of the map bounds in meters in each cardinal direction. Defaults to [32,32,16].
        """
        self._set_json("SetMapBounds", {"Center":_parse_vector(center),
                                        "Extends": _parse_vector(extends)})
        sleep()


    def set_building_budget(self, budget:int):
        """Set the player's budget to place/build machines on their own. A budget of 0 means no limit on budget. A budget < 0 disables placement entirely. 

        Args:
            budget (int): Building budget.
        """
        raise NotImplementedError("Building / Budget system is WIP and not available yet.")
        self._set_int("SetBuildingBudget", budget)

    def set_allowed_buildings(self, allow_list:List[BuildingEntry], forbid_unlisted = False, reset = False):
        """Provide a list of machines the player will be allowed to purchase and build. The counts indicate how many are available at most. 0 means infinite. -1 means unavailable.

        Args:
            allow_list (List[BuildingEntry]): List of entities / machines the player will be allowed to place and their maximum counts.
            forbid_unlisted (boolean): Make all unlisted buildings infinitely available or forbid them entirely.
            reset (boolean): Reset all allowed buildings or only change the ones supplied
        """
        raise NotImplementedError("Building / Budget system is WIP and not available yet.")
        self._set_json("SetAllowedBuildings", {
            "Entries":[item._to_dict() for item in allow_list],
            "bForbidUnlisted":forbid_unlisted,
            "bReset":reset
            })

    def set_building_area(self, center:Vector3, extends:Vector3 ):
        """Restricts player building to the specified rectangular area.

        Args:
            center (Vector3): Center of the building area in meters.
            extends (Vector3): Extends (half size in all directions) of the building area in meters.
        """
        raise NotImplementedError("Building / Budget system is WIP and not available yet.")
        self._set_json("SetBuildingArea", {"Center":_parse_vector(center), "Extends":_parse_vector(extends)})

    def get_used_budget(self) -> float:
        """Get the current budget used by the player. Negative amounts indicate a surplus."""
        raise NotImplementedError("Building / Budget system is WIP and not available yet.")
        return self._get_float("UsedBudget")

    def get_current_money(self) -> float:
        """Get the current amount of money the player has."""
        raise NotImplementedError("Money system WIP")
        return self._get_float("CurrentMoney")
    
    def set_current_money(self, new_amount:float):
        """Set the current amount of money the player has. Also useful as a proxy for some kind of winning score."""
        raise NotImplementedError("Money system WIP")
        self._set_float("SetCurrentMoney", new_amount)



    def set_template_code(self, new_code:str = "", from_line:int = -1, from_comment = ""):
        """Set the python template code for this level.

        Args:
            new_code (str): the full template code
            from_line (int, optional): optionally write the template directly at the end of your level script and give this function the line number where it starts.
            from_comment (str, optional): optionally write the template directly at the end of your level script and give this function a unique comment line directly above the template code.
        """
        if new_code:
            self._set_json("SetTemplateCode", {"SourceCode":new_code})
            return
        try:
            source_code = []
            import inspect
            current_frame = inspect.currentframe()
            if current_frame and current_frame.f_back:
                with open(inspect.getmodule(current_frame.f_back).__file__, encoding='utf-8') as f:
                    source_code = f.read().splitlines()
        except:
            pass
        if from_line > 0 and len(source_code) > from_line:
            self._set_json("SetTemplateCode", {"SourceCode":"\n".join(source_code[from_line:])})
            return
        if from_comment:
            for i,l in enumerate(source_code):
                if l.strip() == from_comment.strip():
                    self._set_json("SetTemplateCode", {"SourceCode":"\n".join(source_code[i+1:])})
                    return
                
        print("Could not set template code", col=Colors.Orange)

    #TODO / Idea: allow to set score weighting from here
        

    # ideas: switch fps/rts mode

    # level editor runs in its own process
    def run_editor_level(self):
        """Start the custom level script. Must be the last line of code in a custom level script. Do not remove it."""

        time.sleep(0.55)
        m = SimEnvManager.first()
        m._set_void("ConstructionCompleted")

        from pyjop.Network import SimEnv

        if LevelEditor._is_construct_only():
            time.sleep(0.6)
            self._run_dynamics()
            time.sleep(0.2)
            SimEnv.disconnect()
            return
        # run the current level and check goals and evaluate dynamic functions. all highly parallel
        
        time.sleep(0.55)
        
        while SimEnv._is_connected:
            start = 0.0
            last_update = EntityBase.last_receive_at
            while last_update == EntityBase.last_receive_at and start < 3:
                time.sleep(0.002)
                start += 0.002

            self._last_tick = self._current_tick
            self._current_tick = m.get_sim_time()

 
            self._run_dynamics()
            self._check_goals()
            _dispatch_events()
            # handle level reset
            # if (
            #     last_sim_time > m.get_sim_time()
            #     and self._on_level_reset_handler is not None
            # ):
            #     self._on_level_reset_handler()
            # last_sim_time = m.get_sim_time()
            if m.get_is_completed():
                break

        SimEnv.disconnect()
        

    def _run_dynamics(self):
        if not self._dynamic_funcs:
            return
        # run all dyn funcs in sequentially
        old_dyns = []
        for k, f in self._dynamic_funcs.items():
            if k in self._running_dynamics:
                continue #already running
            self._running_dynamics.add(k)
            if f(self._current_tick, max(0.0,self._current_tick - self._last_tick)):
                old_dyns.append(k)
            self._running_dynamics.remove(k)

        #delete completed dyns
        for k in old_dyns:
            if k in self._dynamic_funcs:
                del self._dynamic_funcs[k]

    def _check_goals(self):
        for k,f in self._optional_goal_funcs.items():
            if k in self._running_goals:
                continue
            self._running_goals.add(k)
            f(k)
            self._running_goals.remove(k)
        for k, f in self._goal_funcs.items():
            if k in self._running_goals:
                continue
            self._running_goals.add(k)
            f(k)
            self._running_goals.remove(k)

class RPCInvoke:
    """Details about a remote procedure call."""
    def __init__(self, func_name:str, args:Tuple = (), kwargs:Dict[str,Any] = {}) -> None:
        self.ts = time.time()
        """Time-stamp in real-time (not game time) of the call."""
        self.func_name = func_name
        """Name of the function the player wants to invoke."""
        self.args = args
        """Any positional arguments that should be passed to the function."""
        self.kwargs = kwargs
        """Any named arguments that should be passed to the function."""

class DataExchange(EntityBase["DataExchange"]):
    """A database to exchange and persist data. Mostly useful to retrieve level specific data or to provide level specific answers.
    """

    def set_data(self, key:str, value:Any, const = False):
        """Add data to the exchange. 

        Args:
            key (str): Unique key.
            value (Any): Any json serializable payload.
            const (bool): Mark this key/value pair as constant, meaning it can not be overwritten

        Example:
            >>>
            dat = DataExchange.first()
            dat.set_data("number", 5.6)
            dat.set_data("stats", {"time":14.5, "distance":12.1, "id":"box"})
        """
        self._set_json("setData", {"Key":key, "Value": value, "Const": const}, True )

    def remove_data(self, key:str):
        """Remove data with the specified key from the exchange. 

        Args:
            key (str): Unique key to remove

        Example:
            >>>
            dat = DataExchange.first()
            dat.set_data("number", 5.6)
            dat.remove_data("number")
        """
        self._set_string("removeData", key, True)

    def get_data(self, key:str) -> Any:
        """Retrieve data from the exchange for the specified key. Note: Only works for small data. Large data like CSV files must me loaded with load_big_data first.

        Example:
            >>>
            dat = DataExchange.first()
            dat.set_data("number", 5.6)
            print(dat.get_data("number"))
        """
        all_dat = self._get_json("Data")
        if key in all_dat:
            return all_dat[key]
        print(f"Key '{key}' not found. Valid keys: {self.get_keys()}", col=Colors.Yellow)
        return ""

    def load_big_data(self, key:str) -> BytesIO:
        """Load and retrieve a big data set from a remote storage. Can take a few seconds on first load. Returns a BytesIO stream.

        Args:
            key (str): The name of the dataset to load. Can be level specific or one of the CsvDatasets.
        """
        all_dat = self._get_json("Data")
        if key in all_dat:
            print(f"{key} is not big data. Get it normally with get_data.", col=Colors.Yellow)
            return BytesIO()
        
        #try to sync load big data
        start = time.time()
        loaded_data:list[bytes] = []
        def wrapper(sender:DataExchange, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes()
            loaded_data.append(raw)

        self._add_event_listener("_eventOnData" + key, wrapper)
        self._set_string("LoadData", key)
        sleep()
        while not loaded_data and start < time.time()+3:
            sleep()
        self._clear_event_handlers("_eventOnData" + key)
        if loaded_data:
            return BytesIO(loaded_data[0])
        
        print(f"{key} not found", col=Colors.Yellow)
        return BytesIO()




    def get_keys(self) -> List[str]:
        """Retrieve list of available keys.

        Example:
            >>>
            dat = DataExchange.first()
            print(dat.get_keys())
        """
        all_dat = self._get_json("Data")
        return list(all_dat.keys())

    def editor_store_big_data(self, key:str, dat:bytes):
        """Store large amounts of data under the specified key. This data is only send to the player upon request. It is still stored in RAM, so try and keep the size reasonable (under 1gb).

        Args:
            key (str): short key to save the data under
            dat (bytes): raw data as byte sequence
        """
        if self.get_data(key):
            raise JoyfulException("The names of big data sets should be different from data already stored in the exchange.")
        self._set_bytes("storeBigData" + key, dat, True)

    def editor_set_readonly(self, is_readonly = True):
        """[Level Editor only] Make this data exchange readonly or not.

        Args:
            is_readonly (bool, optional): Defaults to True.
            
        Example:
            >>>
            DataExchange.first().editor_set_readonly(True)
        """
        self._set_bool("setReadonly",is_readonly)


    def rpc(self, func_name:str, *args, **kwargs) -> Any:
        """Make a synchronous remote procedure call. Available RPCs depend of the current level and should be explained there.

        Args:
            func_name (str): name of the function to call
            args: positional arguments to pass to the function
            kwargs: named parameters to pass to the function
        """
        old_dat = self.get_data("rpc_result")
        start = time.time()
        js = RPCInvoke(func_name,args, kwargs)
        self._set_json("rpc", js.__dict__)
        sleep()
        while self.get_data("rpc_result") == old_dat and start < time.time()-3:
            sleep()
        dat = self.get_data("rpc_result")
        if dat and dat["func_name"] == func_name:
            return dat["value"]
        else:
            return ""

    def on_rpc(self, handler:Callable[["DataExchange", RPCInvoke],None]):
        """React to a remote procedure call.

        Args:
            handler (Callable[[DataExchange, RPCInvoke],None]): Event handler called on any remote procedure call
        """
        def wrapper(sender:DataExchange, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            rpcinv = None
            try:
                js = json.loads(raw)
                rpcinv = RPCInvoke(js["func_name"],js["args"], js["kwargs"])
            except:
                pass
            if rpcinv is not None:
                handler(sender,rpcinv)

        self._add_event_listener("_eventOnRPC",wrapper)

    def return_rpc(self, func_name:str, val:Any):
        """Return the result for a given remote procedure call and store it in this data exchange.

        Args:
            func_name (str): The of the RPC for which to return a result.
            val (Any): Any json serializable payload. 
        """
        self.set_data("rpc_result", {"ts":time.time(), "func_name":func_name, "value":val})




def clamp(x, xmin=0, xmax=1):
    """Clamp the specified value x between the lower and upper limits"""
    if x < xmin:
        return xmin
    if x > xmax:
        return xmax
    return x


class LEDStrip(EntityBase["LEDStrip"]):
    """programmable LED strip"""

    def set_all_leds(self, colors: Sequence[Tuple[Colors, float]] | np.ndarray):
        """Set all LEDs at once by supplying a sequence of color/intensity tuples.

        Args:
            colors (Sequence[Tuple[Colors,float]] or ndarray): sequence of color/intensity tuples, either as a list of Colors and floats or directly as a numpy array.

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_all_leds([(Colors.Red,1),(Colors.Purple,0.5),(Colors.Yellow,1.5)])
        """
        if type(colors) is not np.ndarray:
            arr = np.zeros(len(colors) * 4, dtype=np.uint8)
            for i, c in enumerate(colors):
                j = i * 4
                arr[j : (j + 3)] = [x * 255.0 for x in c[0]]
                arr[j + 3] = clamp(c[1]) * 255  # assign data
        else:
            arr = colors
        k = self._build_name("setAllLeds")
        self._set_out_data(k, NPArray(k, arr), False)
        self._post_API_call()

    def set_intensity(self, intensity: float):
        """Set the intensity for the entire LED strip to the specified relative value in [0,1]

        Args:
            intensity (float): relative intensity in [0,1]

        Example:
            >>>
            LEDStrip.first().set_intensity(0.1)
        """
        self._set_float("setIntensity", intensity)

    def set_start_location(self, location:Vector3, *args:float):
        """Set the relative start location of the led strip. Limited to a +/- 2m adjustment in all directions.

        Args:
            location (Vector3): relative start location of the led strip. Limited to an +/- 2m adjustment in all directions.

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_start_location((-1,0,1))
        """
        self._set_vector3d("setStartLocation", location, add_args=args)

    def set_end_location(self, location:Vector3, *args:float):
        """Set the relative end location of the led strip. Limited to a +/- 2m adjustment in all directions.

        Args:
            location (Vector3): relative end location of the led strip. Limited to an +/- 2m adjustment in all directions.

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_end_location((2,0,0))
        """
        self._set_vector3d("setEndLocation", location, add_args=args)



class Maze(EntityBase["Maze"]):
    """A 2D maze"""

    def get_maze_data(self) -> np.ndarray:
        """Get the full maze as a 2D array. Can be None for certain levels.

        Example:
            >>>
            maz = Maze.first().get_maze_data()
            print(maz.shape) #size of the maze
            print(maz/maz.max()) #print maze as 2d pseudo image
        """
        return self._get_array_raw("MazeData",[0,0,1])

    def get_maze_size(self) -> Tuple[int, int]:
        """Get the size (width x height) of the maze in meters."""
        xy = self._get_array_raw("MazeSize",[2,1,1]).tolist()
        return (int(xy[0]), int(xy[1]))

    def editor_generate_maze(self, width: int, height: int):
        """[Level Editor only] Generate a new maze with the specified width and height.

        Args:
            width (int): width in meters, must be odd number
            height (int): height (or length) in meters, must be odd number

        Example:
            >>>
            Maze.first().editor_generate_maze(15,9)
        """

        if width % 2 == 0:
            width -= 1
        if height % 2 == 0:
            height -= 1
        width = clamp(width, 5, 255)
        height = clamp(height, 5, 255)
        self._set_json("GenerateMaze", {"width": width, "height": height})

    def editor_get_shortest_path(self):
        """[Level Editor only] Get the shortest path from entry to exit. Returns Nx2 ndarray with x,y coordinates."""
        k = self._build_name("ShortestPath")
        if k in self._in_dict:
            self._post_API_call()
            return self._in_dict[k].array_data[:, :, 0]

    def editor_set_path_visible(self, is_visible: bool):
        """[Level Editor only] Show the shortest path in-game."""
        self._set_bool("setPathVisible", is_visible)

    def editor_set_maze_data_enabled(self, is_enabled: bool):
        """[Level Editor only] Show the shortest path in-game."""
        self._set_bool("setMazeDataEnabled", is_enabled)


class DialupPhone(EntityBase["DialupPhone"]):
    """An old dial-up phone with audible dial tones that can be intercepted."""

    def get_last_number_audio(self):
        """Get raw PCM Wave audio data of the dial tones for the last number that was dialed.

        Example:
            >>>
            phone = DialupPhone.first()
            phone.dial_number("0124")
            sleep(4)
            #get the raw PCM audio data of the number tones we just dialed
            print(phone.get_last_number_audio())
            #todo: reconstruct the number 0124 from the audio data?
        """
        k = self._build_name("LastNumberAudio")
        if k in self._in_dict:
            self._post_API_call()
            return self._in_dict[k].array_data.squeeze()
        return None

    def dial_number(self, number: str):
        """Dial the specified number. Afterwards you can retrieve the recorded dial tones with get_last_number_audio()

        Args:
            number (str): The number to dial.

        Example:
            >>>
            phone = DialupPhone.first()
            phone.dial_number("0124")
            sleep(4)
            #get the raw PCM audio data of the number tones we just dialed
            print(phone.get_last_number_audio())
            #todo: reconstruct the number 0124 from the audio data?
        """
        self._set_string("DialNumber", number)


class RadarData(BaseEventData):
    """Event data returned by a radar"""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)
        
        self.angle: float = new_vals["angle"]
        """The planar angle (in degrees, relative to the radar) at which the other entity was scanned."""
        self.distance: float = new_vals["distance"]
        """The distance in meters (relative to the radar) at which the other entity was scanned."""
        self.heading: float = new_vals["heading"]
        """The planar direction (in degrees, relative to the radar) the other entity is heading towards."""
        self.speed: float = new_vals["speed"]
        """The speed (in meters / second) the other entity is moving at."""
        self.size: float = new_vals["size"]
        """The signature size in meters"""


class SmartRadar(EntityBase["SmartRadar"]):
    """A radar that can give information about all objects in its range."""

    def get_radar_data(self) -> List[RadarData]:
        """Get radar data for all objects in range.

        Returns list RadarData. For each object, you get "angle","distance","heading","speed","entity_type", "entity_name" (depending on the radar model).

        Example:
            >>>
            radar = SmartRadar.first()
            readings = radar.get_radar_data()
            for dat in readings:
                print(f"{dat.entity_type} at {dat.distance}m")
        """
        return [RadarData(d) for d in self._get_json("RadarData")["items"]]

    def editor_set_radar_range(self, new_range:float):
        """[Level Editor only] Set the radar's max range to the specified value (in meters). """
        self._set_float("setRadarRange", new_range)


class SmartLiDAR(EntityBase["SmartLiDAR"]):
    """A LiDAR sensor that produces point-clouds in local space relative to the lidar head. Depending on the model, it can associate each scanned point with an object id."""

    def editor_set_max_range(self, range: float):
        """[Level Editor only] Set the max range of the lidar in meters."""
        self._set_float("setMaxRange", range)
    def editor_set_has_semantic_sensor(self, is_enabled:bool):
        """[Level Editor only] Set whether the LiDAR has a semantic sensor to associate all scanned points with the object they belong to."""
        self._set_bool("setHasSemanticSensor", is_enabled)

    def get_lidar_data(self) -> np.ndarray:
        """Get LiDAR data.

        Returns LiDAR point cloud as a numpy matrix of shape (n,4), where the columns are x,y,z positions in local space relative to the lidar  head, and the object id, and n is the number of scanned points.

        Example:
            >>>
            lidar = SmartLiDAR.first()
            points = lidar.get_lidar_data()
            print(points.shape) #n points with 4 attributes each
            #show top down view of point cloud
            # import numpy as np
            img = np.zeros((256,256,1), np.uint8)
            coords = points[:,(0,1)]
            #scale to -1,1
            coords = coords / max(abs(coords.min()),coords.max())
            coords[:,0] *= -1 #mirror image
            #rescale to 0,256
            coords = coords * 128.0 + 128.0
            coords = coords.astype(np.uint8)
            #draw into image
            img[coords[:,0],coords[:,1]] = 255
            print(img)
        """
        return self._get_array_raw("LidarData",[0,4,1])




class ProximityData(BaseEventData):
    """Event data returned by a proximity sensor."""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)

        self.distance: float = new_vals["distance"]
        """The distance in meters (relative to the sensor) at which the other entity was scanned."""

        
class ProximitySensor(EntityBase["ProximitySensor"]):
    """Proximity sensor that can scan the relative distance to other entities."""

    def get_proximity_data(self) -> List[ProximityData]:
        """Get proximity data for all objects in range.

        Returns list ProximityData. For each object, you get base data plus distance in meters.

        Example:
            >>>
            prox = ProximitySensor.first()
            readings = prox.get_proximity_data()
            for dat in readings:
                print(f"{dat.entity_type} at {dat.distance}m")
        """
        return [ProximityData(d) for d in self._get_json("ProximityData")["items"]] 

    def editor_set_max_range(self, new_range:float):
        """[Level Editor only] Set the proximity sensor's max range to the specified value (in meters). """
        self._set_float("setMaxRange", new_range)

#class MaterialDepthSensor(EntityBase["MaterialDepthSensor"]):
#    pass # measure how deep the material below and above this sensor is / multi overlap sensor of some kind
class MovementEvent(BaseEventData):
    """Event data returned by a motion detector."""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)

        self.movement_amount: float = new_vals["movementAmount"]
        """Absolute amount of movement in meters that was detected."""

class MotionDetector(EntityBase["MotionDetector"]):
    """Simple motion detector sensor that fires an event whenever an object in its range moves."""
    
    def editor_set_max_range(self, new_range:float):
        """[Level Editor only] Set the motion detector's max range to the specified value (in meters). """
        self._set_float("setMaxRange", new_range)

    def on_movement(self, handler:Callable[["MotionDetector", float, MovementEvent],None]):
        """Event called when something moves within the motion detectors range.

        Args:
            handler (Callable[[MotionDetector,float, MovementEvent],None]): Event handler function that takes sender, simtime, MovementEvent data as arguments.

        Example:
            >>>
            mot = MotionDetector.first()
            #define event handler function
            def handle_motion(t,simtime,mov_data):
                print(f"{mov_data.entity_name} moved {mov_data.movement_amount} meters")

            #register event handler
            mot.on_movement(handle_motion)

            while SimEnv.run_main():
                pass #do nothing but wait for event
        """
        def wrapper(sender:MotionDetector, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            coll = None
            try:
                js = json.loads(raw)
                coll = MovementEvent(js)
            except:
                pass
            if coll is not None:
                handler(sender,gametime,coll)

        self._add_event_listener("_eventOnMovement", wrapper)


class SatelliteData(BaseEventData):
    """Data returned by a satellite."""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)

        self.world_location:Vector3 = Vector3(_parse_vector(new_vals["worldLocation"]))
        """Precise world location of the detected object."""

class SurveillanceSatellite(EntityBase["SurveillanceSatellite"]):
    """Eye in the sky. Surveillance satellite that can scan objects for their precise world location."""
    def get_satellite_data(self) -> List["SatelliteData"]:
        """Get data for all objects on the map. Returns a list of SatelliteData for each object.

        Example:
            >>>
            sat = SurveillanceSatellite.first()
            readings = sat.get_satellite_data()
            for dat in readings:
                print(f"{dat.entity_type} at {dat.world_location}")
        """
        return [SatelliteData(d) for d in self._get_json("SatelliteData")["items"]]


class Thermometer(EntityBase["Thermometer"]):
    """Can measure the temperature at its current location.
    """
    def get_temperature(self) -> float:
        """Measures the temperature at its current location in Kelvin.
        """
        return self._get_float("Temperature")

class Microphone(EntityBase["Microphone"]):
    """Can measure the audio level at its current location.
    """
    def get_audio_level(self) -> float:
        """Measures the current audio level at its current location in decibel.
        """
        return self._get_float("AudioLevel")

class GeigerCounter(EntityBase["GeigerCounter"]):
    """Can measure the radioactivity at its current location.
    """
    def get_radiation_level(self) -> float:
        """Measures the radioactivity at its current location.
        """
        return self._get_float("RadiationLevel")



class Elevator(EntityBase["Elevator"]):
    """A stationary elevator that can dynamically reach different heights."""

    def set_target_height(self, height: float):
        """Set the target height in meters."""
        self._set_float("setTargetHeight", height)

    def get_current_height(self) -> float:
        """Get the current height in meters."""
        return self._get_float("CurrentHeight")

    def get_state(self) -> ElevatorState:
        """Get the current state of the elevator (Idle, Upwards, Downwards)"""
        return ElevatorState(self._get_string("State"))


class PusherRobot(EntityBase["PusherRobot"]):
    """A simple 1D extendible robot that can push objects away in front of it."""

    def set_target_length(self, length: float):
        """Extend or retract the extension tip of the robot to the specified length and push out any objects in front of it. 

        Args:
            length (float): Target length between 0 and 3

        Example:
            >>>
            pusher = PusherRobot.first()
            #extend to 2.5m
            pusher.set_target_length(2.5)
            sleep(2)
            #retract to 0m
            pusher.set_target_length(0)
        """
        self._set_float("setTargetLength", length)

    def get_is_moving(self) -> bool:
        """Check whether the pusher is currently moving (True) or not (False).

        Example:
            >>>
            pusher = PusherRobot.first()
            pusher.set_target_length(2.5)
            sleep() #wait for command to be sent
            while pusher.get_is_moving():
                print("is moving!")
                sleep(0.1)
        """
        return self._get_bool("IsMoving")

class PullerRobot(EntityBase["PullerRobot"]):
    """A simple 1D pulling robot that can pull objects close with a hook-shot."""

    def set_pulling(self, is_enabled:bool):
        """Enable to pull any object on the line in front of the puller robot close towards it. Disable to stop pulling.

        Args:
            is_enabled (bool): True to pull, False to stop.

        Example:
            puller = PullerRobot.first()
            puller.set_pulling(True)
        """
        self._set_bool("setPulling", is_enabled)

    def editor_set_range(self, max_range:float = 15.0):
        """[Level Editor Only] Set the max range (in meters) of this puller robot.

        Args:
            max_range (float, optional): New maximum range of this puller robot. Defaults to 15m.
        """
        self._set_float("setRange", max_range)


class LaunchPad(EntityBase["LaunchPad"]):
    """Launch any object on top of this launch pad."""

    def launch(self, power: float):
        """Launch any object on top of this launch pad with the specified power.

        Args:
            power (float): Power to launch with in [0,1].

        Example:
            >>>
            #launch whatever is on top with 95% power
            LaunchPad.first().launch(0.95)
        """
        self._set_float("Launch", power)


class RemoteExplosive(EntityBase["RemoteExplosive"]):
    """An explosive device that can be triggered remotely"""

    def detonate(self):
        """Detonate this device immediately.

        Example:
            >>>
            #detonate all
            for expl in RemoteExplosive.find_all():
                expl.detonate()
                sleep(1)
        """
        self._set_void("Detonate")

    def set_countdown(self, seconds: float):
        """Set a countdown timer until the device detonates. Set to <= 0 to disarm.

        Args:
            seconds (float): Number of seconds until detonation. Use a value <= 0 to disarm.

        Example:
            >>>
            #10 second timer
            RemoteExplosive.first().set_countdown(10)
        """
        self._set_float("setCountdown", seconds)

    def get_countdown(self) -> float:
        """Get the remaining countdown in seconds.

        Example:
            >>>
            expl = RemoteExplosive.first()
            expl.set_countdown(60)
            while SimEnv.run_main():
                print(expl.get_countdown())  
        """
        return self._get_float("Countdown")

    def set_explosion_type(self, explosion_type:AmmunitionTypes):
        """Change the type of explosion this device causes.

        Args:
            explosion_type (AmmunitionTypes): Ammo type
        """
        self._set_string("setExplosionType", str(explosion_type))

    def editor_set_can_change_explosion_type(self, new_enabled:bool):
        """[Level Editor Only] Set wether the player can change the explosion type of this device or not."""
        self._set_bool("SetCanChangeExplosionType", new_enabled)

    
# class BaseTurret(EntityBase["BaseTurret"]):
#     """Base class for all turrets with mounted weapons."""
#     def set_rotation(self, yaw:float, pitch:float):
#         """Set target yaw and pitch rotation. Limited depending on the turret model.

#         Args:
#             yaw (float): in degrees.
#             pitch (float): in degrees.
#         """
#         self._set_vector3d("setRotation", [0,pitch,yaw])

# class GunTurret(EntityBaseStub["GunTurret"],BaseTurret):
#     pass


class ArcadeMachine(EntityBase["ArcadeMachine"]):
    """An old-school arcade game machine, offering a variety of games that can be played and automated with AI."""

    def send_buttons(self, buttons: Set[ArcadeButtons]):
        """Push and release all of the specified buttons at the same time.

        Example:
            >>>
            arcade = ArcadeMachine.first()
            arcade.send_buttons({ArcadeButtons.Up, ArcadeButtons.A})

        """
        self._set_string("SendButtons", ",".join([str(btn) for btn in buttons]))
    def set_axis(self, axis:ArcadeAxis, value:float):
        """Set and hold the specified axis to the specified value (in [-1,1]).

        Example:
            >>>
            arcade = ArcadeMachine.first()
            #50% up
            arcade.set_axis(ArcadeAxis.UpDown, 0.5)
            #100% left
            arcade.set_axis(ArcadeAxis.RightLeft, -1)
        """
        self._set_json("setAxis", {"axis":str(axis), "value":value}, True)

    def restart(self):
        """Restart the current arcade game.

        Example:
            >>>
            ArcadeMachine.first().restart()
        """
        self._set_void("Restart")

    def get_current_frame(self) -> np.ndarray:
        """Get the current frame image as displayed on the arcade machine. Not all arcade machines support this. Check in the simulation.

        Example:
            >>>
            arcade = ArcadeMachine.first()
            img = arcade.get_current_frame()
            print(img)
        """
        return self._get_image("CurrentFrame")

    def get_prev_frame(self) -> np.ndarray:
        """Get the prev frame image as it was displayed on the arcade machine. Not all arcade machines support this. Check in the simulation.

        Example:
            >>>
            arcade = ArcadeMachine.first()
            img = arcade.get_prev_frame()
            print(img)
        """
        return self._get_image("PrevFrame")


    def get_state_dict(self) -> dict[str, Any]:
        """Get the current state of the game being played directly from the RAM of the arcade machine. Returns a dictionary with different state parameters, depending on the game being played on the arcade machine.

        Example:
            >>>
            arcade = ArcadeMachine.first()
            print(arcade.get_state_dict())
        """
        return self._get_json("StateDict")

    def get_score(self) -> float:
        """Get the current score of the game being played on this arcade machine.

        Example:
            >>>
            arcade = ArcadeMachine.first()
            print(arcade.get_score())
        """
        return self._get_float("Score")
    def get_done(self) -> bool:
        """Get whether the game currently being played is over or not.
        
        Example:
            >>>
            arcade = ArcadeMachine.first()
            print(arcade.get_done())
        """
        return self._get_bool("Done")

    def editor_set_frame_grabber_enabled(self, is_enabled:bool):
        """[Level Editor Only] Enable or disable the frame grabber on this arcade machine."""
        self._set_bool("setFrameGrabberEnabled", is_enabled)
    def editor_set_state_dict_enabled(self, is_enabled:bool):
        """[Level Editor Only] Enable or disable the state dictionary on this arcade machine."""
        self._set_bool("setStateDictEnabled", is_enabled)
    def editor_set_game(self, game_name:ArcadeGames):
        """[Level Editor Only] Load the specified game into this arcade machine.

        Example:
            >>>
            ArcadeMachine.first().editor_set_game(ArcadeGames.Snak)
        """
        self._set_string("setGame",str(game_name))

    


class PushButton(EntityBase["PushButton"]):
    """A push button that can be pressed via script or within the simulation."""

    def get_last_press(self) -> float:
        """Get the last time (in simulation seconds) this button was pressed. Returns -1 if it was never pressed.

        Example:
            >>>
            btn = PushButton.first()
            #wait for button press in-game
            while btn.get_last_press() <= 0:
                sleep(0.1)
            print("pressed!")
        """
        return self._get_float("LastPress")

    def press(self):
        """Immediately press this button one time.

        Example:
            >>>
            PushButton.first().press()
        """
        self._set_void("Press")

    def on_press(self, handler:Callable[["PushButton",float],None]):
        """Event called when this button is pressed. 

        Args:
            handler (Callable[[PushButton,float],None]): Event handler function that takes sender,simtime as arguments.

        Example:
            >>>
            btn = PushButton.first()
            def on_press_handler(sender,simtime):
                print("button pressed at " + int(simtime))
            btn.on_press(on_press_handler)
            while SimEnv.run_main():
                #wait for event
                sleep(0.1)
        """
        def wrapper(sender:PushButton, gametime:float, nparr:NPArray):
            handler(sender,gametime)

        self._add_event_listener("_eventOnPress",wrapper)


class ToggleSwitch(EntityBase["ToggleSwitch"]):
    """A toggle button / switch that can be pressed via script or within the simulation."""

    def get_last_switch(self) -> float:
        """Get the last time (in simulation seconds) this toggle button was switched. Returns -1 if it was never switch.

        Example:
            >>>
            sw = ToggleSwitch.first()
            #wait for switch to be toggled in-game
            while sw.get_last_switch() <= 0:
                sleep(0.1)
            if sw.get_is_switched_on():
                print("switch ON")
            else:
                print("switch OFF")

        """
        return self._get_float("LastSwitch")

    def toggle(self):
        """Immediately toggle this switch.

        Example:
            >>>
            ToggleSwitch.first().toggle()
        """
        self._set_void("Toggle")

    def get_is_switched_on(self):
        """Get the current state of this toggle button (True for ON, False for OFF).

        Example:
            >>>
            sw = ToggleSwitch.first()
            #wait for switch to be toggled in-game
            while sw.get_last_switch() <= 0:
                sleep(0.1)
            if sw.get_is_switched_on():
                print("switch ON")
            else:
                print("switch OFF")
        """
        return self._get_bool("IsSwitchedOn")

    def on_toggle(self, handler:Callable[["ToggleSwitch",float, bool],None]):
        """Event called when the state of this switch changes. 

        Args:
            handler (Callable[[ToggleSwitch,float, bool],None]): Event handler function that takes sender,simtime,is_on as arguments.

        Example:
            >>>
            sw = ToggleSwitch.first()
            def on_toggle_handler(sender,simtime,is_on):
                print(f"switched to {"ON" if is_on else "OFF"}")
            sw.on_toggle(on_toggle_handler)
            while SimEnv.run_main():
                #wait for event
                sleep(0.1)
        """
        def wrapper(sender:ToggleSwitch, gametime:float, nparr:NPArray):
            if nparr.array_data.size > 0:
                is_on = bool(nparr.array_data[0][0][0] > 0)
                handler(sender,gametime,is_on)

        self._add_event_listener("_eventOnToggle",wrapper)


class Slider(EntityBase["Slider"]):
    """A slider that can be set to a value between 0 and 1"""

    def get_current_value(self) -> float:
        """Get the current value of the slider in [0...1].

        Example:
            >>>
            print(Slider.first().get_current_value())
        """
        return self._get_float("CurrentValue")

    def set_value(self, new_value: float):
        """Set the value of the slider in [0...1].

        Example:
            >>>
            Slider.first().set_value(0.8)
        """
        self._set_float("setValue", new_value)

    def on_changed(self, handler:Callable[["Slider",float, float],None]):
        """Event called when the value of this slider has changed. 

        Args:
            handler (Callable[[Slider,float, float],None]): Event handler function that takes sender,simtime,new_val as arguments.

        Example:
            >>>
            s = Slider.first()
            def on_value_changed(sender,simtime,new_val):
                print(f"slider set to {new_val}")
            s.on_changed(on_value_changed)
            while SimEnv.run_main():
                #wait for event
                sleep(0.1)
        """
        def wrapper(sender:Slider, gametime:float, nparr:NPArray):
            if nparr.array_data.size > 0:
                new_val = float(nparr.array_data[0][0][0])
                handler(sender,gametime,new_val)
                

        self._add_event_listener("_eventOnChanged",wrapper)

class InputBox(EntityBase["InputBox"]):
    """A box where the player can enter short text values."""

    def set_text(self, new_text:str):
        """Sets the current text. Maximum length is 32 characters.

        Args:
            new_text (str): Text to enter. Max 32 characters. ASCII only.

        Example:
            >>>
            ibox = InputBox.first()
            ibox.set_text("some text")
        """
        new_text = str(new_text)
        if new_text.strip():
            self._set_string("SetText", new_text)
        else:
            self._set_void("ClearText")

    def get_text(self) -> str:
        """Gets the current text.

        Example:
            >>>
            txt = InputBox.first().get_text()
            if txt:
                print(txt)
        """

        return self._get_string("Text")

    def on_changed(self, handler:Callable[["InputBox",float, str],None]):
        """Event called when the text for this input box was changed and committed. 

        Args:
            handler (Callable[[InputBox,float, str],None]): Event handler function that takes sender,simtime,new_text as arguments.

        Example:
            >>>
            ibox = InputBox.first()
            def on_text_changed(sender,simtime,new_text):
                print(f"text input: {new_text}")
            ibox.on_changed(on_text_changed)
            while SimEnv.run_main():
                #wait for event
                sleep(0.1)
        """
        def wrapper(sender:InputBox, gametime:float, nparr:NPArray):
            if nparr.array_data.size > 0:
                new_text = nparr.array_data.squeeze().tobytes().decode("ascii",errors='replace').strip()
                handler(sender,gametime,new_text)
                

        self._add_event_listener("_eventOnChanged",wrapper)

    def editor_set_hint_text(self, new_text:str):
        """[Level Editor Only] Change the initial hint text display in the input box.
        """
        self._set_string("SetHintText", new_text)


class RadarTrap(EntityBase["RadarTrap"]):
    """A radar trap / speedometer that can measure the speed of objects in front of it."""

    def get_speed(self) -> float:
        """Get the current speed (in m/s) of the closest moving object in front of the radar trap."""
        return self._get_float("Speed")

    def take_photo(self):
        """Take a photo of the closest moving object in front of the radar trap to issue a warning."""
        self._set_void("TakePhoto")


class TrafficLight(EntityBase["TrafficLight"]):
    """A programmable traffic light."""

    def set_state(self, new_state: TrafficLightStates):
        """Set and change the current state of the traffic light."""
        self._set_string("setState", str(new_state))

    def get_state(self) -> TrafficLightStates:
        """Get the current state of the traffic light."""
        return TrafficLightStates(self._get_string("State"))


class VacuumRobot(EntityBase["VacuumRobot"]):
    """A programmable vacuum robot. Does not have any sensors itself."""

    def move(self, forwards:int=1):
        """Move 1 step (10cm) instantly in forwards or backwards direction.

        Args:
            forwards (int): Defaults to 1 for forwards step. Set to -1 for backwards step.
        """
        return self._set_int("Move",forwards)

    def turn(self, clockwise:int=1):
        """Instantly turn 90° clockwise or counter-clockwise.

        Args:
            clockwise (int): Defaults to 1 for clockwise rotation. Set to -1 for counter-clockwise rotation.
        """
        return self._set_int("Turn",clockwise)

    def get_dirt_count(self) -> int:
        """Get the amount of dirt collected by this robot.
        """
        return self._get_int("DirtCount")

    def get_bumper_front(self) -> bool:
        """Returns true if the front of the robot collided with a wall with the last move.
        """
        return self._get_bool("BumperFront")
    def get_bumper_back(self) -> bool:
        """Returns true if the back of the robot collided with a wall with the last move.
        """
        return self._get_bool("BumperBack")



class ColorCubePuzzle(EntityBase["ColorCubePuzzle"]):
    """Classical puzzle of twisting a cube with 9 sub-faces such that each of the 6 sides consist of one solid color only."""

    def get_state(self) -> np.ndarray:
        """Get the state of the cube as 6 slices (Y[up],-Y[down],X[right],-X[left],Z[face],-Z[back]) of 3x3 sub-faces with color ids from 0 to 5"""
        return self._get_array_raw("State",[3,3,6])

    def twist(self, move: str):
        """Twist the cube with the specified single move. https://www.speedsolving.com/wiki/index.php?title=NxNxN_Notation https://hobbylark.com/puzzles/Rubik-Cube-Algorithms"""
        self._set_string("Twist", move)


class TriggerEvent(BaseEventData):
    """Event data returned by a TriggerZone"""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)

        self.begin_overlap:bool = bool(new_vals["bIsBeginOverlap"])
        """True if this is an BeginOverlap event, False for an EndOverlap event
        """


class TriggerZone(EntityBase["TriggerZone"]):
    """Trigger zone that registers an event each time another entity enters it / starts to overlap with it or exits / ends overlapping it."""

    def get_overlaps(self) -> List[TriggerEvent]:
        """Get all entities currently overlapping / triggering this zone.

        Returns:
            List[TriggerEvent]: list of trigger event data

        Example:
            >>>
            trigg = TriggerZone.first()
            for overlap in trigg.get_overlaps():
                print(f"triggered at {overlap.at_time}")
        """
        return [TriggerEvent(d) for d in self._get_json("Overlaps")["items"]]

    def on_triggered(self, handler:Callable[["TriggerZone",float, TriggerEvent],None]):
        """Event called when something enters / overlaps or exits this zone. 

        Args:
            handler (Callable[[TriggerZone,float, TriggerEvent],None]): Event handler function that takes sender, simtime, TriggerEvent data as arguments.

        Example:
            >>>
            trigg = TriggerZone.first()
            #define overlap event handler function
            def handle_overlap(t,simtime,trigg_data):
                if trigg_data.begin_overlap:
                    print(f"overlap with {trigg_data.entity_type}")
                else:
                    print("end overlap")

            #register event handler
            trigg.on_triggered(handle_overlap)

            while SimEnv.run_main():
                pass #do nothing but wait for event
        """
        def wrapper(sender:TriggerZone, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            coll = None
            try:
                js = json.loads(raw)
                coll = TriggerEvent(js)
            except:
                pass
            if coll is not None:
                handler(sender,gametime,coll)

        self._add_event_listener("_eventOnTriggered",wrapper)


class CollisionEvent(BaseEventData):
    """Event data returned by a SmartWall"""

    def __init__(self, new_vals: "dict[str, Any]"):
        super().__init__(new_vals)

        self.normal_impulse:Vector3 = Vector3(_parse_vector(new_vals["normalImpulse"]))
        """Normal impulse of the collision as a 3d vector."""

        self.impact_location:Vector3 = Vector3(_parse_vector(new_vals["impactLocation"]))
        """World-space location of the collision impact as a 3d vector."""

        self.impact_location_local:Vector3 = Vector3(_parse_vector(new_vals["impactLocationLocal"]))
        """Relative local-space location of the collision impact as a 3d vector."""


class SmartWall(EntityBase["SmartWall"]):
    """A smart wall (yes, that's totally a thing) that registers an event each time another entity bumps into it / collides with it."""

    def get_collisions(self) -> List[CollisionEvent]:
        """Get all collision events that happened within the last 5 seconds.

        Example:
            >>>
            wall = SmartWall.first()
            for coll in wall.get_collisions():
                print(f"collision at {coll.at_time} with {coll.entity_type}")
        """
        dat = self._get_json("Collisions")["items"]
        return [CollisionEvent(d) for d in dat]

    def on_collision(self, handler:Callable[["SmartWall",float, CollisionEvent],None]):
        """Event called when something collides with this wall. 

        Args:
            handler (Callable[[SmartWall,float, CollisionEvent],None]): Event handler function that takes sender,simtime,CollisionEvent data as arguments.

        Example:
            >>>
            wall = SmartWall.first()
            #define collision event handler function
            def handle_coll(s,simtime,coll_data):
                print(f"collision at {simtime} with {data.entity_type}")

            #register event handler
            wall.on_collision(handle_coll)

            while SimEnv.run_main():
                pass #do nothing but wait for event
        """
        #wrap and dispatch event
        import json
        def wrapper(sender:SmartWall, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            coll = None
            try:
                js = json.loads(raw)
                coll = CollisionEvent(js)
            except:
                pass
            if coll is not None:
                handler(sender,gametime,coll)

        self._add_event_listener("_eventOnCollision",wrapper)

    def editor_set_can_read_local_coll(self, enabled:bool):
        """[Level Editor only] Enable or disable the reading of local impact coordinates on this device."""
        self._set_bool("setCanReadLocalColl", enabled)
    def editor_set_can_read_world_coll(self, enabled:bool):
        """[Level Editor only] Enable or disable the reading of world-space impact coordinates on this device."""
        self._set_bool("setCanReadWorldColl", enabled)


        


# class PoolTable(EntityBase["PoolTable"]):
#     """A pool billiards table with integrated sensors and actuators."""

#     def set_cue_aiming(self, yaw: float, pitch: float, power: float):
#         """Set the target aim angles (yaw and pitch), the desired power for the next shot."""
#         self._set_vector3d("CueAiming", (yaw, pitch, power))

#     def set_cue_english(self, x_offset: float = 0.0, y_offset: float = 0.0):
#         """Set the target english / cue offset for the next shot.

#         Args:
#             x_offset (float, optional): in [-1...1]. Defaults to 0.0 for no offset.
#             y_offset (float, optional): in [-1...1]. Defaults to 0.0 for no offset.
#         """
#         self._set_vector3d("CueEnglish", (x_offset, y_offset, 0.0))

#     def shoot_ball(self):
#         """Shoot the cue ball with the previously specified angles, power and english."""
#         self._set_void("ShootBall")

#     def get_ball_locations(self) -> np.ndarray:
#         """Get a 2x16 array with the relative x/y positions of all balls. First index is the white cue ball, then the remaining 15 balls. Pocketed balls have -1/-1 as their coordinates."""
#         return self._get_array_raw("BallLocations",[2,16,1])


class HumanoidRobot(EntityBase["HumanoidRobot"]):
    """A humanoid robot able to walk around the world and manipulate physical objects."""

    def set_walking(self, yaw_angle: float, speed=1.0):
        """Set the walking speed and direction of the robot.

        Args:
            angle (float): Global direction in [0...360]
            speed (float, optional): Walking speed in [0...1]. Set to 0 to stop. Defaults to 1.0.

        Example:
            >>>
            robot = HumanoidRobot.first()
            #walk forwards
            robot.set_walking(0,1)
            sleep(3)
            #walk to the right
            robot.set_walking(90,1)
            sleep(3)
            #walk backwards
            robot.set_walking(180,1)
        """
        self._set_vector3d("setWalking", (yaw_angle, speed, 0))

    def get_orientation(self) -> float:
        """Get the robots yaw orientation (normalized to [-180,180] degrees) in world space.

        Example:
            robot = HumanoidRobot.first()
            robot.set_walking(45,1)
            while SimEnv.run_main():
                #should be 45 unless robot gets perturbed
                print(robot.get_orientation())
        """
        return self._get_float("Orientation")

    def jump(self):
        """Make the robot jump up. Can double jump.

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.jump()
            sleep() #wait 1 tick
            robot.jump() #double jump
        """
        self._set_void("Jump")

    def set_crouching(self, is_crouching: bool):
        """Toggle crouching on or off. Can also walk while crouching.

        Args:
            is_crouching (bool): Toggle crouch on (True) or off (False)

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.set_crouching(True)
            robot.set_walking(0,1)
            sleep(2)
            robot.set_crouching(False)
        """
        self._set_bool("setCrouching", is_crouching)

    def set_dancing(self, is_dancing: bool):
        """Toggle dancing on or off. Cannot walk while dancing.

        Args:
            is_dancing (bool): Toggle dancing on (True) or off (False)

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.set_dancing(True)
            sleep(5)
            robot.set_dancing(False)
        """
        self._set_bool("setDancing", is_dancing)
        

    def punch(self):
        """Punch any object directly in front of the robot.

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.punch()
        """
        self._set_void("Punch")

    def kick(self):
        """Kick any object directly in front of the robot.

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.kick()
        """
        self._set_void("Kick")

    def pickup(self):
        """Pickup an object directly in front of the robot. Not all objects can be picked up. Obviously.
        
        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.pickup()
            sleep(1)
            if robot.get_is_carrying():
                robot.release()
        """
        self._set_void("Pickup")

    def release(self):
        """Release any object the robot is currently carrying around.
        
        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.pickup()
            sleep(1)
            if robot.get_is_carrying():
                robot.release()
        """
        self._set_void("Release")

    def get_is_carrying(self) -> bool:
        """Returns True if the robot previously picked up an object and is carrying it around. 

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.pickup()
            sleep(1)
            if robot.get_is_carrying():
                robot.release()
                
        """
        return self._get_bool("IsCarrying")

    

    def get_is_on_ground(self) -> bool:
        """Check whether the robot is on firm ground (with at least one foot). If not, it means the robot is jumping or falling over.

        Example:
            >>>
            robot = HumanoidRobot.first()
            print(robot.get_is_on_ground())
        """
        return self._get_bool("IsOnGround")

    def get_is_blocked(self) -> bool:
        """Check whether the desired walking direction of the robot is blocked (True) or not (False).

        Example:
            >>>
            robot = HumanoidRobot.first()
            robot.set_walking(0,1)
            sleep(4)
            is_blocked = robot.get_is_blocked()
            if is_blocked:
                print("path blocked")
                robot.set_walking(180,1)
        """
        return self._get_bool("IsBlocked")

    def use(self):
        """Use / interact with the closest object in front of / in range of this humanoid robot. Interaction details depend on the target object and the current level."""
        self._set_void("Use")

    def fire(self):
        """If this robot has a weapon equipped or is interacting with a stationary weapon this command will trigger a single shot."""
        self._set_void("Fire")

    def editor_set_can_carry(self, can_carry:bool):
        """[Level Editor Only] Enable or disable carrying for this robot.

        Args:
            can_carry (bool): True to enable, False to disable.
        """
        self._set_bool("setCanCarry", can_carry)

    def editor_set_equipped_weapon(self, new_weapon:Firearms):
        """[Level Editor Only] Change the currently equipped weapon of this robot.

        Args:
            new_weapon (Firearms): new weapon to equip
        """
        self._set_string("SetEquippedWeapon", str(new_weapon))

    def get_health(self) -> float:
        """Get the current health of this robot."""
        return self._get_float("Health")

    def editor_set_health(self, new_health:float):
        """[Level Editor Only] Change the health of this robot."""
        self._set_float("SetHealth", new_health)

    def get_ammo(self) -> int:
        """Get the remaining ammunition count for the currently equipped weapon."""
        return self._get_int("Ammo")

    def editor_set_ammo(self, new_ammo:int):
        """[Level Editor Only] Change the available ammo for the currently equipped weapon."""
        self._set_int("SetHealth", new_ammo)

    def equip_cosmetics(self, cosmetic_item:CosmeticItems):
        """Equip the specified cosmetic item. If it is already equipped, un-equip it."""
        self._set_string("EquipCosmetics", str(cosmetic_item))


class Swapper(EntityBase["Swapper"]):
    """A machine with n slots can quickly swap objects on two arbitrary slots and return information about every object on its slots"""
    def editor_set_num_slots(self, num_slots:int):
        pass
    def swap(self, i:int, j:int):
        pass
    def get_tags(self) -> tuple[str]:
        return self._get_json("Tags")["items"]
    def get_weights(self):
        return self._get_array_raw("Weights")
    def attach(self):
        self._set_void("Attach")
    def release(self):
        self._set_void("Release")


class MessageSniffer(EntityBase["MessageSniffer"]):
    """Intercept messages that are encrypted with a simple Caesar substitution cipher. Meaning the encryption key must be a natural number. For example the message "abx" encrypted with the key "2" would be "cdz".
    """
    def get_cipher_text(self) -> str:
        """Get the intercepted message. It contains a hidden message. It's encrypted with a simple Caesar substitution cipher. Meaning the encryption key must be a natural number. For example the message "abx" encrypted with the key "2" would be "cdz".

        Example:
            >>>
            sniffer = MessageSniffer.first()
            print(sniffer.get_cipher_text())
            subkey = 2 #figure out what the substitution key is
            #then decrypt the message
            decrypt = sniffer.try_decrypt(subkey)
            print(decrypt)# did it work?
        """
        return self._get_string("CipherText")
    
    def try_decrypt(self, substitution_key:int):
        """Try to decode the intercepted message and get the decoded result.

        Args:
            substitution_key (int): Caesar substitution cipher. Meaning the encryption key must be a natural number. For example the message "abx" encrypted with the key "2" would be "cdz".
            
        Example:
            >>>
            sniffer = MessageSniffer.first()
            print(sniffer.get_cipher_text())
            subkey = 2 #figure out what the substitution key is
            #then decrypt the message
            decrypt = sniffer.try_decrypt(subkey)
            print(decrypt)# did it work?
        """
        self._set_int("TryDecrypt", substitution_key)
        await_receive()
        return self._get_string("DecryptedText")

    def editor_set_hidden_message(self, msg:str, substitution_key:int):
        """[Level Editor only] Set the hidden message and encrypt it with the specified substitution key.

        Args:
            msg (str): The hidden message you want to encrypt. 
            substitution_key (int): The encryption key (it's modulo 93, so there are only 93 possible values, all modulo values work just as well.)
        """
        self._set_json("setHiddenMessage",{"message":msg, "subkey":substitution_key})





class SniperRifle(EntityBase["SniperRifle"]):
    """Sniper rifle with an smart scope, targeting system and smart tracer bullet. Uses realistic G7 ballistics.
    """

    def fire(self):
        """Fire a single shot in the direction you are currently aiming. Has about 2 seconds reload time.

        Example:
            >>>
            SniperRifle.first().fire()
            sleep(2)
            #fire again
            SniperRifle.first().fire()
        """
        self._set_void("Fire")

    def set_zoom(self, zoom_factor:float):
        """Set the zoom factor of the sniper rifles scope in [1,25]

        Args:
            zoom_factor (float): Zoom factor from 1x to 25x

        Example:
            >>>
            #zoom in 10x
            SniperRifle.first().set_zoom(10)
        """
        self._set_float("setZoom", zoom_factor)


    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255]).

        Example:
            >>>
            r = SniperRifle.first()
            img = r.get_camera_frame()
            #show the scope's camera footage in-game
            print(img)
        """
        return self._get_image("CameraFrame")

    def get_object_detections(self) -> List[DetectionData]:
        """Get a list of all objects (entityName, entityType, 2D bounding box) currently visible in the scope.

        Example:
            >>>
            r = SniperRifle.first()
            dects = r.get_object_detections()
            for d in dects:
                print(f"{d.entity_type} detected at {d.real_distance}m")
        """
        return [DetectionData(d) for d in self._get_json("ObjectDetections")["items"]]

    def on_bullet_hit(self, handler:Callable[["SniperRifle",float, CollisionEvent],None]):
        """Event called when this sniper rifle hits something.

        Args:
            handler (Callable[[SmartWall,float, CollisionEvent],None]): Event handler function that takes sender,simtime,CollisionEvent data as arguments.

        Example:
            >>>
            #define event handler
            def on_hit(rifle:SniperRifle, gt:float, coll:CollisionEvent):
                print(f"Hit {coll.entity_name} with force {coll.normal_impulse}")
            #bind event handler    
            SniperRifle.first().on_bullet_hit(on_hit)
        """
        #wrap and dispatch event
        import json
        def wrapper(sender:SniperRifle, gametime:float, nparr:NPArray):
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            coll = None
            try:
                js = json.loads(raw)
                coll = CollisionEvent(js)
            except:
                pass
            if coll is not None:
                handler(sender,gametime,coll)

        self._add_event_listener("_eventOnBulletHit",wrapper)

    def editor_set_reload_time(self, new_reload_time:float):
        """[Level Editor Only] Adjust the reload time (cooldown) of this SniperRifle after every shot.

        Args:
            new_reload_time (float): Reload time in seconds.
        """
        self._set_float("setReloadTime", new_reload_time)

class Rocket(EntityBase["Rocket"]):
    """A steerable rocket with a gimbaled thruster"""
    
    def set_thruster_rotation(self, rotation:Rotator3, *args:float):
        """Set the rotation of the gimbaled thruster to the specified target in degrees. Roll is ignored.

        Args:
            rotation (Rotator3):roll (ignored), pitch and yaw angles in degrees within [-60,60] of the gimbaled thruster
        """
        self._set_vector3d("setThrusterRotation", rotation, add_args=args)

    def set_thruster_force(self, force: float):
        """Set the continuous force of the thruster to the specified value in [0,1000].

        Example:
            >>>
            apollo = Rocket.first()
            apollo.set_thruster_rotation(0,0,0) #straight up
            apollo.set_thruster_force(1000) #full throttle
        """
        self._set_float("setThrusterForce", force)

    def get_location(self) -> Vector3:
        """Get the rocket's own location in XYZ (forward,right,up) in world space in meters."""
        return self._get_vector3d("Location")

    def get_rotation(self) -> Rotator3:
        """Get the rocket's rotation vector in roll,pitch,yaw in degrees in world space"""
        return self._get_rotator3d("Rotation")

    def get_velocity(self) -> Vector3:
        """Get rocket's current velocity vector in meters per second"""
        return self._get_vector3d("Velocity")

    def detonate(self):
        """Detonate / self-destruct the rocket immediately."""
        self._set_void("Detonate")

class Quadcopter(EntityBase["Quadcopter"]):
    """A quadcopter drone with immediate thrust control."""

    def set_thruster_force_fl(self, new_thrust:float):
        """Set the thrust of the front left rotor.
        """
        self._set_float("SetThrusterForceFL", new_thrust)

    def set_thruster_force_fr(self, new_thrust:float):
        """Set the thrust of the front right rotor.
        """
        self._set_float("SetThrusterForceFR", new_thrust)

    def set_thruster_force_bl(self, new_thrust:float):
        """Set the thrust of the back left rotor.
        """
        self._set_float("SetThrusterForceBL", new_thrust)

    def set_thruster_force_br(self, new_thrust:float):
        """Set the thrust of the back right rotor.
        """
        self._set_float("SetThrusterForceBR", new_thrust)

    def get_ground_distance(self) -> float:
        """Get the altitude / distance to ground from the drone center to the actual ground below. Independent of drone orientation."""
        return self._get_float("GroundDistance")

    def get_rotation(self) -> Rotator3:
        """Get the drone's rotation vector in roll,pitch,yaw in degrees in world space"""
        return self._get_rotator3d("Rotation")

    def get_velocity(self) -> Vector3:
        """Get drones's current velocity vector in meters per second"""
        return self._get_vector3d("Velocity")

    #other sensors or interaction methods? camera (gimbaled / de-rotated), pickup / release, drop grenade



class PlayingCard(EntityBase["PlayingCard"]):
    """A single playing card from a standard 52-card deck."""

    def set_card(self, card_id:int|Tuple[CardRank,CardSuit]):
        """Set the card currently visible on this playing card. Either as linear card index or as rank/suit tuple.

        Args:
            card_id: linear card index or (CardRank,CardSuit) tuple.

        Example:
            >>>
            card = PlayingCard.first()
            card.set_card(5) # 7 of Clubs
            sleep(1)
             # King of Hearts:
            card.set_card((CardRank.King,CardSuit.Hearts))
        """
        
        if type(card_id) == int:
            lin_idx = card_id
        elif type(card_id) == Tuple[CardRank,CardSuit]:
            rank,suit = card_id
            lin_idx = (int(rank)-2) + 13*int(suit) 
        else:
            raise Exception("card_id must be integer or tuple of CardRank and CardSuit")
        self._set_int("SetCard", lin_idx)

    def get_current_card(self)->Tuple[CardRank,CardSuit]:
        """Get the card currently visible on this playing card. Functionality is level dependent and might be restricted.
        
        Example:
            >>>
            rank,suit = PlayingCard.first().get_current_card()
            print(f"Rank: {rank}, Suit: {suit}")
        """
        cardidx = self._get_int("CurrentCard")
        return (CardRank(cardidx%13 + 2), CardSuit(cardidx//13))

    def editor_set_has_card_getter(self, is_enabled:bool):
        """[Level Editor Only] Allow or prevent the player from reading this cards value.
        """
        self._set_bool("SetHasCardGetter", is_enabled)
        
    def editor_set_has_card_setter(self, is_enabled:bool):
        """[Level Editor Only] Allow or prevent the player from changing this cards value.
        """
        self._set_bool("SetHasCardSetter", is_enabled)


# class CardDeck(EntityBase["CardDeck"]):
#     """A standard deck of 52 playing cards."""
#     def draw(self) -> PlayingCard:
#         """Draw a single PlayingCard from the deck."""
#         pass

#     def shuffle(self, reshuffle:bool = True):
#         """Shuffle the whole 52 deck deck. Alternatively only shuffle the remaining cards with reshuffle = False."""
#         pass

class Dice(EntityBase["Dice"]):
    """Class for all dice: D4, D6, D8, D10, D12, D20."""

    def roll(self):
        """Roll this dice. Async function. Roll result will be returned in on_landed event handler."""
        self._set_void("Roll")

    def get_value(self) -> int:
        """Returns the current face value of the dice."""
        return self._get_uint8("Value")

    def get_is_rolling(self) -> bool:
        """Returns True if the dice is currently rolling, else False."""
        return self._get_bool("IsRolling")

    def on_landed(self, handler:Callable[["Dice", float, int],None]):
        """Event handler, called once the dice lands and returns a new face value. Also called on physical interaction without explicitly calling roll() beforehand.

        Args:
            handler (Callable[[Dice, float, int],None]): Handler function taking the current dice, gametime and face value as parameters.
        """
        def wrapper(sender:Dice, gametime:float, nparr:NPArray):
            val = -1
            try:
                val = int(nparr.array_data[0][0][0])
            except:
                pass
            if val >= 0:
                handler(sender,gametime,val)
        self._add_event_listener("_eventOnLanded", wrapper)

    # def dice_roller(roll_string:str):
    #     """Roll all the dice specified in the roll string at once.
    #     """
class DiceRoller(EntityBase["DiceRoller"]):
    """Dice rolling tower that can roll an (almost) arbitrary number of dice."""
    def roll_dice(self, roll_string:str):
        """Roll all the dice specified in the roll string at once. Format is "xDy+nDm...", e.g. "2D6" or "1D4 + 3d20" or "2d12 + 1D6 + 3d8". Async function. Roll result will be returned in on_completed event handler.
        """
        self._set_string("RollDice", roll_string)

    def on_completed(self, handler:Callable[["DiceRoller", float, List[int]],None]):
        """Event handler, called once all the rolled dice have landed and returns a list of dice face values sorted by dice type in ascending order (D4 to D20).

        Args:
            handler (Callable[[DiceRoller, float, List[int]],None]): Handler function taking the current DiceRoller, gametime and list of face values as parameters.
        """
        def wrapper(sender:DiceRoller, gametime:float, nparr:NPArray):
            vals = [int(val) for val in nparr.array_data.flatten()]
            if vals:
                handler(sender,gametime,vals)
        self._add_event_listener("_eventOnCompleted", wrapper)

class MiniatureFigure(EntityBase["MiniatureFigure"]):
    """A programmable game piece used in boardgames. Logic, rules and available functions depend on the current level."""

    #idea: show custom gui for figurine created from level editor script
    
    def editor_set_img(self, img:SpawnableImages):
        """Set a standee image for this figurine."""
        self._set_string("SetImg", str(img))
        
    def editor_set_mesh(self, mesh:SpawnableMeshes):
        """Set a 3d mesh for this figurine."""
        self._set_string("SetMesh", str(mesh))
        
        
    def perform(self, action:str, *args, **kwargs):
        """Perform the specified action with the specified named arguments. """
        if not action:
            return
        kwargs["PosArgsList"] = list(args)
        self._set_json(action, kwargs)

    def editor_set_state(self, key:str, value:Any):
        """Set or update a state variable for this figurine. States starting with _ are not readable by the player.

        Args:
            key (str): Unique key.
            value (Any): Value.
        """
        self._set_json("setState", {"Key":key, "Value": value}, True)

    def get_state(self, key:str) -> Any:
        """Retrieve the specified state variable for this figurine. Availability and meaning depends on the current level.
        """
        key = str(key)
        if not key or key.startswith("_"):
            return ""
        all_dat = self._get_json("State")
        if key in all_dat:
            return all_dat[key]
        return ""

    def get_state_variables(self) -> List[str]:
        """Retrieve list of available state variables
        """
        all_dat = self._get_json("Data")
        return [k for k in list(all_dat.keys()) if not k.startswith("_")]

    def get_action_names(self) -> List[str]:
        """Retrieve list of available actions this figurine can perform
        """
        return self._get_string("ActionNames").split(",")


    

class AirliftCrane(EntityBase["AirliftCrane"]):
    """A crane hook attached to a helicopter. Can lift up and put down objects anywhere quickly."""
    def editor_set_shake_intensity(self, intensity:float = 0.2):
        """[Level Editor Only] Set the relative shake intensity of the crane hook.

        Args:
            intensity (float): Intensity in [0,1]. Defaults to 0.2.
        """
        self._set_float("setShakeIntensity", intensity)

    def editor_set_size_limit(self, max_size:float = 5.0):
        """[Level Editor Only] Set the maximum size of objects this airlift can carry. Diameter in meters.

        Args:
            intensity (float): Diameter in meters. Defaults to 5m.
        """
        self._set_float("setSizeLimit", max_size)

    def editor_set_can_carry_non_physics(self, is_enabled:bool):
        """[Level Editor Only] Enable or disable the possibility to carry around non physically simulated objects. Careful, this means the player can lift up anything.
        """
        self._set_bool("setCanCarryNonPhysics", is_enabled)

    def set_target_location(self, loc:Vector3, *args:float):
        """Set a new target location for the hook of the AirliftCrane (meters in world space).

        Args:
            loc (Vector3): xyz (forward,right,up) vector with absolute position (meters in world space)

        Example:
            >>>
            air = AirliftCrane.first()
            air.set_target_location([0,0,5])
            air.pickup()
            air.set_target_location([5,3,7])
            sleep(3)
            air.release()
        """
        self._set_vector3d("setTargetLocation", loc, add_args=args)

    def pickup(self):
        """Pickup an object currently on / near the hook. Maximum size this crane can pick up may be limited.

        Example:
            >>>
            air = AirliftCrane.first()
            air.set_target_location(0,0,5)
            air.pickup()
            air.set_target_location(5,3,7)
            sleep(3)
            air.release()
        """
        self._set_void("Pickup")

    def release(self):
        """Immediately release any object currently on the hook of the Airlift.
        
        Example:
            >>>
            air = AirliftCrane.first()
            air.set_target_location(0,0,5)
            air.pickup()
            air.set_target_location(5,3,7)
            sleep(3)
            air.release()
        """
        self._set_void("Release")

    def get_is_transporting(self) -> bool:
        """Returns true if the Airlift has successfully picked up an object, and false if not.

        Example:
            >>>
            air = AirliftCrane.first()
            air.set_target_location(0,0,5)
            air.pickup()
            sleep(1)
            print(air.get_is_transporting())
        """
        return self._get_bool("IsTransporting")

    def get_is_moving(self) -> bool:
        """Returns true if the Airlift is currently moving, and false if not.

        Example:
            >>>
            air = AirliftCrane.first()
            air.set_target_location(0,0,5)
            sleep()
            print(air.get_is_moving())
        """
        return self._get_bool("IsMoving")

# class RailwayTrain(EntityBase["AlarmClock"]):
#     """A train on a railway track."""

#     def set_throttle(self, new_throttle:float):
#         self._set_float("SetThrottle", new_throttle)

#     def set_emergency_brake(self, is_enabled:bool):
#         self._set_bool("SetEmergencyBrake", is_enabled)

#     def get_track_ahead(self) -> np.ndarray:
#         pass # return next n spline points (position)

#     def editor_set_track_ahead_range(self, num_points:int):
#         self._set_int("SetTrackAheadRange", num_points)

class AlarmClock(EntityBase["AlarmClock"]):
    """Programmable alarm clock.
    """

    def get_current_time(self) -> str:
        """Gets the current time set on the clock as a hh::mm::ss string.

        Example:
            >>>
            #print current time
            t = AlarmClock.first().get_current_time()
            print(t)
            #convert current time from hh:mm:ss to total seconds
            hh,mm,ss = t.split(":")
            total_sec = ss + 60 * mm + 3600 * hh
            print(total_sec)
        """
        return self._get_string("CurrentTime")

    def set_is_running(self, is_enabled:bool):
        """Stop or run the clock.
        
        Example:
            >>>
            AlarmClock.first().set_is_running(False)
        """
        self._set_bool("setIsRunning",is_enabled)

    def set_use_gametime(self, is_enabled:bool):
        """Use gametime (True) or realtime (False).
        
        Example:
            >>>
            AlarmClock.first().set_use_gametime(False)
        """
        self._set_bool("setUseGametime",is_enabled)

    def set_alarm_time(self, alarm_time:float):
        """Sets the time when the alarm clock will trigger an alarm.

        Args:
            alarm_time (float): Alarm time as total hours from midnight in [0,24]

        Example:
            >>>
            #set alarm to 7 a.m.
            AlarmClock.first().set_alarm_time(7)
            #set alarm to 3 p.m.
            AlarmClock.first().set_alarm_time(15)
        """
        self._set_float("setAlarmTime", alarm_time)

    def set_current_time(self, new_time:float):
        """Sets the current time of the clock to the specified time (total hours from midnight).

        Args:
            new_time (float): total hours from midnight in [0,24[

        Example:
            >>>
            c = AlarmClock.first()
            #set time to 6 a.m.
            c.set_current_time(6)
            #set alarm to 8 p.m.
            c.set_current_time(20)
        """
        import datetime
        time.time
        self._set_float("setCurrentTime", new_time)

    def on_alarm(self, handler:Callable[["AlarmClock",float],None]):
        """Event called when the set alarm time of this clock is hit. Handler takes AlarmClock and gametime as arguments.

        Args:
            handler (Callable[[AlarmClock,float],None]): Handler function to be executed once the alarm time is hit. Takes AlarmClock and gametime as arguments.

        Example:
            >>>
            #define event handler
            def on_alarm(clock:AlarmClock, gt:float):
                print(f"Alarm at {clock.get_current_time()}")
            #bind event handler    
            AlarmClock.first().on_alarm(on_alarm)
        """
        def wrapper(sender:AlarmClock, gametime:float, nparr:NPArray):
            handler(sender, gametime)

        self._add_event_listener("_eventOnAlarm", wrapper)


class SimplePhysicsCar(EntityBase["SimplePhysicsCar"]):
    """A car with 4 simple physically simulated wheels. Can only drive forwards and backwards, no steering."""
    
    def apply_impulse(self, val:float):
        """Apply the given forward impulse in m/s."""
        self._set_float("ApplyImpulse", val)

class RaceCar(EntityBase["RaceCar"]):
    """A physically simulated wheeled race car."""
    
    def set_throttle(self, val:float):
        """Set the relative throttle of the engine in [0,1] from no throttle to full throttle. Driving backwards requires a positive throttle and a reverse gear.

        Args:
            val (float): relative throttle of the engine in [0,1]

        Example:
            >>>
            car = RaceCar.first()
            #full speed ahead
            car.set_throttle(1)
            car.set_gear(1)
            #half speed backwards
            car.set_throttle(0.5)
            car.set_gear(-1)
        """
        self._set_float("setThrottle",val)

    def set_steering(self, val:float):
        """Set the relative steering wheel angle in [-1,1] from full left to full right.

        Args:
            val (float): relative steering wheel angle in [-1,1] from full left to full right.

        Example:
            >>>
            car = RaceCar.first()
            #go left
            car.set_steering(-1)
            #go straight
            car.set_steering(0)
            #go half-right
            car.set_steering(0.5)
        """
        self._set_float("setSteering",val)

    def set_brake(self, val:float):
        """Set the relative brake intensity in [0,1] from no break to full break.

        Args:
            val (float): relative brake intensity in [0,1] from no break to full break.

        Example:
            >>>
            car = RaceCar.first()
            speed_limit = 20
            speeding = max(0,car.get_speed() - 20)
            #start braking smoothly if too fast
            car.set_brake(speeding / 10.0)
        """
        self._set_float("setBrake",val)

    def set_handbrake(self, is_enabled:bool):
        """Fully enable or disable the handbrake.

        Args:
            is_enabled (bool): enable or disable the handbrake.
            
        Example:
            >>>
            car = RaceCar.first()
            car.set_handbrake(True)
            sleep(1) #brake for 1 second
            car.set_handbrake(False)
        """
        self._set_bool("setHandbrake", is_enabled)

    def set_lights(self, is_enabled:bool):
        """Turn the headlights and taillights on or off.

        Args:
            is_enabled (bool): enable or disable the handbrake.
            
        Example:
            >>>
            #lights on
            RaceCar.first().set_lights(True)
        """
        self._set_bool("setLights",is_enabled)

    def set_gear(self, val:int):
        """Change gears to the specified target gear. Clutch transmission is automatic. Gear 0 is neutral, gears -1 and -2 are backwards and gears 1 to 6 are forwards.

        Args:
            val (int): Gear 0 is neutral, gears -1 and -2 are backwards and gears 1 to 6 are forwards.
            
        Example:
            >>>
            car = RaceCar.first()
            #full speed ahead
            car.set_throttle(1)
            car.set_gear(1)
            #half speed backwards
            car.set_throttle(0.5)
            car.set_gear(-1)
        """
        self._set_int("setGear", val)

    def apply_boost(self):
        """Apply a short nitro speed boost in the car's forward direction. Costs a lot of fuel.

        Example:
            >>>
            car = RaceCar.first()
            fuel1 = car.get_fuel()
            #boost
            car.apply_boost()
            sleep(1)
            #show fuel cost
            print(fuel1 - car.get_fuel())
        """
        self._set_void("ApplyBoost")

    def get_speed(self) -> float:
        """Get the car's current forward speed in m/s.

        Example:
            >>>
            car = RaceCar.first()
            speed_limit = 20
            speeding = max(0,car.get_speed() - 20)
            #start braking smoothly if too fast
            car.set_brake(speeding / 10.0)
        """
        return self._get_float("Speed")
    def get_rpm(self) -> float:
        """Get the engines current rotations per minute (RPM). Range is 800 (idle) to 8000 (maximum).

        Example:
            >>>
            car = RaceCar.first()
            #dynamically switch gears based on RPM
            gear = car.get_gear()
            if car.get_rpm() > 6000:
                car.set_gear(gear+1)
            elif car.get_rpm() < 3000:
                car.set_gear(gear-1)
        """
        return self._get_float("RPM")
    def get_gear(self) -> int:
        """Get the current gear of the car. Gear 0 is neutral, gears -1 and -2 are backwards and gears 1 to 6 are forwards.

        Example:
            >>>
            car = RaceCar.first()
            #dynamically switch gears based on RPM
            gear = car.get_gear()
            if car.get_rpm() > 6000:
                car.set_gear(gear+1)
            elif car.get_rpm() < 3000:
                car.set_gear(gear-1)

        """
        return self._get_int("Gear")
    def get_fuel(self) -> float:
        """Get the remaining fuel level of the car (in liters).

        Example:
            >>>
            car = RaceCar.first()
            fuel1 = car.get_fuel()
            #boost
            car.apply_boost()
            sleep(1)
            #show fuel cost
            print(fuel1 - car.get_fuel())

        """
        return self._get_float("Fuel")

    # editor functions
    def editor_set_allow_boost(self, is_enabled:bool):
        """Allow or disallow players to apply the nitro booster."""
        self._set_float("setAllowBoost", is_enabled)

    def editor_set_current_fuel(self, val:float):
        """Change the current fuel level of the car."""
        self._set_float("setFuelLevel", val)

    def editor_set_max_speed(self, val:float):
        """Limit the max speed of the car in m/s.

        Args:
            val (float): max speed of the car in m/s.
        """
        self._set_float("setMaxSpeed", val)



class PostProcessVolume(EntityBase["PostProcessVolume"]):
    """Level Editor only. A post-processing volume to change the look of a level."""

    def editor_set_bounds(self, bounds:Vector3, *args:float):
        """Set the bounds of this post process volume. Everything inside is impacted by the post process settings. Negative bounds mean unbounded volume to affect everything.
        """
        self._set_vector3d("setBounds", bounds, add_args=args)

    def editor_set_blend_radius(self, radius):
        self._set_float("setBlendRadius", radius)

    def editor_set_color_saturation(self, value:Vector3, *args:float):
        self._set_vector3d("setColorSaturation", value, add_args=args)
    def editor_set_color_contrast(self, value:Vector3, *args:float):
        self._set_vector3d("setColorContrast", value, add_args=args)
    def editor_set_color_gain(self, value:Vector3, *args:float):
        self._set_vector3d("setColorGain", value, add_args=args)
    def editor_set_color_offset(self, value:Vector3, *args:float):
        self._set_vector3d("setColorOffset", value, add_args=args)
    def editor_set_color_gamma(self, value:Vector3, *args:float):
        self._set_vector3d("setColorGamma", value, add_args=args)

    def editor_set_film_grain_intensity(self, value:float):
        self._set_float("setFilmGrainIntensity", value)

    def editor_set_vignette_intensity(self, value:float):
        self._set_float("setVignetteIntensity", value)



class ExpressiveTextLabel(EntityBase["ExpressiveTextLabel"]):
    """A versatile text label that can take any captions."""

    def set_text(self, new_text:str):
        """Set the text of this label. Supports expressive text markup.
        """
        self._set_string("setText", new_text)

    def set_font_size(self, font_size:int):
        """Set the default font size for this label.
        """
        self._set_int("setFontSize", font_size)

    
class AlarmSiren(EntityBase["AlarmSiren"]):
    """Alarm Siren with strong audio and visual feedback.
    """

    def set_alarm_enabled(self, is_enabled:bool = True):
        """Turn the alarm siren on or off.

        Args:
            is_enabled (bool, optional): Defaults to True to turn alarm on.
        """
        self._set_bool("setAlarmEnabled", is_enabled)

    def get_alarm_enabled(self) -> bool:
        """Returns True if the alarm is currently enabled, else False.
        """
        return self._get_bool("AlarmEnabled")



def get_color_from_map(cmap:Colormaps, x:float) -> Tuple[float,float,float]:
    """Get a color from a named colormap (based on matplotlib's colormaps).

    Args:
        cmap (Colormaps): The selected Colormap
        x (float): Sample position in colormap in [0,1]

    Returns:
        Tuple[float,float,float]: RGB tuple in [0,1]
    """
    cm = colormaps.get_cmap(str(cmap))
    return cm(int(x*255))[0:3]

