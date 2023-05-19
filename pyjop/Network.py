from typing import Any, Dict, List, Tuple, Type, Union
import time
import numpy as np
import threading
import socket
import errno
import sys
#import os, psutil
from psutil import Process
from os import getpid
from gc import collect
from datetime import datetime
from pyjop.EntityBase import EntityBase, NPArray, _find_all_entity_classes_rec, _is_custom_level_runner
import copy
import inspect
import random
import math

class SockAPIClient:

    BUF_SIZE = 2 ** 16

    TIMEOUT = 5
    lock = threading.Lock()

    

    @staticmethod
    def threaded_receive(connection:socket.socket):
        # connection.send(str.encode('Welcome to the Servern'))
        time.sleep(0.20095217)
        datall = bytearray()
        lendatall = 0
        while True:
            # connection.sendall(str.encode("hellö",'utf-8'))
            SockAPIClient.lock.acquire()
            try:
                while True:
                    datall += connection.recv(SockAPIClient.BUF_SIZE)
                    if len(datall) == lendatall:
                        break
                    lendatall = len(datall)
            except socket.error as e:
                if not (e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK):
                    #_logjop.error("unkown error receiving: %s", e)
                    SockAPIClient.lock.release()
                    break
            SockAPIClient.lock.release()
            if len(datall) > 0:
                
                #print("receive: " + str(datall))
                # unpack all
                all_frames = datall.split(NPArray._MAGIC_BYTES)
                all_arrs = [
                    NPArray.from_msg(m2)
                    for m2 in all_frames
                    if len(m2) >= NPArray._HEADER_SIZE + 1
                    and int.from_bytes(m2[:4], "little")
                    == len(m2[NPArray._HEADER_SIZE:])
                ]
                #missing frames / incomplete?
                if len(all_arrs) > 0:
                    #received valid data
                    for nparr in all_arrs:
                        EntityBase._sync_incoming_data(nparr)
                    EntityBase.last_receive_at = datetime.utcnow()

                if len(all_arrs) != len(all_frames):
                    datall = bytearray() + all_frames[-1] #keep leftovers
                else:
                    datall = bytearray()

            if (datetime.utcnow() - EntityBase.last_receive_at).total_seconds() > SockAPIClient.TIMEOUT:
                #_logjop.warn("receive has timeout")
                break
            time.sleep(0.005)
            #log.info("receive")
        #_logjop.warn("receive has closed")
        connection.close()

    @staticmethod
    def threaded_send(connection:socket.socket):
        time.sleep(0.2112456)
        # connection.send(str.encode('Welcome to the Servern'))
        data = b""
        while True:
            # log mem usage
            if _is_custom_level_runner()==False and random.random() < 0.01:
                k = "SimEnvManager.Current.MemUsg"
                nparr = NPArray(k,np.asarray([get_memory_usage()],dtype=np.float32))
                EntityBase._set_out_data(k,nparr)
            did_send = False
            if len(EntityBase._out_dict)>0:
                EntityBase.sendlock.acquire()
                out_dict = copy.deepcopy(EntityBase._out_dict)
                EntityBase._out_dict = dict() #clear
                EntityBase.sendlock.release()
                #out_items = out_dict.items()
                
                #pack data
                l = [v for k,v in out_dict.items()]
                flat_list = [num.pack_msg() for sublist in l for num in sublist]
                data = b"".join(flat_list)
                
                SockAPIClient.lock.acquire()
                try:
                    # while sent
                    while len(data) > 0:
                        len_sent = connection.send(data)
                        did_send = True
                        #print("sent " + str(len_sent))
                        data = data[len_sent:]
                except socket.error as e:
                    if not (e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK):
                        SockAPIClient.lock.release()
                        #_logjop.error("unkown error sending: %s", e)
                        break
                SockAPIClient.lock.release()
                if did_send:
                    EntityBase.last_send_at = datetime.utcnow()
            if (datetime.utcnow() - EntityBase.last_receive_at).total_seconds() > SockAPIClient.TIMEOUT:
                #_logjop.warn("send has timeout")
                break
            time.sleep(0.005)
            #log.info("sent")
        #_logjop.warn("sending closed")
        connection.close()


class SimEnv:
    """Python class for communicating with the current Simulation Environment. Use the SimEnvManager class once you are connected.
    """    
    _is_connected = False
    _client_socket = socket.socket()

    @staticmethod
    def connect(host="127.0.0.1", port=18189) -> bool:
        """connect to the SimEnv instance. returns true on sucess.

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
        if len(custom_classes) > 0: #convert to dict
            EntityBase._custom_classes = {c.__name__: c for c in custom_classes if inspect.isclass(c) and issubclass(c,EntityBase)}

       
        client_socket = socket.socket()
        client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, SockAPIClient.BUF_SIZE
        )
        client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, SockAPIClient.BUF_SIZE
        )

        #_logjop.info("Waiting for remote host %s:%i",host,port)
        try:
            client_socket.connect((host, port))
        except socket.error as e:
            #_logjop.error("connection error: %s",e)
            return False

        client_socket.setblocking(False)


        # start sender / recv threads
        t1 = threading.Thread(
            target=SockAPIClient.threaded_receive, args=(client_socket,)
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
        nparr = NPArray(k,np.asarray([get_memory_usage()],dtype=np.float32))
        EntityBase._set_out_data(k,nparr)
        SimEnv.run_main()
        time.sleep(0.4)

        #send source code statistics
        
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
        #_logjop.info("connection closed")

    @staticmethod
    def _handle_event_queue():
        while SimEnv._is_connected and EntityBase._event_q_handlers:
            try:
                eventDat = EntityBase._event_q_raw.get_nowait()
            except:
                break
            old_handlers = set()
            for h in EntityBase._event_q_handlers:
                if h.accepts(eventDat):
                    if h.is_oneshot:
                        old_handlers.add(h)
                    h.handler_code(eventDat)
                    h.accepted_at = datetime.utcnow()
            
        #clear old handlers
        EntityBase._event_q_handlers = [h for h in EntityBase._event_q_handlers if h not in old_handlers]
                        

    @staticmethod
    def run_main()->bool:
        """run the main loop and exchange data with the SimEnv inside the loop while the connection is active. waits for one tick.
        """
 
        #SimEnv.await_tick()
        
        last_update = EntityBase.last_receive_at
        #wait for update
        start = 0.0
        while last_update == EntityBase.last_receive_at and start<3 and SimEnv._is_connected:
            time.sleep(0.002)
            start += 0.002
        SimEnv._handle_event_queue()

        return SimEnv._is_connected
    
    @staticmethod
    def disconnect():
        """disconnect from the SimEnv.
        """
        time.sleep(0.6)
        EntityBase._log_debug_static("pyjop closed connection")
        time.sleep(0.6)
        SimEnv._is_connected = False
        SimEnv._client_socket.close()
        
#_logjop.info("SimEnv ready")

_overhead_mem_bytes = 0

def get_memory_usage(subtract_overhead=True) -> float:
    """get the currently used memory of your program in megabytes.
    """
    collect()
    process = Process(getpid())
    mb = process.memory_info().rss / (1e6)
    if subtract_overhead:
        mb -= _overhead_mem_bytes
    if mb < 1:
        mb = 1
    return mb
        

_overhead_mem_bytes = math.ceil(get_memory_usage(False))
