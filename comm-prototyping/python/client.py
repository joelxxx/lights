# -*- coding: utf-8 -*-
import socket
import os

print("Connecting...")
if os.path.exists("/tmp/python_unix_sockets_example"):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
#    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/tmp/python_unix_sockets_example")
    print("Ready.")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
        try:
            x = raw_input("> ")
            if "" != x:
                print("SEND:", x)
                client.send(x.encode('utf-8'))
                if "DONE" == x:
                    print("Shutting down.")
                    break
        except KeyboardInterrupt as k:
            print("Shutting down.")
            client.close()
            break
else:
    print("Couldn't Connect!")
    print("Done")
