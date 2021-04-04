# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 13:45:39 2021

@author: josh
"""
import threading
import sys
import socket

import Q
import file_io
import file_grabber


def send(main, client, content):
    client.sendall(content.encode())


def rc_file_rq(main, q, client):
    try:
        if q.peak() in main.meta_data:
            path = main.meta_data[q.pop()][0]
            data = file_io.read_bytes(path)
            if data is not None:
                client.sendall(data)
            else:
                client.sendall("fail".encode())
    except:
        client.sendall("fail".encode())


def rc_server_list(main, q):
    while q.peak() != 'msgend':
        server = q.pop()
        if server not in main.server_list:
            main.server_list.append(server)
        file_io.write_data(server_list, ''.join(server_list)

#todo
def send_server_list(main):
    s = socket.socket()
    fails = []
    for server in main.server_list:
        try:
            s.connect((server, main.port))
            if "accepted" in s.recv(1024).decode():
                s.sendall(("rc_server_list," + ''.join(main.server_list) + ",msgend").encode())
        except:
            fails.append(server)
        s.close()

    # try one more time
    for server in fails:
        try:
            s.connect((server, main.port))
            if "accepted" in s.recv(1024).decode():
                s.sendall(("rc_server_list," + ''.join(main.server_list) + ",msgend").encode())
        except:
            print("server", server, "offline")
        s.close()


# todo
def rc_meta_data(main, q):
    new_meta_data = {}

    while q.peak() != "msgend":
        command = q.pop()
        if command == "data_start":
            md5 = q.pop()
            new_meta_data[md5] = []
            while q.peak() != "data_end":
                new_meta_data[md5].append(q.pop())

    if new_meta_data != main.meta_data:
        # deal with deletions
        for item in main.metaDelete(new_meta_data):
            file_io.remove_file(main.meta_data[item])

        # make the update
        main.meta_data = new_meta_data

        # start a new file grabber
        fg = threading.Thread(target=file_grabber.start(), args=(main,), daemon=True)
        fg.start()


def rc_meta_data_rq(main, q, client):
    datastr = "rc_meta_data,"
    try:
        for item in main.meta_data:
            datastr += "data_start," + item + ","
            for path in item:
                datastr += path + ","
            datastr += "data_end,"
        datastr += "msgend"
        send(main, client, datastr)
    except:
        send(main, client, "failed")


def threaded_client(main, client, address):
    print("connected to ",address)
    send(main, client, "accepted")
    buffer = ""
    while "msgend" not in buffer:
        buffer += client.recv(1024).decode()

    q = Q.MsgQueue()
    q.push(buffer.split(','))

    while q.has_items():
        command = q.pop()
        print(command)
        if address in main.server_list:
            # commands available to known addresses

            # return a file's actual data
            if "rc_file_rq" in command:
                rc_file_rq(main, q, client)

            # process new server_list
            elif "rc_server_list" in command:
                rc_server_list(main, q)

            # process new hash table
            elif "rc_meta_data" in command:
                rc_meta_data(main, q)

            # return the hash table
            elif "rc_meta_data_rq" in command:
                rc_meta_data_rq(main, client, q)

            # kill
            elif "msgend" in command:
                client.close()

            # delete an item from the server_list
            # TODO
            #elif "rc_server_del" in command:
                #rc_server_del()

        # accessible by all
        # server joining a network gets their address stored and the server_list gets sent to all
        if main.password in command:
            if q.pop() == "msgend":  # remove msg end of join request
                q.push(address)
                q.push("msgend")
                rc_server_list(main, q)  # update local server list
                rc_meta_data_rq(main, client, q)  # send hash table
                send_server_list(main.server_list)  # update all server lists
            else:
                client.close()
                break


def start(main):
    print("boop")
    host = 'localhost'  # 0.0.0.0
    port = main.port

    # join network
    if main.server_list != []:
        for server in main.server_list:
            try:
                print(main.server_list)
                main.s.connect((server, port))
                # successful connection
                if 'accepted' in main.s.recv(1024).decode():
                    # join a network
                    main.s.sendall(main.password.encode() + ",msgend".encode())

                    # receive hash table data
                    buffer = ""
                    while "msgend" not in buffer:
                        buffer += main.s.recv(1024).decode()

                    # push it onto a queue
                    q = Q.MsgQueue()
                    q.push(buffer.split(','))
                    if q.peak() == 'rc_meta_data':
                        q.pop()

                        # process the updated hash table
                        rc_meta_data(main, q)
            except:
                sys.exit("all your servers are offline, or you are offline")


    # use main socket for listening
    main.s.bind((host, port))
    print('Waiting for a Connection..')
    main.s.listen()

    while True:
        client, address = main.s.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        c = threading.Thread(target=threaded_client, args=(main, client, address[0]))
        c.start()
