#!/usr/bin/env python3

import lldb
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import threading
from typing import List


class Shim:
    def __init__(self, debugger_id: int):
        self.debugger_id = debugger_id

    def get_debugger(self) -> lldb.SBDebugger:
        return lldb.SBDebugger_FindDebuggerWithID(self.debugger_id)

    def get_breakpoints(self) -> List[str]:
        d = self.get_debugger()
        assert isinstance(d, lldb.SBDebugger)
        t: lldb.SBTarget = d.GetSelectedTarget()
        bps = []
        for i in range(0, t.GetNumBreakpoints()):
            bp: lldb.SBBreakpoint = t.GetBreakpointAtIndex(i)
            bps.append(str(bp))
        print(bps)
        return bps


def serve(debugger_id: int):
    server = SimpleXMLRPCServer(("localhost", 8089))
    server.register_instance(Shim(debugger_id))
    server.serve_forever()


def init_serverside(debugger: lldb.SBDebugger):
    debugger_id = debugger.GetID()
    python_thread = threading.Thread(target=serve, args=(debugger_id,))
    python_thread.start()


class Client:
    def __init__(self, server_address: str):
        self.proxy = xmlrpc.client.ServerProxy(server_address)

    def get_breakpoints(self) -> List[str]:
        return self.proxy.get_breakpoints()
