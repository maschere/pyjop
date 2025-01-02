# pip wheel . --no-deps
import base64
import builtins
import json
import queue
import random
import threading
from io import BytesIO
from itertools import count

builtins.print(".", end="")
from collections.abc import Callable, Sequence
from types import FrameType, ModuleType, SimpleNamespace
from typing import (
    Any,
    Final,
    Generic,
    TypeVar,
)

import numpy as np
from PIL import Image

builtins.print(".", end="")
import skimage

builtins.print(".", end="")
import sys
import time

import skimage.transform
import skimage.util

builtins.print(".", end="")
import contextlib
import inspect
from datetime import datetime
from inspect import currentframe, getframeinfo
from queue import Queue

from pyjop.Enums import Colors, VerbosityLevels
from pyjop.Vector import Rotator3, Vector3


class NPArray:
    """numpy array for transfer over tcp socket."""

    _MAGIC_BYTES: Final = b"Ihg\x1c"
    _NAME_LEN: Final = 128
    _PRE_HEADER: Final = 17
    _HEADER_SIZE: Final = _NAME_LEN + _PRE_HEADER

    time_id_it = count(start=0, step=1)

    def __init__(self, name: str, arr: np.ndarray) -> None:
        self.unique_name = name
        self.array_data: np.ndarray = arr
        self.time_id = 0

    @classmethod
    def from_msg(cls, msg_b):
        # skip 4 bytes if magic bytes still there
        if msg_b[:4] == NPArray._MAGIC_BYTES:
            msg_b = msg_b[4:]
        msg_len = int.from_bytes(msg_b[:4], "little")
        w = int.from_bytes(msg_b[4:8], "little")
        h = int.from_bytes(msg_b[8:12], "little")
        c = int.from_bytes(msg_b[12:16], "little")
        dt = np.uint8 if msg_b[16] == 0 else np.float32
        name = str.strip(
            msg_b[NPArray._PRE_HEADER : NPArray._HEADER_SIZE].decode("ascii"),
        )
        msg_b = msg_b[NPArray._HEADER_SIZE : NPArray._HEADER_SIZE + msg_len]
        if msg_len > 0:
            arr = np.ndarray(shape=(h, w, c), dtype=dt, buffer=msg_b)
        else:
            arr = np.zeros((1, 1, 1), dtype=dt)
        return NPArray(name, arr)

    def pack_msg(self) -> bytearray:
        out = bytearray()
        if self.array_data.dtype not in (np.uint8, np.float32):
            self.array_data = self.array_data.astype(np.float32)

        name = self.unique_name.ljust(NPArray._NAME_LEN, " ")[: NPArray._NAME_LEN]
        arr = self.array_data.squeeze()
        arr_b = arr.tobytes()

        out += NPArray._MAGIC_BYTES  # 4 magic bytes
        # 4bytes len
        out += int.to_bytes(len(arr_b), 4, "little")
        if len(arr.shape) == 0:
            arr = np.expand_dims(arr, 0)
        # 4bytes w
        out += int.to_bytes(arr.shape[0], 4, "little")
        # 4bytes h
        if len(arr.shape) > 1:
            out += int.to_bytes(arr.shape[1], 4, "little")
        else:
            out += int.to_bytes(1, 4, "little")
        # 4bytes c
        if len(arr.shape) > 2:
            out += int.to_bytes(arr.shape[2], 4, "little")
        else:
            out += int.to_bytes(1, 4, "little")
        # 1byte dtype
        if arr.dtype == np.uint8:
            out += b"\x00"
        else:
            out += b"\x01"
        # fixed length name
        # 128asci bytes name
        out += name.encode("ascii")
        # variable array
        out += arr_b
        return out

    def get_string(self) -> str:
        return (
            self.array_data.squeeze()
            .tobytes()
            .decode("ascii", errors="replace")
            .strip()
        )

    def get_json_dict(self) -> dict[str, Any]:
        js = {}
        raw = self.array_data.squeeze().tobytes().decode("utf-8")
        with contextlib.suppress(Exception):
            js = json.loads(raw)
        return js

    def get_bool(self) -> bool:
        return int(self.array_data[0][0][0]) != 0

    def get_float(self) -> float:
        return float(self.array_data[0][0][0])


def _is_custom_level_runner() -> bool:
    import sys

    if len(sys.argv) > 1:
        return "custom_level_running" in sys.argv
    return False


def _internal_python_process() -> bool:
    import sys

    if len(sys.argv) > 1:
        return "internal_python" in sys.argv
    return False


from itertools import count


def _stack_size(size: int = 2):
    frame = sys._getframe(size)

    for size in count(size):
        frame = frame.f_back
        if not frame:
            return size
    return None


def is_non_spawnable(cls):
    return "Base" in cls.__name__


class JoyfulException(Exception):
    """Custom exception for JOY OF PROGRAMMING."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


T = TypeVar("T")


class BaseEventData:
    """Event data returned by several entities."""

    def __init__(self, new_vals: "dict[str, Any]") -> None:
        self.at_time: float = new_vals["time"]
        """Simulation time in seconds when this event occurred"""
        self.entity_type: str = new_vals["entityType"]
        """The type of the entity that triggered this event."""
        self.entity_name: str = new_vals["entityName"]
        """The name of the entity that triggered this event."""
        self.rfid_tag: str = new_vals["rfidTag"]
        """The (optional) RFID tag of this entity."""

    def __repr__(self) -> str:
        s = ""
        for k, v in self.__dict__.items():
            s += f"{k}: {v!s}\n"
        return s

    def __str__(self) -> str:
        return self.__repr__()


class EntityBase(Generic[T]):
    """Base class for all entities in the SimEnv. Use Find or FindAll to get the entities you want to control and program them."""

    _out_dict: dict[str, list[NPArray]] = {}
    _out_time_dict: dict[str, tuple[int, int]] = {}
    _in_time_dict: dict[str, tuple[int, int]] = {}
    _in_dict: dict[str, NPArray] = {}
    _entity_dict: dict[str, "EntityBase"] = {}
    _custom_classes: dict[str, type["EntityBase"]] = {}
    _BLANK_IMAGE: Final = np.zeros((64, 64, 3), dtype=np.uint8)
    _TIMEOUT: Final = 5
    last_receive_at = datetime.utcnow()

    last_send_at = datetime.utcnow()
    _is_debug_paused = False

    sendlock = threading.Lock()

    _event_queue: Queue[tuple[NPArray, Callable[[T, float, Any], None]]] = Queue()

    @staticmethod
    def _set_out_data(k: str, arr: NPArray, append=False, max_appends=0) -> None:
        EntityBase.sendlock.acquire()
        arr.time_id = next(NPArray.time_id_it)
        needs_await = False
        if append:
            if k not in EntityBase._out_dict:
                EntityBase._out_dict[k] = [arr]
            else:
                EntityBase._out_dict[k].append(
                    arr,
                )  # TODO change append to also allow specific number of max appends
                if max_appends > 0 and len(EntityBase._out_dict[k]) > max_appends:
                    needs_await = True
        else:
            EntityBase._out_dict[k] = [arr]
        EntityBase.sendlock.release()
        if needs_await:
            _dispatch_events()
            await_receive()
        if not append and not k.startswith("SimEnvManager.Current"):
            t0, c0 = 0, 0
            if k in EntityBase._out_time_dict:
                t0, c0 = EntityBase._out_time_dict[k]
            t1 = time.time_ns()
            if t1 < t0 + 3 * 1e6:  # 3ms
                EntityBase._out_time_dict[k] = (t1, c0 + 1)
                if c0 > 20:
                    EntityBase._log_debug_static(
                        f"Setter rate limit: use sleep() or SimEnv.run_main() to repeatedly call commands like '{k}'",
                        Colors.Yellow,
                    )
                    _dispatch_events()
                    await_receive()
            else:
                EntityBase._out_time_dict[k] = (t1, 0)

    @staticmethod
    def _sync_incoming_data(nparr: NPArray) -> None:
        if nparr.unique_name.count(".") != 2:
            return
        # get identifiers
        type_name, entity_name, prop_name = nparr.unique_name.split(".")
        fullname = type_name + "." + entity_name

        # ensure is in entity dict
        if fullname in EntityBase._entity_dict:
            # update sync timestamp
            EntityBase._entity_dict[fullname].last_sync_utc = datetime.utcnow()
        # add instance to entity dict if not exists. try custom entities first
        elif type_name in EntityBase._custom_classes:
            try:
                # get custom class as provided in custom classes
                customcls = EntityBase._custom_classes[type_name]
                customcls(entity_name, synccall="internal")
            except:
                pass
                # print(f"ERROR {type_name} not found! please add as custom class derived from EntityBase and import into your main module")
        else:
            try:
                cls = getattr(sys.modules["pyjop.EntityClasses"], type_name)
                # assert inspect.isclass(cls) and  issubclass(cls, EntityBase)
                cls(entity_name, synccall="internal")
            except:
                pass
                # print(f"ERROR {type_name} not found! please add as custom class derived from EntityBase and import into your main module")
        # save type and name of all incoming entities (what about entities without sensors? should send ping and save timestamp)

        if prop_name.startswith("_event"):
            # print(f"received event {nparr.unique_name} {fullname in EntityBase._entity_dict}")
            if (
                fullname in EntityBase._entity_dict
                and nparr.unique_name
                in EntityBase._entity_dict[fullname].event_handlers
            ):
                # print(f"event handler there")
                # put an event in queue
                entity = EntityBase._entity_dict[fullname]
                for listener in entity.event_handlers[nparr.unique_name]:
                    entity._event_queue.put((nparr, listener))
                    # print(f"enqueue event for entity")

        else:
            # replicate value
            EntityBase._in_dict[nparr.unique_name] = nparr

    @staticmethod
    def _clean_entity_dict() -> None:
        items = EntityBase._entity_dict.copy().items()
        EntityBase._entity_dict = {k: v for k, v in items if v.is_valid}

    @classmethod
    def find_all(cls, find_derived=False, suppress_warnings=False) -> list[T]:
        """Get all entities of the current type. If find_derived=True, then all derived classes are found as well.

        Args:
            find_derived (bool, optional): True to find all derived classes as well, False otherwise. Defaults to False.

        Example:
            >>>
            convs = ConveyorBelt.find_all(True) #list of all conveyor belts, large conveyor belts, turnable conveyor belts and railed conveyor belts.
        """
        all_ents = cls._find_all_internal(find_derived)
        if len(all_ents) == 0 and suppress_warnings is False:
            EntityBase._log_debug_static(
                f"Cannot find any entities of type '{cls.__name__}'",
                (1, 1, 0),
            )
        return all_ents

    @classmethod
    def _find_all_internal(cls, find_derived=False):
        items = EntityBase._entity_dict.copy().items()
        EntityBase._log_line_number()
        if find_derived or cls == EntityBase:
            all_ents = [v for k, v in items if isinstance(v, cls) and v.is_valid]
        else:
            all_ents = [v for k, v in items if v.__class__ == cls and v.is_valid]
        all_ents.sort(key=lambda x: x.entity_name)
        return all_ents

    @classmethod
    def find(cls, entity_name: str, suppress_warnings=False) -> T:
        """Find entity of the current type (or its derivatives) by its unique name.

        Example:
            >>>
            #get conveyor belt named _entityConveyorBelt0
            conv = ConveyorBelt.find("_entityConveyorBelt0")
        """
        fullname = cls.__name__ + "." + entity_name
        EntityBase._log_line_number()
        if fullname not in EntityBase._entity_dict and suppress_warnings is False:
            EntityBase._log_debug_static(
                f"Cannot find entity '{entity_name}'",
                (1, 1, 0),
            )
            return None
        v = EntityBase._entity_dict[fullname]
        if isinstance(v, cls) and v.is_valid:
            return v
        if suppress_warnings is False:
            EntityBase._log_debug_static(
                f"Cannot find entity '{entity_name}' of type '{cls.__name__}'",
                (1, 1, 0),
            )
        return None

    @classmethod
    def first(cls, suppress_warnings=False) -> T:
        """Get first entity of the current type (non derived take precedence) if at least one exists.

        Example:
            >>>
            conv = ConveyorBelt.first() #first conveyor belt
            sim = SimEnvManager.first() #first (and only) simenv manager
        """
        all = cls._find_all_internal()
        if len(all) > 0:
            return all[0]
        all = cls._find_all_internal(True)
        if len(all) > 0:
            return all[0]
        if suppress_warnings is False:
            EntityBase._log_debug_static(
                f"Cannot find any entities of type '{cls.__name__}'",
                (1, 1, 0),
            )
        return None

    @classmethod
    def any_random(cls, suppress_warnings=False) -> T:
        """Get any random entity of the current type (non derived take precedence), if at least one exists.

        Example:
            >>>
            conv = ConveyorBelt.first() #first conveyor belt
            sim = SimEnvManager.first() #first (and only) simenv manager
        """
        all = cls._find_all_internal()
        if len(all) > 0:
            return random.choice(all)
        all = cls._find_all_internal(True)
        if len(all) > 0:
            return random.choice(all)
        if suppress_warnings is False:
            EntityBase._log_debug_static(
                f"Cannot find any entities of type '{cls.__name__}'",
                (1, 1, 0),
            )
        return None

    def __init__(self, entity_name: str, **kwargs) -> None:
        if self.__class__ == EntityBase:
            msg = "Abstract class cannot be instantiated"
            raise TypeError(msg)
        self.__entity_name = entity_name
        fullname = self._build_name()
        if fullname in EntityBase._entity_dict:
            msg = f"Please use EntityBase.find('{entity_name}')"
            raise SyntaxError(msg)
        if "synccall" not in kwargs or kwargs["synccall"] != "internal":
            msg = f"entity '{entity_name}' does not exist in the SimEnv"
            raise KeyError(msg)

        self.last_sync_utc = datetime.utcnow()
        EntityBase._entity_dict[fullname] = self
        self.event_handlers: dict[str, list[Callable[[T, float, NPArray], None]]] = {}

    def _post_API_call(self) -> None:
        # stuff to do after each api call
        self._log_line_number()

    def _check_get_rate(self, k: str) -> None:
        t0, c0 = 0, 0
        if k in EntityBase._in_time_dict:
            t0, c0 = EntityBase._in_time_dict[k]
        t1 = time.time_ns()
        if t1 < t0 + 3 * 1e6:  # 3ms
            EntityBase._in_time_dict[k] = (t1, c0 + 1)
            if c0 >= 20:
                EntityBase._log_debug_static(
                    f"Getter rate limit: use sleep() or SimEnv.run_main() to repeatedly get data such as '{k}'",
                    Colors.Yellow,
                )
                _dispatch_events()
                await_receive()
        else:
            EntityBase._in_time_dict[k] = (t1, 0)

    def _build_name(self, prop_name="") -> str:
        # if self.IsValid() == False:
        #    raise KeyError(f"entity '{self.entityName}' was removed from the game. Please use IsValid and Find get updated references.")
        s = self.__class__.__name__ + "." + self.__entity_name
        if prop_name != "":
            s = s + "." + prop_name
        return s

    def _add_event_listener(
        self,
        event_name: str,
        handler: Callable[[T, float, NPArray], None],
        force_singleton=False,
    ) -> None:
        full_eventname = self._build_name(event_name)
        if force_singleton or full_eventname not in self.event_handlers:
            self.event_handlers[full_eventname] = [handler]
        else:
            self.event_handlers[full_eventname].append(handler)

    def _clear_event_handlers(self, event_name: str) -> None:
        full_eventname = self._build_name(event_name)
        self.event_handlers[full_eventname] = []

    def _get_array_raw(
        self,
        prop_name: str,
        shape: list[int] | None = None,
    ) -> np.ndarray:
        if shape is None:
            shape = [0, 0, 0]
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            squeeze_axe = []
            shape = list(shape)
            for i in range(len(shape)):
                if shape[i] == 0:
                    shape[i] = self._in_dict[k].array_data.shape[i]
                if shape[i] == 1:
                    squeeze_axe.append(i)
            return (
                self._in_dict[k]
                .array_data[0 : shape[0], 0 : shape[1], 0 : shape[2]]
                .squeeze(tuple(squeeze_axe))
            )
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return np.zeros(shape, dtype=np.uint8)

    def _get_float(self, prop_name: str) -> float:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return float(self._in_dict[k].array_data[0][0][0])
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return 0.0

    def _get_vector3d(self, prop_name: str) -> Vector3:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return Vector3(self._in_dict[k].array_data.squeeze()[:3])
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return Vector3()

    def _get_rotator3d(self, prop_name: str) -> Rotator3:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return Rotator3(self._in_dict[k].array_data.squeeze()[:3])
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return Rotator3()

    def _get_uint8(self, prop_name: str) -> int:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return int(self._in_dict[k].array_data[0][0][0])
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return 0

    def _get_int(self, prop_name: str) -> int:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return int.from_bytes(
                self._in_dict[k].array_data.squeeze().tobytes(),
                "little",
                signed=True,
            )

        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return 0

    def _get_bool(self, prop_name: str) -> bool:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return int(self._in_dict[k].array_data[0][0][0]) != 0
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return False

    def _get_string(self, prop_name: str) -> str:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return self._in_dict[k].get_string()  # check if ascii
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return ""

    def _get_json(self, prop_name: str, suppress_warn=False) -> dict[str, Any]:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._check_get_rate(k)
            self._post_API_call()
            return self._in_dict[k].get_json_dict()
        if not _is_custom_level_runner() and not suppress_warn:
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return {}

    def _set_void(self, prop_name: str, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([], dtype=np.float32))
        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_float(self, prop_name: str, val: float, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([val], dtype=np.float32))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_vector3d(
        self,
        prop_name: str,
        val: Sequence[float] | Vector3 | Rotator3,
        append: bool = False,
        add_args: Sequence[float] = [],
    ) -> None:
        vec = _parse_vector(val, add_args=add_args)
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([vec[0], vec[1], vec[2]], dtype=np.float32))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_uint8(self, prop_name: str, val: int, append: bool = False) -> None:
        k = self._build_name(prop_name)
        if val < 0:
            val = 0
        if val > 255:
            val = 255
        nparr = NPArray(k, np.asarray([val], dtype=np.uint8))
        # check duplicate here

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_int(self, prop_name: str, val: int, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(
            k,
            np.frombuffer(int.to_bytes(val, 4, "little", signed=True), dtype=np.uint8),
        )
        # check duplicate here

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_bool(self, prop_name: str, val: bool, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([1 if val else 0], dtype=np.uint8))
        # check duplicate here

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_string(self, prop_name: str, val: str, append: bool = False) -> None:
        k = self._build_name(prop_name)
        bytes = str(val).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_bytes(self, prop_name: str, val: bytes, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.frombuffer(val, dtype=np.uint8))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_json(self, prop_name: str, val: dict, append: bool = False) -> None:
        k = self._build_name(prop_name)

        bytes = json.dumps(val, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _get_image(self, prop_name: str, channels=3) -> np.ndarray:
        k = self._build_name(prop_name)
        self._post_API_call()
        if (
            k in self._in_dict
            and len(self._in_dict[k].array_data.shape) == 3
            and self._in_dict[k].array_data.shape[2] >= channels
        ):
            self._check_get_rate(k)
            if channels == 3:
                return self._in_dict[k].array_data[:, :, (2, 1, 0)] + 1 - 1  # but why?
            if channels == 2:
                return self._in_dict[k].array_data[:, :, (0, 1)] + 1 - 1  # but why?
            if channels == 1:
                return self._in_dict[k].array_data[:, :, 0] + 1 - 1  # but why?
        if not _is_custom_level_runner():
            EntityBase._log_debug_static(f"Sensor unavailable: {k}", Colors.Yellow)
        return (
            self._BLANK_IMAGE
            if channels == 3
            else self._BLANK_IMAGE[:, :, 0]
            if channels <= 1
            else self._BLANK_IMAGE[:, :, 0:2]
        )

    # def _is_already_set(self,arr:NPArray)->bool:
    #     return False
    #     if arr.unique_name in EntityBase.inDict and arr.unique_name not in EntityBase.outDict and EntityBase.inDict[arr.unique_name].pack_msg() == arr.pack_msg():
    #         #out msg equal to target (and no out dict set), no need to set it
    #         return True
    #     return False
    #     if arr.unique_name in EntityBase.outDict and EntityBase.outDict[arr.unique_name].pack_msg() == arr.pack_msg():
    #         return True #out dict already set
    #     if arr.unique_name in EntityBase.inDict and arr.unique_name not in EntityBase.outDict and EntityBase.inDict[arr.unique_name].pack_msg() == arr.pack_msg():
    #         #out msg equal to target (and no out dict set), no need to set it
    #         return True
    #     return False

    @property
    def is_valid(self) -> bool:
        """Checks if this entity is still in the SimEnv and valid."""
        return (
            _debugger_is_active()
            or (datetime.utcnow() - self.last_sync_utc).total_seconds() < 3
        )

    @property
    def entity_name(self) -> str:
        """Get the unique name of this entity."""
        return self.__entity_name

    # def Ping(self, color = (255,0,0), duration = 2):
    #     """Pings the current entity in-game and blinks with the specified color for the specified duration (in seconds). good for debugging.
    #     """
    #     k = self.__build_name__("Ping")
    #     nparr = NPArray(k,np.asarray(color + (duration,),dtype=np.uint8))
    #     #check duplicate here
    #     if self.__is_already_set__(nparr):
    #         return
    #     self.__outDict__[k] = nparr
    #     self.__post_API_call__(k,duration)

    def focus(self) -> None:
        """Select and focus on this entity in the SimEnv viewport."""
        self._set_void("Focus")

    def __str__(self) -> str:
        # custom string representation. print type and unique name
        return self.entity_name

    def __repr__(self) -> str:
        # custom string representation. print type and unique name and TODO all sensor values
        return self.entity_name

    def __eq__(self, other: object) -> bool:
        """Two entities are equal if their unique names are equal. Comparison with str is also possible."""
        if isinstance(other, EntityBase):
            return self.entity_name == other.entity_name
        if isinstance(other, str):
            return self.entity_name == other
        return False

    def __hash__(self) -> int:
        """Hash value of entities is based on their unique name str."""
        return hash(self.entity_name)

    @staticmethod
    def _get_line_number() -> int:
        if sys.gettrace():
            return -1
        if threading.current_thread() is not threading.main_thread():
            return -1
        if _is_custom_level_runner():
            return -1
        cf = currentframe()
        if not cf:
            return -1
        m = inspect.getmodule(cf)
        while cf.f_back and m and m.__name__.startswith("pyjop."):
            cf = cf.f_back
        finfo = getframeinfo(cf)
        return finfo.lineno

    @staticmethod
    def _log_line_number() -> None:
        """Send the currently running line number (of the main file) to the game."""
        no = EntityBase._get_line_number()
        if no < 0:
            return
        # builtins.print(no)
        k = "SimEnvManager.Current.LogLineNo"
        nparr = NPArray(k, np.frombuffer(int.to_bytes(no, 4, "little"), dtype=np.uint8))
        EntityBase._set_out_data(k, nparr)

    def log_debug(self, msg: str, col=Colors.White) -> None:
        """Log a debug message into Python and into the SimEnv from this entity."""
        k = self._build_name("LogDebug")
        jsonDict = {"msg": msg, "col": _parse_color(col)}
        bytes = json.dumps(jsonDict, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, True)

        self._post_API_call()

    @staticmethod
    def _log_debug_static(
        msg: str,
        col=Colors.White,
        log_level=VerbosityLevels.Important,
    ) -> None:
        """Log a debug message into Python and into the SimEnv."""
        jsonDict = {"msg": msg, "col": _parse_color(col), "level": int(log_level)}
        k = "SimEnvManager.Current.LogDebug"
        bytes = json.dumps(jsonDict, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))
        EntityBase._set_out_data(k, nparr, True, 30)

        EntityBase._log_line_number()

    @staticmethod
    def _log_img_static(imgArr: np.ndarray) -> None:
        """Display an image in the SimEnv log."""
        k = "SimEnvManager.Current.LogImg"

        if len(imgArr.shape) == 2:
            imgArr = np.expand_dims(imgArr, 2)

        if imgArr.shape[0] != 256 or imgArr.shape[1] != 256:
            imgArr = skimage.transform.resize(
                imgArr,
                (256, 256),
                anti_aliasing=False,
                preserve_range=True,
                order=0,
            )

        # convert to uint8
        if imgArr.dtype != np.uint8:
            imgArr = (imgArr * 255).astype(np.uint8)

        if imgArr.shape[2] == 3:
            imgArr = np.dstack((imgArr, np.ones((256, 256), dtype=np.uint8) * 255))

        nparr = NPArray(k, imgArr)
        EntityBase._set_out_data(k, nparr)
        EntityBase._log_line_number()


class EntityBaseStub(EntityBase[T]):
    pass


def await_send(timeout=6) -> None:
    start = 0.0
    last_send = EntityBase.last_send_at
    while last_send == EntityBase.last_send_at and start < timeout:
        time.sleep(0.002)
        start += 0.002


def await_receive(timeout=6) -> None:
    """Wait for one roundtrip between Python and the SimEnv.

    Args:
        timeout (int, optional): Defaults to 6 seconds.
    """
    start = 0.0
    last_receive = EntityBase.last_receive_at
    while last_receive == EntityBase.last_receive_at and start < timeout:
        time.sleep(0.002)
        start += 0.002


def _find_all_entity_classes(modules: list[ModuleType]) -> list[type[EntityBase]]:
    """Helper function to find and list all classes derived from entity base in the given modules."""
    entity_classes = []
    builtin_classes = dir(sys.modules["pyjop.EntityClasses"])
    for m in modules:
        # get all imported classes in each module derived from entitybase
        all_classes = inspect.getmembers(
            m,
            lambda x: inspect.isclass(x)
            and issubclass(x, EntityBase)
            and x.__name__ not in builtin_classes,
        )
        entity_classes.extend([i[1] for i in all_classes])
    return list(set(entity_classes))


def _find_all_entity_classes_rec(
    module: ModuleType | None = None,
) -> list[type[EntityBase]]:
    """Helper function to find and list all classes derived from entity base currently loaded in __main__."""
    if module is None:
        module = sys.modules["__main__"]
    entity_classes = []
    entity_classes.extend(_find_all_entity_classes([module]))

    inner_modules = inspect.getmembers(module, inspect.ismodule)

    for _name, m in inner_modules:
        if m.__name__.startswith("mypyjop"):
            entity_classes.extend(_find_all_entity_classes_rec(m))
    all_classes = list(set(entity_classes))
    all_names = [a.__name__ for a in all_classes]
    dupes = {x for x in all_names if all_names.count(x) > 1}
    assert len(dupes) == 0, f"duplicate entity classes found: {dupes}"
    return all_classes


def _dispatch_events() -> None:
    try:
        gt = float(
            EntityBase._in_dict["SimEnvManager.Current.SimTime"].array_data[0, 0, 0],
        )
        while True:
            event = EntityBase._event_queue.get_nowait()
            if not event:
                return
            if event[1] is None:
                continue
            nparr = event[0]
            type_name, entity_name, prop_name = nparr.unique_name.split(".")
            fullname = type_name + "." + entity_name
            if fullname not in EntityBase._entity_dict:
                continue

            event[1](EntityBase._entity_dict[fullname], gt, nparr)
    except queue.Empty:
        pass
    except Exception as err:
        EntityBase._log_debug_static("Event error: " + str(err), (1, 0, 0))

    if EntityBase._is_debug_paused and _debugger_is_active():
        from pyjop.Network import SimEnv, SockAPIClient

        SockAPIClient._force_send_manual(
            SimEnv._client_socket,
            NPArray(
                "SimEnvManager.Current.setTimeDilation",
                np.asarray([1], dtype=np.float32),
            ),
        )
        EntityBase._is_debug_paused = False


# beware of the depths below:


def _trace_debug_jop_call(frame: FrameType, event, arg):
    if event == "return":
        return None
    if frame is None:
        return None
    if "currentpyscript.py" not in frame.__repr__():
        return None
    m = inspect.getmodule(frame)

    # if m.__name__.startswith("pyjop."):
    #     while frame.f_back:
    #         frame = frame.f_back
    #     m = inspect.getmodule(frame)

    if m is None or m.__name__ != "__main__":
        return None

    # if _trace_debug_jop_call.main_line==frame.f_lineno:
    #    return
    # builtins.print("--------")

    # while frame:

    finfo = inspect.getframeinfo(frame)

    if finfo.code_context and (
        finfo.code_context[0].endswith("jopmainhidden()\n")
        or finfo.code_context[0].endswith("def jopmainhidden():\n")
    ):
        return _trace_debug_jop_call

    if _trace_debug_jop_call.resume_main and frame.f_code.co_name != "jopmainhidden":
        return _trace_debug_jop_call

    lineno = frame.f_lineno - 2

    do_break = False
    if _trace_debug_jop_call.stepping or lineno in _trace_debug_jop_call.bp:
        do_break = True
    if _trace_debug_jop_call.break_on_error and event == "exception":
        do_break = True
    # else:
    #     for bp in _trace_debug_jop.bp:
    #         if _trace_debug_jop.main_line <= bp and frame.f_lineno >= bp:
    #             do_break = True
    #             break
    # log line number

    k = "SimEnvManager.Current.LogLineNo"
    nparr = NPArray(k, np.frombuffer(int.to_bytes(lineno, 4, "little"), dtype=np.uint8))
    EntityBase._set_out_data(k, nparr)
    simenv = _trace_debug_jop_call.m.first()  # simenv manager
    if simenv:
        old_res = simenv._get_json("DebugCmd", True)  # res and ts (real time)
        if "bp" in old_res:
            _trace_debug_jop_call.bp = old_res["bp"]
    if do_break and simenv:
        allvars = {}
        alltvars_watch = []
        for k, v in frame.f_locals.items():
            if isinstance(v, (ModuleType)):
                continue
            vstr = str(v)
            if (
                type(v) is np.ndarray
                and len(v.shape) >= 2
                and v.shape[0] > 10
                and v.shape[1] > 10
            ):
                pil_img = Image.fromarray(v)
                with BytesIO() as buff:
                    pil_img.save(buff, format="JPEG")
                    vstr = base64.b64encode(buff.getvalue()).decode("ascii")
            allvars[k] = vstr
            d_valstr = vstr if len(vstr) < 41 else vstr[0:40] + "..."
            d_typestr = f"({type(v).__name__!s})"
            if type(v).__module__.startswith("pyjop.EntityClasses"):
                d_typestr = ""
            alltvars_watch.append(f"{k} {d_typestr}: {d_valstr}")

        _trace_debug_jop_call.print(
            "DEBUG:",
            lineno,
            [s.strip() for s in finfo.code_context],
            ", ".join(alltvars_watch),
        )

        simenv._set_json("DebugData", allvars)
        while True:
            time.sleep(0.01)
            res = simenv._get_json("DebugCmd", True)
            if res and res != old_res:
                # cmd = _trace_debug_jop_call.input("c/s/o: ")
                cmd: str = res["res"]

                # set breakpoints if changed
                if "bp" in res:
                    _trace_debug_jop_call.bp = res["bp"]

                # step command
                if cmd == "continue":
                    _trace_debug_jop_call.stepping = False
                    break
                elif cmd == "stepin":
                    _trace_debug_jop_call.stepping = True
                    break
                elif cmd == "stepout":
                    _trace_debug_jop_call.stepping = True
                    _trace_debug_jop_call.resume_main = True
                    simenv.set_time_dilation(1)
                    return None
                elif cmd == "stop":
                    # sys.settrace(None)
                    _trace_debug_jop_call.bp = []
                    _trace_debug_jop_call.stepping = False
                    break

    _trace_debug_jop_call.resume_main = False
    return _trace_debug_jop_call


def debug_mode(
    bp: Sequence[int] = [],
    stepping=False,
    break_error=True,
    enabled=True,
) -> None:
    if not enabled:  ##disable
        sys.settrace(None)
        return
    from pyjop.EntityClasses import SimEnvManager, input, print

    if not sys.gettrace():  # enable
        sys.settrace(_trace_debug_jop_call)
    _trace_debug_jop_call.stepping = stepping
    _trace_debug_jop_call.bp = bp
    _trace_debug_jop_call.resume_main = False
    _trace_debug_jop_call.break_on_error = break_error
    _trace_debug_jop_call.print = print
    _trace_debug_jop_call.input = input
    _trace_debug_jop_call.m = SimEnvManager


def _is_admin_process():
    return "admin_process" in sys.argv


def _debugger_is_active() -> bool:
    """Return if the debugger is currently active."""
    return hasattr(sys, "gettrace") and sys.gettrace() is not None


def _parse_vector(
    arg,
    as_dict=False,
    dict_names: tuple[str, str, str] = ("x", "y", "z"),
    add_args: Sequence[float] = [],
) -> tuple[float, float, float] | dict[str, float] | None:
    if arg is None:
        return None
    if not hasattr(arg, "__len__"):
        vec = (arg, arg, arg)
        if len(add_args) == 2:
            vec = (arg, add_args[0], add_args[1])
    elif type(arg) is dict:
        vec = (arg[dict_names[0]], arg[dict_names[1]], arg[dict_names[2]])
    elif len(arg) == 1:
        vec = (arg[0], arg[0], arg[0])
        if len(add_args) == 2:
            vec = (arg, add_args[0], add_args[1])
    elif len(arg) == 2:
        vec = (arg[0], arg[1], 0)
    else:
        vec = (arg[0], arg[1], arg[2])
    vec = (float(vec[0]), float(vec[1]), float(vec[2]))
    if as_dict:
        return {dict_names[0]: vec[0], dict_names[1]: vec[1], dict_names[2]: vec[2]}
    else:
        return vec


def _hex_to_rgb(hex_string: str):
    hex_string = hex_string.lstrip("#").upper()  # Remove '#' and convert to uppercase
    red = int(hex_string[0:2], 16) / 255.0
    green = int(hex_string[2:4], 16) / 255.0
    blue = int(hex_string[4:6], 16) / 255.0
    return red, green, blue


def _parse_color(
    color_arg,
    as_dict=False,
) -> tuple[float, float, float] | dict[str, float]:
    if color_arg is None or (type(color_arg) is str and color_arg == ""):
        return (
            {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0} if as_dict else (1.0, 1.0, 1.0)
        )  # default color white
    if type(color_arg) is str and color_arg in Colors:
        color_arg = Colors[color_arg]
    if type(color_arg) is Colors:
        color_arg = color_arg.value
    if type(color_arg) is str and len(color_arg) == 7 and color_arg[0] == "#":
        color_arg = _hex_to_rgb(color_arg)
    if type(color_arg) is dict:
        color_arg = [color_arg["r"], color_arg["g"], color_arg["b"]]
    if not hasattr(color_arg, "__len__"):
        color_arg = (color_arg, color_arg, color_arg)
    if len(color_arg) > 3:
        color_arg = color_arg[:3]
    if (
        max(color_arg) > 1
        and type(color_arg[0]) is int
        and type(color_arg[1]) is int
        and type(color_arg[2]) is int
    ):
        color_arg = [c / 255.0 for c in color_arg]

    if as_dict:
        return {"r": color_arg[0], "g": color_arg[1], "b": color_arg[2], "a": 1.0}
    else:
        return color_arg


# def singleton(cls):
#     instances = {}
#     def get_instance(*args, **kwargs):
#         if cls not in instances:
#             instances[cls] = cls(*args, **kwargs)
#         return instances[cls]


#     return get_instance
class DataModelBase(SimpleNamespace):
    def __init__(self) -> None:
        super().__init__()

    def reset(self) -> None:
        """Reset the data model to its initial state."""
        self.__init__()

    def __repr__(self) -> str:
        return ", ".join([f"{k}={v!s}" for k, v in self.__dict__.items()])

    def __str__(self) -> str:
        return self.__repr__()
