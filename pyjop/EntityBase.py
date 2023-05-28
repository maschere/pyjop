# pip wheel . --no-deps
from abc import ABC, abstractmethod
import builtins
from collections import deque
import copy
import json
import random
import threading
from types import FrameType, ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)
import numpy as np
import sys
import time
import skimage.transform
import skimage.util
from datetime import datetime
import inspect
from queue import Queue
from inspect import currentframe, getframeinfo

from pyjop.Enums import Colors, _parse_color

# _logjop = logging.getLogger("JOP_GAME")


class NPArray:
    """numpy array for transfer over tcp socket"""

    _MAGIC_BYTES: Final = b"Ihg\x1c"
    _NAME_LEN: Final = 128
    _PRE_HEADER: Final = 17
    _HEADER_SIZE: Final = _NAME_LEN + _PRE_HEADER

    def __init__(self, name: str, arr: np.ndarray) -> None:
        self.unique_name = name
        self.array_data: np.ndarray = arr

    @classmethod
    def from_msg(cls, msg_b):
        # skip 4 bytes if magic bytes still there
        if msg_b[:4] == NPArray._MAGIC_BYTES:
            msg_b = msg_b[4:]
        msg_len = int.from_bytes(msg_b[:4], "little")
        w = int.from_bytes(msg_b[4:8], "little")
        h = int.from_bytes(msg_b[8:12], "little")
        c = int.from_bytes(msg_b[12:16], "little")
        if msg_b[16] == 0:
            dt = np.uint8
        else:
            dt = np.float32
        name = str.strip(
            msg_b[NPArray._PRE_HEADER : NPArray._HEADER_SIZE].decode("ascii")
        )
        msg_b = msg_b[NPArray._HEADER_SIZE : NPArray._HEADER_SIZE + msg_len]
        arr = np.ndarray(shape=(w, h, c), dtype=dt, buffer=msg_b)
        nparr = NPArray(name, arr)
        return nparr

    def pack_msg(self) -> bytearray:
        out = bytearray()
        if self.array_data.dtype != np.uint8 and self.array_data.dtype != np.float32:
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


def _is_custom_level_runner() -> bool:
    import sys

    if len(sys.argv) > 1:
        return "custom_level_running" in sys.argv
    return False


class EventData:
    """unused at the moment"""

    def __init__(
        self, event_name: str, sender_uniquename: str, timestamp: float, data: Any
    ) -> None:
        self.event_name = event_name
        self.sender_uniquename = sender_uniquename
        self.timestamp = timestamp
        self.data = data


class EventListener:
    def __init__(
        self,
        for_event: str,
        from_sender: str,
        is_oneshot=False,
        test_accept: Optional[Callable[[EventData], bool]] = None,
    ) -> None:
        self.for_event = for_event
        self.from_sender = from_sender
        self.test_accept = test_accept
        self.is_oneshot = is_oneshot
        self.accepted_at = 0

    def accepts(self, event_data: EventData) -> bool:
        accepts = True
        if self.for_event and self.for_event != event_data.event_name:
            accepts = False
        elif self.from_sender and self.from_sender != event_data.sender_uniquename:
            accepts = False
        elif self.test_accept is not None and self.test_accept(event_data) == False:
            accepts = False
        return accepts


class EventHandler(EventListener):
    def __init__(
        self,
        handler_code: Callable[[EventData], None],
        for_event: str,
        from_sender: str,
        test_accept: Optional[Callable[[EventData], bool]] = None,
    ) -> None:
        super().__init__(for_event, from_sender, test_accept)
        self.handler_code = handler_code

    def clear(self):
        EntityBase._event_q_handlers = [
            h for h in EntityBase._event_q_handlers if h != self
        ]

    def is_completed(self):
        time.sleep(0.002)


T = TypeVar("T")


class EntityBase(Generic[T]):
    """Base class for all entities in the SimEnv. Use Find or FindAll to get the entities you want to control and program them."""

    _out_dict: Dict[str, List[NPArray]] = dict()
    _in_dict: Dict[str, NPArray] = dict()
    _entity_dict: Dict[str, "EntityBase"] = dict()
    _event_q_raw: Queue[
        EventData
    ] = Queue()  # event name, sender unqiue name, timestamp, payload
    _event_q_handlers: List[EventHandler] = []
    _custom_classes: Dict[str, Type["EntityBase"]] = dict()
    _BLANK_IMAGE: Final = np.zeros((64, 64, 3), dtype=np.uint8)
    _TIMEOUT: Final = 5
    last_receive_at = datetime.utcnow()

    last_send_at = datetime.utcnow()

    sendlock = threading.Lock()

    @staticmethod
    def _set_out_data(k, arr, append=False):
        EntityBase.sendlock.acquire()
        if append:
            if k not in EntityBase._out_dict:
                EntityBase._out_dict[k] = [arr]
            else:
                EntityBase._out_dict[k].append(arr)
        else:
            EntityBase._out_dict[k] = [arr]
        EntityBase.sendlock.release()

    @staticmethod
    def _sync_incoming_data(nparr: NPArray):
        if nparr.unique_name.startswith("EventQ."):
            event_name = nparr.unique_name.replace("EventQ.", "")
            raw = nparr.array_data.squeeze().tobytes().decode("utf-8")
            try:
                raw_payload = json.loads(raw)
                ts = raw_payload["ts"]
                sender_name = raw_payload["sender"] if "sender" in raw_payload else ""
            except:
                return
            EntityBase._event_q_raw.put_nowait(
                EventData(event_name, sender_name, ts, raw_payload)
            )
        if nparr.unique_name.count(".") != 2:
            return
        EntityBase._in_dict[nparr.unique_name] = nparr
        # get identifiers
        type_name, entity_name, prop_name = nparr.unique_name.split(".")
        fullname = type_name + "." + entity_name
        if fullname in EntityBase._entity_dict:
            # update sync timestamp
            EntityBase._entity_dict[fullname].last_sync_utc = datetime.utcnow()
            return
        # add instance to entity dict if not exists. try custom entities first
        if type_name in EntityBase._custom_classes:
            try:
                # get custom class as provied in custom classes
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

    @classmethod
    def find_all(cls, find_derived=False) -> List[T]:
        """Get all entities of the current type. If find_derived=True, then all dervied classes are found as well

        Args:
            find_derived (bool, optional): True to find all dervied classes as well, False otherwise. Defaults to False.

        Example:
            >>>
            convs = ConveyorBelt.find_all(True) #list of all conveyor belts, large conveyor belts, turnable conveyor belts and railed conveyor belts.
        """
        all_ents = cls._find_all_internal(find_derived)
        if len(all_ents) == 0:
            EntityBase._log_debug_static(
                f"Cannot find any entities of type '{cls.__name__}'", (1, 0, 0)
            )
        return all_ents

    @classmethod
    def _find_all_internal(cls, find_derived=False):
        items = EntityBase._entity_dict.copy().items()
        EntityBase._log_line_number()
        if find_derived or cls == EntityBase:
            all_ents = [v for k, v in items if isinstance(v, cls)]
        else:
            all_ents = [v for k, v in items if v.__class__ == cls]
        all_ents.sort(key=lambda x: x.get_entity_name())
        return all_ents

    @classmethod
    def find(cls, entity_name: str) -> T:
        """Find entity of the current type (or its derivatives) by its unique name. Entity names always start with "_entity" by default.

        Example:
            >>>
            #get conveyor belt named _entityConveyorBelt0
            conv = ConveyorBelt.find("_entityConveyorBelt0")
        """
        fullname = cls.__name__ + "." + entity_name
        EntityBase._log_line_number()
        if fullname not in EntityBase._entity_dict:
            EntityBase._log_debug_static(
                f"Cannot find entity '{entity_name}'", (1, 1, 0)
            )
            return None
        v = EntityBase._entity_dict[fullname]
        if isinstance(v, cls):
            return v
        EntityBase._log_debug_static(
            f"Cannot find entity '{entity_name}' of type '{cls.__name__}'", (1, 1, 0)
        )
        return None

    @classmethod
    def first(cls) -> T:
        """Get first entity of the current type (non derived take precedence)

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
        EntityBase._log_debug_static(
            f"Cannot find any entities of type '{cls.__name__}'", (1, 1, 0)
        )
        return None

    def __init__(self, entity_name: str, **kwargs) -> None:
        if self.__class__ == EntityBase:
            raise TypeError("Abstract class cannot be instantiated")
        self.__entity_name = entity_name
        fullname = self._build_name()
        if fullname in EntityBase._entity_dict:
            raise SyntaxError(f"Please use EntityBase.find('{entity_name}')")
        if "synccall" not in kwargs or "internal" != kwargs["synccall"]:
            raise KeyError(f"entity '{entity_name}' does not exist in the SimEnv")

        self.last_sync_utc = datetime.utcnow()
        EntityBase._entity_dict[fullname] = self

    def _post_API_call(self):
        # stuff to do after each api call
        self._log_line_number()

    def _build_name(self, prop_name="") -> str:
        # if self.IsValid() == False:
        #    raise KeyError(f"entity '{self.entityName}' was removed from the game. Please use IsValid and Find get updated references.")
        s = self.__class__.__name__ + "." + self.__entity_name
        if prop_name != "":
            s = s + "." + prop_name
        return s

    def _get_float(self, prop_name: str) -> float:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return float(self._in_dict[k].array_data[0][0][0])
        return 0.0

    def _get_vector(self, prop_name: str) -> np.ndarray:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return self._in_dict[k].array_data[:3, 0, 0]
        return np.asarray([0, 0, 0], dtype=np.float32)

    def _get_uint8(self, prop_name: str) -> int:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return int(self._in_dict[k].array_data[0][0][0])
        return 0

    def _get_int(self, prop_name: str) -> int:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return int.from_bytes(
                self._in_dict[k].array_data.squeeze().tobytes(), "little"
            )
        return 0

    def _get_bool(self, prop_name: str) -> bool:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return int(self._in_dict[k].array_data[0][0][0]) != 0
        return False

    def _get_string(self, prop_name: str) -> str:
        k = self._build_name(prop_name)
        if k in self._in_dict:
            self._post_API_call()
            return (
                self._in_dict[k].array_data.squeeze().tobytes().decode("ascii").strip()
            )  # check if ascii
        return ""

    def _get_json(self, prop_name: str) -> dict:
        k = self._build_name(prop_name)
        js = {}
        if k in self._in_dict:
            self._post_API_call()
            raw = self._in_dict[k].array_data.squeeze().tobytes().decode("utf-8")
            try:
                js = json.loads(raw)
            except:
                pass
        return js

    def _set_void(self, prop_name: str, append: bool = False):
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([], dtype=np.float32))
        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_float(self, prop_name: str, val: float, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([val], dtype=np.float32))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_vector(self, prop_name: str, val, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([val[0], val[1], val[2]], dtype=np.float32))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_uint8(self, prop_name: str, val: int, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(k, np.asarray([val], dtype=np.uint8))
        # check duplicate here

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_int(self, prop_name: str, val: int, append: bool = False) -> None:
        k = self._build_name(prop_name)
        nparr = NPArray(
            k, np.frombuffer(int.to_bytes(val, 4, "little"), dtype=np.uint8)
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
        bytes = val.encode("ascii")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _set_json(self, prop_name: str, val: Dict, append: bool = False) -> None:
        k = self._build_name(prop_name)
        bytes = json.dumps(val, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, append)
        self._post_API_call()

    def _get_image(self, prop_name: str, channels=3) -> np.ndarray:
        k = self._build_name(prop_name)
        if (
            k in self._in_dict
            and len(self._in_dict[k].array_data.shape) == 3
            and self._in_dict[k].array_data.shape[2] >= channels
        ):
            if channels == 3:
                return self._in_dict[k].array_data[:, :, (2, 1, 0)] + 1 - 1  # but why?
            if channels == 1:
                return self._in_dict[k].array_data[:, :, 0] + 1 - 1  # but why?
        return self._BLANK_IMAGE if channels == 3 else self._BLANK_IMAGE[:, :, 0]

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
        """checks if this entity is still in the SimEnv and valid"""
        return (datetime.utcnow() - self.last_sync_utc).total_seconds() < 5

    def get_entity_name(self) -> str:
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

    def focus(self):
        """select and focus on this entity in the SimEnv viewport"""
        self._set_void("Focus")

    def resend_data(self):
        """to save bandwith, several entities send static data only once. calling this causes a resend of all data of this entity."""
        self._set_void(
            "*ResendData"
        )  # wildcard command for all components in this entity
        await_tick()

    def __str__(self):
        # custom string representation. print type and unique name
        return self._build_name()

    def __repr__(self):
        # custom string representation. print type and unique name and TODO all sensor values
        return self._build_name()

    @staticmethod
    def _log_line_number():
        """send the currently running line number (of the main file) to the game"""
        if sys.gettrace():
            return
        if threading.current_thread() is not threading.main_thread():
            return
        if _is_custom_level_runner():
            return
        cf = currentframe()
        m = inspect.getmodule(cf)
        while cf.f_back and m and m.__name__.startswith("pyjop."):
            cf = cf.f_back
        finfo = getframeinfo(cf)
        no = finfo.lineno
        # builtins.print(no)
        k = "SimEnvManager.Current.LogLineNo"
        nparr = NPArray(k, np.frombuffer(int.to_bytes(no, 4, "little"), dtype=np.uint8))
        EntityBase._set_out_data(k, nparr)

    def log_debug(self, msg: str, col=Colors.White):
        """log a debug message into Python and into the SimEnv from this entity"""
        k = self._build_name("LogDebug")
        jsonDict = {"msg": msg, "col": _parse_color(col)}
        bytes = json.dumps(jsonDict, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))

        self._set_out_data(k, nparr, True)

        # _logjop.info(self.__class__.__name__ + "." + self.__entity_name + ": " + msg)
        self._post_API_call()

    @staticmethod
    def _log_debug_static(msg: str, col=Colors.White):
        """log a debug message into Python and into the SimEnv"""
        jsonDict = {"msg": msg, "col": _parse_color(col)}
        k = "SimEnvManager.Current.LogDebug"
        bytes = json.dumps(jsonDict, ensure_ascii=False).encode("utf-8")
        nparr = NPArray(k, np.frombuffer(bytes, dtype=np.uint8))
        EntityBase._set_out_data(k, nparr, True)
        # _logjop.info(msg)
        # check for multi print
        # EntityBase.sendlock.acquire()
        # if k in EntityBase._out_dict:
        #     oldBytes = EntityBase._out_dict[k].array_data.tobytes()
        #     if oldBytes != bytes:
        #         oldjsonDict = json.loads(EntityBase._out_dict[k].array_data.tobytes().decode("utf-8"))
        #         if oldjsonDict["col"] == list(col):
        #             oldjsonDict["msg"] += "\n" + msg
        #             bytes = json.dumps(oldjsonDict,ensure_ascii=False).encode("utf-8")
        #             nparr = NPArray(k,np.frombuffer(bytes, dtype=np.uint8))

        # EntityBase._out_dict[k]=nparr
        # EntityBase.sendlock.release()
        EntityBase._log_line_number()

    @staticmethod
    def _log_img_static(imgArr: np.ndarray):
        """display an image in the SimEnv log"""

        k = "SimEnvManager.Current.LogImg"

        if len(imgArr.shape) == 2:
            imgArr = np.expand_dims(imgArr, 2)

        if imgArr.shape[0] != 256 or imgArr.shape[1] != 256:
            imgArr = skimage.transform.resize(imgArr, (256, 256)) * 255

        # convert to uint8
        if imgArr.dtype != np.uint8:
            imgArr = (imgArr * 255).astype(np.uint8)

        if imgArr.shape[2] == 3:
            imgArr = np.dstack((imgArr, np.ones((256, 256), dtype=np.uint8) * 255))

        nparr = NPArray(k, imgArr)
        EntityBase._set_out_data(k, nparr)
        EntityBase._log_line_number()


def await_tick(timeout=6):
    """Wait for one roundtrip between Python and the SimEnv

    Args:
        timeout (int, optional): Defaults to 6 seconds.
    """
    start = 0.0
    last_send = EntityBase.last_send_at
    while last_send == EntityBase.last_send_at and start < timeout:
        time.sleep(0.002)
        start += 0.002

    start = 0.0
    last_receive = EntityBase.last_receive_at
    while last_receive == EntityBase.last_receive_at and start < timeout:
        time.sleep(0.002)
        start += 0.002


def _find_all_entity_classes(modules: List[ModuleType]) -> List[Type[EntityBase]]:
    """helper function to find and list all classes derived from entity base in the given modules"""
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
    module: Optional[ModuleType] = None,
) -> List[Type[EntityBase]]:
    """helper function to find and list all classes derived from entity base currently loaded in __main__"""
    if module is None:
        module = sys.modules["__main__"]
    entity_classes = []
    entity_classes.extend(_find_all_entity_classes([module]))

    inner_modules = inspect.getmembers(module, inspect.ismodule)

    for name, m in inner_modules:
        if m.__name__.startswith("mypyjop"):
            entity_classes.extend(_find_all_entity_classes_rec(m))
    all_classes = list(set(entity_classes))
    all_names = [a.__name__ for a in all_classes]
    dupes = set([x for x in all_names if all_names.count(x) > 1])
    assert len(dupes) == 0, f"duplicate entity classes found: {dupes}"
    return all_classes


# beware of the depths below:


def _trace_debug_jop_call(frame: FrameType, event, arg):
    if event == "return":
        return
    if frame is None:
        return
    if "currentpyscript.py" not in frame.__repr__():
        return
    m = inspect.getmodule(frame)

    # if m.__name__.startswith("pyjop."):
    #     while frame.f_back:
    #         frame = frame.f_back
    #     m = inspect.getmodule(frame)

    if m is None or m.__name__ != "__main__":
        return

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
        old_res = simenv._get_json("DebugCmd")  # res and ts (real time)
        if "bp" in old_res:
            _trace_debug_jop_call.bp = old_res["bp"]
    if do_break and simenv:
        allvars = {
            k: str(v)
            for (k, v) in frame.f_locals.items()
            if not isinstance(v, (ModuleType))
        }
        _trace_debug_jop_call.print(
            "DEBUG:", lineno, [s.strip() for s in finfo.code_context], allvars
        )

        simenv._set_json("DebugData", allvars)
        while True:
            time.sleep(0.01)
            res = simenv._get_json("DebugCmd")
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
                    return
                elif cmd == "stop":
                    # sys.settrace(None)
                    _trace_debug_jop_call.bp = []
                    _trace_debug_jop_call.stepping = False
                    break

    _trace_debug_jop_call.resume_main = False
    return _trace_debug_jop_call


def debug_mode(bp: Sequence[int] = [], stepping=False, break_error=True, enabled=True):
    if not enabled:  ##disable
        sys.settrace(None)
        return
    from pyjop.EntityClasses import print, input, SimEnvManager

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


# def exec_python_script(path:str,m_name="CurrentPyScript"):
#     from pathlib import Path
#     # import ctypes.wintypes
#     # CSIDL_PERSONAL = 5       # My Documents
#     # SHGFP_TYPE_CURRENT = 0   # Get current, not default value
#     # buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
#     # ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

#     p = Path(path)
#     #p = Path.joinpath(doc_path, "JoyOfProgramming/CurrentCustomLevel.py")
#     if p.absolute().is_file():

#         import importlib.util
#         spec = importlib.util.spec_from_file_location(m_name, str(p.absolute()))
#         foo = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(foo)
