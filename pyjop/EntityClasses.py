import copy
import random
import sys
import threading
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    TypedDict,
)
from typing_extensions import Unpack
import asyncio


import psutil
from pyjop.EntityBase import EntityBase, NPArray, await_tick
from pyjop.Enums import *
import numpy as np
import time
import pandas as pd
from io import StringIO

from pyjop.Enums import _parse_color


class ConveyorBelt(EntityBase["ConveyorBelt"]):
    """Conveyor Belt with variable belt speed for transporting objects. Can move objects forwards or backwards. Also has a sensor to check if it is transporting any objects."""

    def set_target_speed(self, speed: float):
        """Set the conveyor's target belt speed to the specified value

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
        self._set_float("setTargetSpeed", float(np.clip(speed, -5.0, 5.0)))

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

    # def on_clicked(self, func:Callable[[EventData],None]) -> EventHandler:
    #     h = EventHandler(func, "EntityClicked", self._build_name())
    #     EntityBase._event_q_handlers.append(h)
    #     return h

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


class LargeConveyorBelt(ConveyorBelt):
    """large conveyor belt. same functions as the regular conveyor belt."""

    pass


class TurnableConveyorBelt(ConveyorBelt):
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
        self._set_float("setTargetRotation", rot)


class RailConveyorBelt(ConveyorBelt):
    """Conveyor Belt with variable belt speed for transporting objects that can be moved along a railway-track."""

    def get_current_position(self) -> float:
        """Get the current position on the railway-track in meters from 0 to length of track

        Example:
            railconv = RailConveyorBelt.first()
            print(railconv.get_current_position())
        """
        return self._get_float("RailPositionCurrentFloat")

    def set_target_position(self, pos: float):
        """set the target position on the railway-track in meters from 0 to length of track.

        Example:
            >>>
            railconv = RailConveyorBelt.first()
            length = railconv.get_rail_track_length()
            #move to center position
            railconv.set_target_position(0.5*length)
        """
        self._set_float("setTargetRailPosition", pos)

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


class ServiceDrone(EntityBase["ServiceDrone"]):
    """Service Drone that can quickly move around. Has a low resolution camera for visual inspection and accurate laser range scanner to detect obstacles."""

    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255]).

        Example:
            >>>
            drone = ServiceDrone.first()
            img = drone.get_camera_frame()
            #show the drone's camera footage in-game
            print(img)
        """
        return self._get_image("CameraFrame")

    # def getDetectionsDeliverable(self)->Union[np.ndarray,None]:
    #     """return an array of all deliverables currently in the camera frame as 2d bounding boxes

    #     Returns:
    #         np.ndarray: columns: x0,y0,x1,y1
    #     """
    #     k = self.__build_name__("DetectionsDeliverable")
    #     if k in self.__inDict__:
    #         return self.__inDict__[k].ArrayData[:,:,0]
    #     return None

    def get_distance_left(self) -> float:
        """Get the value of the left distance sensor in [0,10] meters.

        Example:
            >>>
            drone = ServiceDrone.first()
            ldist = drone.get_distance_left()
            rdist = drone.get_distance_right()
            print(f"left {ldist:.2f}m, right {rdist:.2f}m")
        """
        return self._get_float("DistanceLeft")

    def get_distance_right(self) -> float:
        """Get the value of the right distance sensor in [0,10] meters.

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
        """Set the continuous force of the right thruster to the specified value in [-200,200].

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
        """set the continuous force of the left thruster to the specified value in [-200,200].

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
        """Apply a one-time impulse with the right thruster in [-200,200].

        Example:
            >>>
            drone = ServiceDrone.first()
            #do emergency break
            drone.apply_thruster_impulse_right(-200)
            drone.apply_thruster_impulse_left(-200)
        """
        impulse = float(np.clip(impulse, -200, 200))
        self._set_float("ApplyThrusterImpulseRight", impulse)

    def apply_thruster_impulse_left(self, impulse: float):
        """Apply a one-time impulse force with the left thruster in [-200,200].

        Example:
            >>>
            drone = ServiceDrone.first()
            #do emergency break
            drone.apply_thruster_impulse_right(-200)
            drone.apply_thruster_impulse_left(-200)
        """
        impulse = float(np.clip(impulse, -200, 200))
        self._set_float("ApplyThrusterImpulseLeft", impulse)

    def set_camera_fov(self, fov: float):
        """Set the field-of-view of the camera to the specified angle in [20,160] degrees.

        Example:
            >>>
            drone = ServiceDrone.first()
            #zoom in
            drone.set_camera_fov(40)
            #zoom out
            drone.set_camera_fov(160)
        """
        fov = float(np.clip(fov, 20, 160))
        self._set_float("setCameraFov", fov)


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


class Deliverable(EntityBase["Deliverable"]):
    """Deliverable that can be transported and sent via the DeliveryBox"""

    def get_value(self) -> float:
        """the value of this deliverable. Can change over time."""
        return self._get_float("Value")


class DeliverableSpawner(EntityBase["DeliverableSpawner"]):
    """Spawns deliverables into the SimEnv."""

    def get_time_until_spawn(self) -> float:
        """Returns the time (in seconds) until the next deliverable will be spawned."""
        return self._get_float("TimeUntilSpawn")

    def spawn(self):
        """Spawns the next deliverable. Only works if this spawner is not automated."""
        self._set_void("Spawn")


class DropZone(EntityBase["DropZone"]):
    """drop deliveriables here for delivery"""

    pass


class SmartDoor(EntityBase["SmartDoor"]):
    """can read rfid tags around it and open / close depending on the tags"""

    def get_rfid_tags_in_range(self) -> List[str]:
        """all the rfid tags in range of the door"""
        return self._get_string("RfIdSensorRadiusTags").split(";")

    # password sensor / actuator
    def open_lock(self):
        """unlock the door"""
        self._set_void("OpenLock")

    def close_lock(self):
        """lock the door"""
        self._set_void("CloseLock")

    def get_is_unlocked(self):
        """returns True if the door is open, else false."""
        return self._get_bool("IsUnlocked")


class RangeFinder(EntityBase["RangeFinder"]):
    """Laser range finder sensor that measures distances in meters."""

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

    def editor_set_can_read_rfid_tags(self, can_read_rfid: bool):
        """[Level Editor only] Enable or disable the rfid reader for this range finder."""
        self._set_bool("setCanReadRfidTags", can_read_rfid)


class SmartPictureFrame(EntityBase["SmartPictureFrame"]):
    """Picture display that can dynamically change its content."""

    def set_image_builtin(self, imgName: str):
        """sets the image to the specified built-in image. you can get a list of those via getImagesBuiltIn" """
        self._set_string("DisplaySetImgByName", imgName)

    def set_image_bytes(self, imgBytes: np.ndarray):
        """sets the image to the specified built-in image. you can get a list of those via getImagesBuiltIn" """
        k = self._build_name("DisplaySetImgByBytes")
        nparr = NPArray(k, imgBytes)

        self._set_out_data(k, nparr)

    def set_display_text(self, txt: str):
        """sets the display text to the specified value"""
        self._set_string("DisplaySetText", txt)

    def get_images_builtin(self) -> List[str]:
        """Returns a list of built-in images" """
        return self._get_string("DisplayBuiltinImages").split(";")


class SimEnvManager(EntityBase["SimEnvManager"]):
    """Manage the current SimEnv with this class."""

    def reset(self, stop_code=False):
        """Resets the current SimEnv to it initial state at time=0. Optionally stop all running Python code.

        Example:
            >>>
            SimEnvManager.first().reset()
        """
        if stop_code:
            self._set_void("ResetSimEnv")
        else:
            self._set_void("ResetSimEnvNoStop")
        # wait for next update loop
        await_tick()

    def get_sim_time(self) -> float:
        """Returns time in seconds that the current SimEnv has been running for (since last reset).

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_sim_time())
        """
        return self._get_float("SimTime")

    def get_time_remaining(self) -> float:
        """Returns time in seconds that is remaining to stay within the optional time-limit of the current SimEnv.

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_time_remaining())
        """
        return self._get_float("TimeRemaining")

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

    def get_parameter(self, name: str) -> float:
        """Get a named parameter for the current SimEnv.

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_available_parameters())
            #choose the parameter you want then call
            #lvl.get_parameter("SOME_PARAM_NAME")
        """
        return self._get_float("p" + name)

    def get_available_parameters(self) -> List[str]:
        """Returns a list of all named parameters in the current SimEnv.

        Example:
            >>>
            lvl = SimEnvManager.first()
            print(lvl.get_available_parameters())
            #choose the parameter you want then call
            #lvl.get_parameter("SOME_PARAM_NAME")
        """
        return self._get_string("LevelParameters").split(";")  # not implemented yet

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


def sleep(seconds: float = 0):
    """Delay execution for a given number of seconds. Is automatically scaled with SimEnv time dilation.

    Example:
        >>>
        sleep(1.5) #sleeps for 1.5 SimEnv seconds
        sleep() #sleep unitl next simulation round trip tick
    """
    if seconds is None or seconds <= 0:
        # sleep tick
        await_tick()
        return
    dseconds = 0.21

    m = SimEnvManager.first()
    start = m.get_sim_time()
    while True:
        step = min(0.1, seconds - dseconds)
        if step <= 0:
            break
        time.sleep(step)
        dtime = m.get_sim_time() - start
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


def print(*args, col: Colors = Colors.White) -> None:
    """print the supplied message to the in-game log. Can also print images directly in-game. Takes optional color for the print message.


    Args:
        col (Colors, optional): RGB color or css color name of the print message. Defaults to white (1.0,1.0,1.0).

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
        EntityBase._log_debug_static(msg, col=_parse_color(col))
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

    # asyncio.get_event_loop().run_in_executor
    ui.run(
        host="127.0.0.1",
        port=18085,
        show=False,
        dark=True,
        reload=False,
        viewport=f"width={width}, height={height}, initial-scale=1",
        title=title,
    )
    # ui.run(host="127.0.0.1",port=18085,show=False, dark=True, reload=False, viewport="width=800, height=600, initial-scale=1")


class Piano(EntityBase["Piano"]):
    """Piano sequencer that plays piano sample sounds in-game."""

    def play_note(self, note: MusicNotes) -> None:
        """play the specified note (from C1 to B7, with s or # for sharps and b for molls).

        Args:
            note (MusicNotes): Note to play as string or from MusicNotes Enum

        Example:
            >>>
            Piano.first().play_note("C#4")
            sleep(1)
            Piano.first().play_note(MusicNotes.Cs4)
        """
        self._set_string("PlayNote", note)

    def play_note_in_octave(self, base_note: str, octave: int) -> None:
        """play the specified note (from C to B, with s or # for sharps and b for molls) on the specified octave (1 to 7)

        Args:
            base_note (str): Note to play as string. Valid values [C,D,E,F,G,A,B], with suffix s or # for sharps and b for molls
            octave (int): Octave to play the note in. Valid values: [1,...,7]

        Example:
            >>>
            Piano.first().play_note_in_octave("C#",4)
            sleep(1)
        """
        self._set_string("PlayNote", base_note + str(octave))

    # new method to choose instrument


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
        self._set_vector("setColor", _parse_color(color))

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

    def set_enabled(self, enabled=True):
        """Turn the light on or off immediately.

        Args:
            enabled (bool, optional): True to turn the ligh on or False to turn it off. Defaults to True.

        Example:
            >>>
            lights = SmartLight.find_all()
            #turn off all lights
            for l in lights:
                l.set_enabled(False)
        """
        self._set_bool("setEnabled", enabled)

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
    """Dynamic speaker that can play a selection of builtin songs or songs by url / filename."""

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

    def set_sound_by_name(self, name: str):
        """Play one of builtin songs / playlists that come with this speaker.

        Args:
            name (str): name of the builtin song. Must be one of the names returned by get_builtin_sounds.

        Example:
            >>>
            speaker = SmartSpeaker.first()
            speaker.set_sound_by_name("Joy's Playlist")
        """
        if name:
            self._set_string("setSoundByName", name)

    def get_builtin_sounds(self):
        """Get a list of builtin songs / playlists that come with this speaker. Play them with set_sound_by_name.

        Example:
            >>>
            speaker = SmartSpeaker.first()
            sounds = speaker.get_builtin_sounds()
            print(sounds)
            if sounds:
                speaker.set_sound_by_name(sounds[0])
        """
        return self._get_string("BuiltinSounds").split(";")

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


class GPSWaypoint(EntityBase["GPSWaypoint"]):
    """GPS waypoint which you can query for its location."""

    def get_location(self):
        """get this waypoint's location in XYZ (see SimEnv description for unit description)"""
        return self._get_vector("Location")


class FactBox(EntityBase["FactBox"]):
    """A small lootbox containing a collectible factsheet. Find it and collect all the factsheets!"""

    def get_distance_to_player(self):
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


class SmartCamera(EntityBase["SmartCamera"]):
    """Camera with adjustable zoom that can return RGB or depth images (depends on SimEnv settings)."""

    def set_zoom_fov(self, fov: float):
        """set the field-of-view (FOV) (min/max values depend on SimEnv settings)  of this camera to zoom in / out"""
        self._set_float("SetFOV", fov)

    def get_camera_frame(self) -> np.ndarray:
        """Return the current camera frame as a numpy array of size 256x256x3 (RGB color image with width=256 and height=256 and values in [0...255])."""
        return self._get_image("CameraFrame")

    def get_depth_frame(self) -> np.ndarray:
        """get the current camera image as a raw depth image in centimeters (divide by maxrange to get a grayscale image for display)"""
        return self._get_image("DepthFrame", 1)


class RobotArm(EntityBase["RobotArm"]):
    """Programmable robot arm with inverse kinematics control"""

    def set_grabber_location(self, vec):
        """set the location in relative XYZ of the grabber arm endpoint"""
        self._set_vector("SetTargetLocation", vec)

    def get_is_grabbing(self) -> bool:
        """True if the grabber is currently grabbing somethng successfully, else False"""
        return self._get_bool("HasGrabbed")

    def get_is_moving(self) -> bool:
        """True if the arm is currently moving towards a target location, else False"""
        return self._get_bool("IsMoving")

    def try_grab(self):
        """try to grab the closest object to the grabber endpoint"""
        self._set_void("TryGrab")

    def release_grabber(self):
        """release any grabbed objects"""
        self._set_void("ReleaseGrabber")


class CsvData(EntityBase["CsvData"]):
    """base class for all SimEnv csv databases"""

    def get_data(self, table_name: str) -> pd.DataFrame:
        """get all available data from this SimEnv csv database as a Pandas DataFrame"""
        self.resend_data()
        return pd.read_csv(StringIO(self._get_string(table_name + "DataTable")))


class WineData(CsvData):
    """Database with wine quality csv data and an integrated wine quality scanner for new bottles of wine"""

    def get_current_wine_quality(self) -> List[str]:
        """get the quality of the currently scanned bottle of wine as list of strings"""
        return self._get_string("ScannedFeatures").split(",")


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
        self._set_vector("Launch", (x, y, z))

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
        return self._get_image("SatelliteCameraFrame")


class Artillery(EntityBase["Artillery"]):
    """Artillery launcher."""

    def set_target_elevation(self, elevation: float):
        """Set the target launch elevation in degree within [5,60].

        Args:
            elevation (float): launch elevation in degree within [5,60]

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_elevation(60)
            arty.set_target_orientation(30)
            #wait until target reached
            sleep(10)
            arty.fire(400)
        """
        self._set_float("setTargetElevation", elevation)

    def set_target_orientation(self, orientation: float):
        """Set the target launch orientation in degree within [0,360].

        Args:
            orientation (float): launch orientation in degree within [0,360]

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_elevation(60)
            arty.set_target_orientation(30)
            #wait until target reached
            sleep(10)
            arty.fire(400)
        """
        self._set_float("setTargetElevation", orientation)

    def fire(self, launch_power: float):
        """Fire a shell with the specified launch power within [200,1000].

        Args:
            launch_power (float):  launch power within [200,1000]

        Example:
            >>>
            arty = Artillery.first()
            arty.set_target_elevation(60)
            arty.set_target_orientation(30)
            #wait until target reached
            sleep(10)
            arty.fire(400)
        """
        self._set_float("Fire", launch_power)

    # TODO: add reload function?


class PinHacker(EntityBase["PinHacker"]):
    """Brute force hacking device for PIN numbers"""

    def enter_pin(self, pin: int):
        """Enter a candidate PIN into the hacking device.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct(p):
                print(str(p) + " is correct!")
            elif hacker.get_is_greater(p):
                print(str(p) + " is greater than the real pin!")
            else:
                print(str(p) + " is smaller than the real pin!")
        """
        self._set_int("EnterPin", pin)

    def get_is_correct(self) -> bool:
        """Check wether the last entered pin was correct or not.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct(p):
                print(str(p) + " is correct!")
            elif hacker.get_is_greater(p):
                print(str(p) + " is greater than the real pin!")
            else:
                print(str(p) + " is smaller than the real pin!")
        """
        return self._get_bool("IsCorrect")

    def get_is_greater(self) -> bool:
        """Check wether the last entered pin is greater than the real pin.

        Example:
            >>>
            hacker = PinHacker.first()
            hacker.enter_pin(pin=123)
            #wait for the hacker to process and send results back. duration depends on your tick rate.
            sleep() #sleep without a duration waits for a complete round-trip
            #check the results
            if hacker.get_is_correct(p):
                print(str(p) + " is correct!")
            elif hacker.get_is_greater(p):
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
        await_tick()
        if self.get_is_correct():
            return "correct"
        elif self.get_is_greater():
            return "greater"
        else:
            return "less"


class VoxelBuilder(EntityBase["VoxelBuilder"]):
    """Spawn Voxels / Cubes / Boxes at the specified location and the specified color."""

    def build(self, location=(0.0, 0.0, 0.0), color=Colors.Grey, simulate_physics=True):
        """Spawn Voxels / Cubes / Boxes at the specified location and the specified color.

        Args:
            location: tuple x (forward), y (right), z (up) in meters.
            color: RGB color to apply to the mesh. Either RGB tuple or Colors name.
            simulate_physics (bool): True to simulate physics, false to make the object stationary.

        Example:
            >>>
            builder = VoxelBuilder.first()
            builder.build((1,1,5))
            sleep(3)
            builder.build((1,1,6),Colors.Red)
        """
        if not hasattr(location, "__len__"):
            location = (location, location, location)
        elif len(location) == 1:
            location = (location[0], location[0], location[0])
        loc = {"x": location[0], "y": location[1], "z": location[2]}

        color = _parse_color(color)
        if len(color) == 3:
            color = {"r": color[0], "g": color[1], "b": color[2], "a": 1.0}

        self._set_json(
            "BuildVoxel",
            {"Location": loc, "Color": color, "bPhysics": simulate_physics},
            False,
        )


def _get_kwargs(kwargs: Dict[str, Any]):
    loc = kwargs.get("location", (0.0, 0.0, 0.0))
    if not hasattr(loc, "__len__"):
        loc = (loc, loc, loc)
    elif len(loc) == 1:
        loc = (loc[0], loc[0], loc[0])
    loc = {"x": loc[0], "y": loc[1], "z": loc[2]}
    scale = kwargs.get("scale", (1.0, 1.0, 1.0))
    if not hasattr(scale, "__len__"):
        scale = (scale, scale, scale)
    elif len(scale) == 1:
        scale = (scale[0], scale[0], scale[0])
    scale = {"x": scale[0], "y": scale[1], "z": scale[2]}
    rot = kwargs.get("rotation", (0.0, 0.0, 0.0))
    if not hasattr(rot, "__len__"):
        rot = (rot, rot, rot)
    elif len(rot) == 1:
        rot = (rot[0], rot[0], rot[0])
    rot = {"roll": rot[0], "pitch": rot[1], "yaw": rot[2]}
    duration = kwargs.get("duration", 0.0)
    mcol = _parse_color(kwargs.get("color", ""))
    set_color = len(mcol) > 2
    if len(mcol) == 3:
        mcol = {"r": mcol[0], "g": mcol[1], "b": mcol[2], "a": 1.0}
    return {
        "Location": loc,
        "Rotation": rot,
        "Scale": scale,
        "Duration": duration,
        "Color": mcol,
        "bSetColor": set_color,
    }


class LevelEditor(EntityBase["LevelEditor"]):
    """Interface to the level editor. Only accessible in the Level Editor View."""

    def __init__(self, entity_name: str, **kwargs) -> None:
        super().__init__(entity_name, **kwargs)
        self._goal_funcs: Dict[str, Callable[[str], None]] = {}
        self._dynamic_funcs: Dict[str, Callable[[float,float], bool]] = {}
        self._dynamic_threads: Dict[str, threading.Thread] = {}
        self._goal_threads: Dict[str, threading.Thread] = {}
        self._on_level_reset_handler: Optional[Callable[[], None]] = None

        self._last_tick = 0
        self._current_tick = 0

    @classmethod
    def first(cls) -> "LevelEditor":
        inst = super().first()
        if inst is None:
            print("no level editor found, exiting")
            await_tick(2)
            from pyjop.Network import SimEnv

            SimEnv.disconnect()
            exit()
        return inst

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
        await_tick()

    # build functions:

    def spawn_entity(self, entity_type: SpawnableEntities, unique_name="", **kwargs):
        """Spawns a smart entity of the given type with the specified transform.

        Args:
            entity_type: type name, e.g. SpawnableEntities.ConveyorBelt
            unique_name (str): entity name, empty for automatic. should be unique
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor

        Example:
            >>>
            editor.spawn_entity(SpawnableEntities.ConveyorBelt,"belt2",location = (5.5,0,0))
        """
        args = _get_kwargs(kwargs)
        self._set_json(
            "SpawnEntity",
            args | {"EntityClass": str(entity_type), "UniqueName": unique_name},
            True,
        )

    def spawn_static_mesh(
        self,
        mesh: SpawnableMeshes,
        unique_name="",
        material=SpawnableMaterials.Default,
        simulate_physics=False,
        **kwargs,
    ):
        """Spawns the specified static mesh with the optional material

        Args:
            mesh (str): the mesh to spawn, e.g. SpawnableMeshes.Cube
            unique_name (str): optional unique name for the mesh. Should only be non-empty if you need access to this mesh via script later
            material (str): name of material to apply to the mesh, SpawnableMaterials.Default keeps default material
            color (tuple): RGB color to apply to the mesh. Either RGB tuple or Colors name
            simulate_physics (bool): True to simulate physics
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree
            scale: tuple x (forward), y (right), z (up) as factor
        """

        args = _get_kwargs(kwargs)

        self._set_json(
            "SpawnEntity",
            args
            | {
                "EntityClass": "StaticMesh",
                "UniqueName": unique_name,
                "Mesh": str(mesh),
                "Material": str(material),
                "bPhysics": simulate_physics,
            },
            True,
        )  # mark as placementspawn ingame

    # def set_level_metadata(self, name:str, description:str, category:str, )

    def specify_goal(
        self,
        unique_name: str,
        display_text: str,
        update_func: Callable[[str], None],
        goal_value: float = 1.0,
        is_resettable: bool = True,
        is_optional: bool = False,
    ):
        """specifiy a goal for this level and how it should be evaluated

        Args:
            unique_name (str): unique name of the goal
            display_text (str): The text as displayed to the player in-game
            update_func (Callable[[str],None]): function to evaluate the current goal. must have a single parameter which will be filled with the unique name of this goal. should call set_goal_progress or set_goal_state internally.
            goal_value (float): The relative value of this goal. If the sum of all completed goals is >1, then the level is completed. Ignored for optional goals (see below).
            is_resettable (bool): Whether the progress of this goal will be set to 0 / Open on a level reset
            is_optional (bool): Whether this is a mandatory goal or one of the optional goals
            

        Example:
            >>>
            def move_it_goal(goal_name:str):
                if ConveyorBelt.find("belt2").get_is_transporting():
                    editor.set_goal_state(goal_name,GoalState.Success)
                elif ConveyorBelt.find("belt1").get_is_transporting()==False:
                    editor.set_goal_state(goal_name,GoalState.Fail,"Better reset the level!")

            editor.specify_goal("moveit", "move the box from one to the other conveyor belt", move_it_goal, 1, True, False)
        """

        self._set_json(
            "SpecifyGoal",
            {
                "UniqueName": unique_name,
                "DisplayText": display_text,
                "GoalValue": goal_value,
                "bResettable": is_resettable,
                "bOptional": is_optional,
            },
            True,
        )

        self._goal_funcs[unique_name] = update_func

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

    # def set_dynamic_func(self, unique_name: str, dynamic_func: Callable[[], bool]):
    #     """set a named dynamic function that manipulates / observes the level at runtime

    #     Args:
    #         unique_name (str): unique name / id of the function
    #         dynamic_func (Callable[[],bool]): reference to the function code. Should return True to stop looping when it is done and False otherwise

    #     Example:
    #         >>>
    #         def blow_stuff_up():
    #             sleep(10)
    #             res = input("show explosion?")
    #             if res=="yes":
    #                 editor.show_vfx(SpawnableVFX.Explosion)
    #                 editor.play_sound(SpawnableSounds.Explosion)
    #             elif res == "stop":
    #                 print("stop blowing stuff up")
    #                 return True

    #         editor.set_dynamic_func("print_stuff", blow_stuff_up)
    #     """
    #     self._dynamic_funcs[unique_name] = dynamic_func

    def on_level_reset(self, func: Callable[[], None]):
        """register a function that fires everytime the level is reset"""
        self._on_level_reset_handler = func

    def on_begin_play(self, func: Callable[[], None]):
        """register a function that executes once on begin play after the level has been fully constructed

        Args:
            func (Callable[[],None]): the function to register
        """

        def wrapper(gametime:float,deltatime:float):
            func()
            return True

        self._dynamic_funcs["on_begin_play_84654"] = wrapper

    def on_tick(self, func: Callable[[float,float], None]):
        """register a function that executes on every data exchange with the SimEnv. Provides current gametime and time since last tick call (both in seconds) as two parameters.

        Args:
            func (Callable[[float,float], None]): the function to register. Provides current gametime and time since last tick call (both in seconds) as two parameters.
        """
        def wrapper(gametime:float,deltatime:float):
            func(gametime,deltatime)
            return False
        self._dynamic_funcs["on_tick_84654"] = wrapper
        

    # run / inference functions
    def show_vfx(self, vfx: SpawnableVFX, **kwargs):
        """Shows the specified vfx effect at run-time

        Args:
            vfx (str): the vfx effect to play
            color (tuple): optional RGB color to apply to the vfx. Either RGB tuple or Colors name
            location: tuple x (forward), y (right), z (up) in meters
            rotation: tuple roll, pitch, yaw in degree

        Example:
            >>>
            editor.show_vfx(SpawnableVFX.Explosion)
        """

        args = _get_kwargs(kwargs)

        self._set_json(
            "SpawnEntity", args | {"EntityClass": "VFX", "VFX": str(vfx)}, True
        )

    def play_sound(self, sfx: SpawnableSounds, volume=1.0, is_ui=False, **kwargs):
        """Plays the specified sound effect at run-time

        Args:
            sfx (str): the sound effect to play
            volume (float): relative volume of the sound, between 0 and 1
            is_ui (boolean): is it a UI sound (2D), then True, else (3D sound) False
            location: tuple x (forward), y (right), z (up) in meters

        Example:
            >>>
            editor.play_sound(SpawnableSounds.Explosion, is_ui=True)
        """

        args = _get_kwargs(kwargs)

        self._set_json(
            "SpawnEntity",
            args
            | {"EntityClass": "SFX", "SFX": str(sfx), "Volume": volume, "bUI": is_ui},
            True,
        )

    def show_image(self, image: SpawnableImages, is_ui=True, duration=-1.0, **kwargs):
        """Shows the specified image at run-time.

        Args:
            image (SpawnableImages): Image to show.
            is_ui (bool, optional): True to show directly on top of the UI / HUD of the player, False to show as a 3D object in the world. Defaults to True.
            duration: duration in seconds. Defaults to -1, which is infinite duration (until player clicks).

        Example:
            >>>
            editor.show_image(SpawnableImages.JoyOfProgrammingLogo)
        """
        args = _get_kwargs(kwargs)
        self._set_json(
            "SpawnEntity",
            args
            | {
                "EntityClass": "Image",
                "Image": str(image),
                "bUI": is_ui,
                "Duration": duration,
            },
            True,
        )

    def show_text(self, text: str, is_ui=True, duration=-1.0, **kwargs):
        """Shows the supplied text on-screen with a typewriter effect.

        Args:
            text (str): text to display
            is_ui (bool, optional): True to show directly on top of the UI / HUD of the player, False to show as a 3D object in the world. Defaults to True.
            duration: duration in seconds. Defaults to 0, which is automatic depending on text length. Negative values are infinite duration (until player clicks).
        """
        args = _get_kwargs(kwargs)
        self._set_json(
            "SpawnEntity",
            args
            | {"EntityClass": "Text", "Text": text, "bUI": is_ui, "Duration": duration},
            True,
        )

    def get_goal_progress(self, unique_name: str):
        """get the relative progress (0.0 to 1.0) of the specified goal"""
        return self._get_float("GoalProgress" + unique_name)

    def get_goal_state(self, unique_name: str) -> GoalState:
        """get the state of the specified goal"""
        val = self._get_string("GoalProgress" + unique_name)
        if val in GoalState:
            return GoalState[val]
        return GoalState.Unknown

    def get_all_spawns(self) -> Sequence[str]:
        """get a list of all the uniquely named spawns created with the level editor"""
        return self._get_string("AllSpawns").split(";")

    def get_location(self, unique_name: str):
        """get the current location of the named entity/mesh that you spawned from the level editor."""
        return self._get_vector("Location" + unique_name)

    def get_rotation(self, unique_name: str):
        """get the current rotation of the named entity/mesh that you spawned from the level editor."""
        return self._get_vector("Rotation" + unique_name)

    def get_velocity(self, unique_name: str):
        """get the current linear velocity (in m/s) of the named entity/mesh that you spawned from the level editor. Only works physically simulated entities."""
        return self._get_vector("Velocity" + unique_name)

    def get_angular_velocity(self, unique_name: str):
        """get the current angular velocity (in deg/s) of the named entity/mesh that you spawned from the level editor. Only works physically simulated entities."""
        return self._get_vector("AngularVelocity" + unique_name)

    def get_mass(self, unique_name: str):
        """get the mass in kg of the named entity/mesh that you spawned from the level editor. Only works physically simulated entities."""
        return self._get_float("Mass" + unique_name)

    def get_bounds(self, unique_name: str) -> np.ndarray:
        """get the current axis aligned bounding box (AABB) of the named entity/mesh that you spawned from the level editor. Returns vector of centerX,centerY,centerZ,extendX,extendY,extendZ in meters"""
        # use https://github.com/adamlwgriffiths/Pyrr
        k = self._build_name("Bounds" + unique_name)
        if k in self._in_dict:
            return self._in_dict[k].array_data[:6, 0, 0]
        return np.asarray([0, 0, 0, 0, 0, 0], dtype=np.float32)

    def set_location(self, unique_name: str, new_location: Tuple[float, float, float]):
        """teleport / set the current location of the named entity/mesh that you spawned from the level editor."""
        self._set_json(
            "SetLocation", {"UniqueName": unique_name, "Location": new_location}, True
        )

    def set_rotation(self, unique_name: str, new_rotation: Tuple[float, float, float]):
        """rotate the named entity/mesh that you spawned from the level editor."""
        self._set_json(
            "SetRotation", {"UniqueName": unique_name, "Location": new_rotation}, True
        )

    def set_clickable(self, unique_name: str, is_clickable: bool):
        """set the entity that you spawned from the level editor to be clickable by the player or not."""
        self._set_json(
            "SetClickable",
            {"UniqueName": unique_name, "bClickable": is_clickable},
            True,
        )

    def set_enabled(self, unique_name: str, is_enabled: bool, component_name=""):
        """completely enable or disable the named entity that you spawned from the level editor. if component_name is specified, only enable or disable that component."""
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
        """hide or show the named entity that you spawned from the level editor."""
        self._set_json(
            "SetHidden", {"UniqueName": unique_name, "bHidden": is_hidden}, True
        )

    def destroy(self, unique_name: str):
        """destroy / remove the entity/mesh that you spawned from the level editor."""
        self._set_string("Destroy", unique_name, True)

    def clear_all(self):
        """clears the entire level"""
        self._set_void("ClearAll")

    # ideas: set player location / viewport, transition to other camera, switch fps/rts mode

    # level editor runs in its own process
    def run_editor_level(self):
        """Start the custom level script. Must be the last line of code in a custom level script."""
        m = SimEnvManager.first()
        sleep(0.5)
        m._set_void("ConstructionCompleted")

        from pyjop.Network import SimEnv

        if (LevelEditor._is_construct_only()) or (
            not self._dynamic_funcs and not self._goal_funcs
        ):
            SimEnv.disconnect()
            return
        # run the current level and check goals and evaluate dynamic funcitons. all highly parallel
        last_sim_time = 999
        sleep(1)
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
            # handle level reset
            if (
                last_sim_time > m.get_sim_time()
                and self._on_level_reset_handler is not None
            ):
                self._on_level_reset_handler()
            last_sim_time = m.get_sim_time()
            if m.get_is_completed():
                break

        SimEnv.disconnect()

    def _run_dynamics(self):
        if not self._dynamic_funcs:
            return
        dyn_funcs = copy.deepcopy(self._dynamic_funcs)
        # run all dyn funcs in sequentially
        for k, f in dyn_funcs.items():
            if f(self._current_tick, self._current_tick - self._last_tick):
                del self._dynamic_funcs[k]

    def _check_goals(self):
        if not self._goal_funcs:
            return
        for k, f in self._goal_funcs.items():
            f(k)  # run it


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
        """set the intensity for the entire LED strip to the specified relative value in [0,1]

        Args:
            intensity (float): relative intensity in [0,1]

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_intensity(0.1)
        """
        self._set_float("setIntensity", intensity)

    def set_start_location(self, location=(0.0, 0.0, 0.0)):
        """Set the relative start location of the led strip. Limited to an +/- 2m adjustment in all directions

        Args:
            location (tuple): relative start location of the led strip. Limited to an +/- 2m adjustment in all directions. Defaults to (0.0,0.0,0.0).

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_start_location((-1,0,1))
        """
        self._set_vector("setStartLocation", location)

    def set_end_location(self, location=(1.0, 0.0, 0.0)):
        """Set the relative end location of the led strip. Limited to an +/- 2m adjustment in all directions

        Args:
            location (tuple): relative end location of the led strip. Limited to an +/- 2m adjustment in all directions. Defaults to (1.0,0.0,0.0).

        Example:
            >>>
            leds = LEDStrip.first()
            leds.set_start_location((2,0,0))
        """
        self._set_vector("setEndLocation", location)

    def get_num_leds(self):
        """Get the number of addressable LEDs on this LED strip."""
        return self._get_int("NumLeds")


class Maze(EntityBase["Maze"]):
    """A 2D maze"""

    def get_maze_data(self):
        """Get the full maze as a 2D array. Can be none for certain levels."""
        k = self._build_name("MazeData")
        if k in self._in_dict:
            return self._in_dict[k].array_data[:, :, 0]

    def get_maze_size(self) -> Tuple[int, int]:
        """Get the size (width x height) of the maze"""
        k = self._build_name("MazeSize")
        if k in self._in_dict:
            return (
                int(self._in_dict[k].array_data[0, 0, 0]),
                int(self._in_dict[k].array_data[0, 0, 0]),
            )
        return (0, 0)

    def editor_generate_maze(self, width: int, height: int):
        """[Level Editor only] Generate a new maze.

        Args:
            width (int): width in meters
            height (int): height (or length) in meters
        """

        if width % 2 == 0:
            width -= 1
        if height % 2 == 0:
            height -= 1
        width = clamp(width, 5, 255)
        height = clamp(height, 5, 255)
        self._set_json("GenerateMaze", {"width": width, "height": height})

    def editor_get_shortest_path(self):
        """[Level Editor only] Get the shortest path from entry to exit. Returns Nx2 ndarray with x,y coordinates.
        """
        k = self._build_name("SSSP")
        if k in self._in_dict:
            self._post_API_call()
            return self._in_dict[k].array_data[:,:,0]

    def editor_set_shortest_path_visible(self, is_visible:bool):
        """[Level Editor only] Show the shortest path in-game"""
        self._set_bool("setPathVisible", is_visible)

class DialupPhone(EntityBase["DialupPhone"]):
    """An old dialup phone with audible dial tones.
    """

    def get_last_number_audio(self):
        """Get raw PCM Wave audio data of the dial tones for the last number that was dialed
        """
        k = self._build_name("LastNumberAudio")
        if k in self._in_dict:
            self._post_API_call()
            return self._in_dict[k].array_data.squeeze()
        return None

    def dial_number(self, number:str):
        """dial the specified number. can later retrieve the recorded dial tones with get_last_number_audio"""
        self._set_string("DialNumber", number)
