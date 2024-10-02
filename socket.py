
#!/usr/bin/env python3
# Broadcast to all subscribers.  The publisher does not buffer the message.

import argparse, zmq, time, random
import bingo

def server(host = '127.0.0.1', port = 1060):
    if host =='': host = '*'
    url = "tcp://{}:{}".format(host, port)
    pub_url = "tcp://{}:{}".format(host, port+1)
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    pub_socket = context.socket(zmq.PUB)
    socket.bind(url)
    pub_socket.bind(pub_url)
    try:
        while True:
            bingo.server(socket, pub_socket)
    except: #KeyboardInterrupt:
        pub_socket.send_string("Quit")
        time.sleep(1)

def client(host, port):
    if host =='': host = '*'
    url = "tcp://{}:{}".format(host, port)
    sub_url = "tcp://{}:{}".format(host, port+1)
    try:
        context = zmq.Context()
        sub_socket = context.socket(zmq.SUB)
        socket = context.socket(zmq.PUSH)
        socket.connect(url)
        sub_socket.connect(sub_url)
        sub_socket.setsockopt_string(zmq.SUBSCRIBE,'')
        bingo.client(socket, sub_socket)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='ZeroMQ Pub/Sub')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='hostname of the server')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)
