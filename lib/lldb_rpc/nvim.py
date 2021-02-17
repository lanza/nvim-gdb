#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

class LLDBListener:
    def did_stop(self, file: str, line: int) -> bool:
        self # void cast
        print(f"{file}:{line}")
        return True


if __name__ == '__main__':
    server = SimpleXMLRPCServer(('localhost', 8098))
    server.register_instance(LLDBListener())
    server.serve_forever()

    proxy = xmlrpc.client.ServerProxy('http://localhost:10045')
    i = proxy.handle_command("reg read")
    print(i)
