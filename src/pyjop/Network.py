import copy
import errno
import inspect
import math
import socket
import sys
import threading
import time
from datetime import datetime
from gc import collect
from os import getpid

import numpy as np
from psutil import Process

from pyjop.EntityBase import (
    EntityBase,
    NPArray,
    _debugger_is_active,
    _dispatch_events,
    _find_all_entity_classes_rec,
    _is_custom_level_runner,
)


class SockAPIClient:
    BUF_SIZE = 2**16

    TIMEOUT = 5
    lock = threading.Lock()

    @staticmethod
    def threaded_receive(connection: socket.socket):
        # connection.send(str.encode('Welcome to the Servern'))
        # time.sleep(0.20095217)
        datall = bytearray()
        lendatall = 0
        last_sim_time = -10.0
        while True:
            update_receive = False
            SockAPIClient.lock.acquire()
            try:
                while True:
                    datall += connection.recv(SockAPIClient.BUF_SIZE)
                    if len(datall) == lendatall:
                        break
                    lendatall = len(datall)
            except OSError as e:
                if not (e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK):
                    SockAPIClient.lock.release()
                    break
            SockAPIClient.lock.release()
            if len(datall) > 0:
                # print("receive: " + str(datall))
                # unpack all
                all_frames = datall.split(NPArray._MAGIC_BYTES)
                all_arrs = [
                    NPArray.from_msg(m2)
                    for m2 in all_frames
                    if len(m2) >= NPArray._HEADER_SIZE + 1
                    and int.from_bytes(m2[:4], "little")
                    == len(m2[NPArray._HEADER_SIZE :])
                ]
                # missing frames / incomplete?
                if len(all_arrs) > 0:
                    # received valid data
                    for nparr in all_arrs:
                        EntityBase._sync_incoming_data(nparr)
                        if nparr.unique_name == "SimEnvManager.Current.SimTime":
                            if last_sim_time != nparr.get_float():
                                update_receive = True
                            last_sim_time = nparr.get_float()

                if len(all_arrs) != len(all_frames):
                    datall = bytearray() + all_frames[-1]  # keep leftovers
                else:
                    datall = bytearray()

            if (
                _debugger_is_active() == False
                and (datetime.utcnow() - EntityBase.last_receive_at).total_seconds()
                > SockAPIClient.TIMEOUT
            ):
                break
            time.sleep(0.005)
            EntityBase._clean_entity_dict()
            if update_receive:
                EntityBase.last_receive_at = datetime.utcnow()
            # log.info("receive")

        connection.close()

    @staticmethod
    def threaded_send(connection: socket.socket):
        # time.sleep(0.2112456)
        # connection.send(str.encode('Welcome to the Servern'))
        data = b""
        iloop = 5
        while True:
            did_send = False
            if len(EntityBase._out_dict) > 0:
                EntityBase.sendlock.acquire()
                out_dict = copy.deepcopy(EntityBase._out_dict)
                EntityBase._out_dict = dict()  # clear
                EntityBase.sendlock.release()
                # out_items = out_dict.items()

                # pack data sequentially
                l = [
                    num
                    for sublist in [v for k, v in out_dict.items() if len(v) > 0]
                    for num in sublist
                ]
                l.sort(key=lambda v: v.time_id)
                flat_list = [num.pack_msg() for num in l]
                if _is_custom_level_runner() == False and iloop % 10 == 0:
                    k = "SimEnvManager.Current.MemUsg"
                    nparr = NPArray(
                        k,
                        np.asarray([get_memory_usage()], dtype=np.float32),
                    )
                    flat_list.append(nparr.pack_msg())

                data = b"".join(flat_list)

                SockAPIClient.lock.acquire()
                try:
                    # while sent
                    while len(data) > 0:
                        len_sent = connection.send(data)
                        did_send = True
                        # print("sent " + str(len_sent))
                        data = data[len_sent:]
                except OSError as e:
                    if not (e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK):
                        SockAPIClient.lock.release()
                        break
                SockAPIClient.lock.release()
                if did_send:
                    EntityBase.last_send_at = datetime.utcnow()
                    iloop += 1
            if (
                _debugger_is_active() == False
                and (datetime.utcnow() - EntityBase.last_receive_at).total_seconds()
                > SockAPIClient.TIMEOUT
            ):
                break
            time.sleep(0.005)
            # log.info("sent")

        connection.close()

    @staticmethod
    def _force_send_manual(connection: socket.socket, *args: NPArray):
        flat_list = [num.pack_msg() for num in args]
        data = b"".join(flat_list)

        try:
            # while sent
            while len(data) > 0:
                len_sent = connection.send(data)
                data = data[len_sent:]
        except OSError as e:
            if not (e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK):
                return

    @staticmethod
    def _debug_pause():
        SockAPIClient._force_send_manual(
            SimEnv._client_socket,
            NPArray(
                "SimEnvManager.Current.setTimeDilation",
                np.asarray([0], dtype=np.float32),
            ),
        )

        out_dict = copy.deepcopy(EntityBase._out_dict)
        EntityBase._out_dict = dict()
        l = [
            num
            for sublist in [v for k, v in out_dict.items() if len(v) > 0]
            for num in sublist
        ]
        l.sort(key=lambda v: v.time_id)
        SockAPIClient._force_send_manual(SimEnv._client_socket, *l)
        EntityBase._is_debug_paused = True


class SimEnv:
    """Python class for communicating with the current Simulation Environment. Use the SimEnvManager class once you are connected."""

    _is_connected = False
    _client_socket = socket.socket()

    @staticmethod
    def connect(host="127.0.0.1", port=18189) -> bool:
        """Connect to the SimEnv instance. returns true on success.

        Args:
            host (str, optional): Host pc running the SimEnv. Defaults to localhost at "127.0.0.1".
            port (int, optional): Port on which the SimEnv is being hosted. Defaults to 18189.

        Returns:
            bool: true on successful connection.
        """
        if SimEnv._is_connected:
            return True
        EntityBase._out_dict = dict()
        EntityBase._in_dict = dict()
        EntityBase._entity_dict = dict()
        custom_classes = _find_all_entity_classes_rec()
        if len(custom_classes) > 0:  # convert to dict
            EntityBase._custom_classes = {
                c.__name__: c
                for c in custom_classes
                if inspect.isclass(c) and issubclass(c, EntityBase)
            }

        client_socket = socket.socket()
        client_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_SNDBUF,
            SockAPIClient.BUF_SIZE,
        )
        client_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_RCVBUF,
            SockAPIClient.BUF_SIZE,
        )

        try:
            client_socket.connect((host, port))
        except OSError:
            return False

        client_socket.setblocking(False)

        # start sender / recv threads
        t1 = threading.Thread(
            target=SockAPIClient.threaded_receive,
            args=(client_socket,),
        )
        t2 = threading.Thread(target=SockAPIClient.threaded_send, args=(client_socket,))

        SimEnv._is_connected = True
        t1.start()
        t2.start()

        t3 = threading.Thread(
            target=SimEnv.__observe_threads__,
            args=(
                client_socket,
                t1,
                t2,
            ),
        )
        t3.start()
        time.sleep(0.7)
        while True:
            print(".", end="")
            time.sleep(0.25)
            if len(EntityBase._entity_dict.copy().keys()) > 0:
                time.sleep(0.25)
                break
        EntityBase._log_debug_static("pyjop connection established")
        SimEnv._client_socket = client_socket
        k = "SimEnvManager.Current.MemUsg"
        nparr = NPArray(k, np.asarray([get_memory_usage()], dtype=np.float32))
        EntityBase._set_out_data(k, nparr)
        SimEnv.run_main()
        time.sleep(0.4)

        # send source code statistics

        return True

    @staticmethod
    def __observe_threads__(cSock, t1, t2):
        t1.join()
        t2.join()
        # done

        cSock.close()
        if SockAPIClient.lock.locked():
            SockAPIClient.lock.release()
        SimEnv._is_connected = False

    main_counter = 0

    @staticmethod
    def run_main() -> bool:
        """Run the main loop and exchange data with the SimEnv inside the loop while the connection is active. waits for one tick."""
        # SimEnv.await_tick()

        last_update = EntityBase.last_receive_at
        time.sleep(0.01)
        # sim_update = float(EntityBase._in_dict["SimEnvManager.Current.SimTime"].array_data[0][0][0])
        # wait for update
        start = 0.0
        while (
            SimEnv.main_counter > 0
            and last_update == EntityBase.last_receive_at
            and start < 3
            and SimEnv._is_connected
        ):
            time.sleep(0.002)
            start += 0.002

        SimEnv.main_counter += 1

        _dispatch_events()

        return SimEnv._is_connected

    @staticmethod
    def disconnect():
        """Disconnect from the SimEnv."""
        time.sleep(0.6)
        EntityBase._log_debug_static("pyjop closed connection")
        time.sleep(0.6)
        SimEnv._is_connected = False
        SimEnv._client_socket.close()
        time.sleep(0.1)
        sys.exit()


_overhead_mem_bytes = 0


def get_memory_usage(subtract_overhead=True) -> float:
    """Get the currently used memory of your program in megabytes."""
    collect()
    process = Process(getpid())
    mb = process.memory_info().rss / (1e6)
    if subtract_overhead:
        mb -= _overhead_mem_bytes
    if mb < 1:
        mb = 1
    return mb


_overhead_mem_bytes = math.ceil(get_memory_usage(False))
