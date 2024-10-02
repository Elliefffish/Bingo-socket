import zmq
from colorama import init, Fore, Back, Style
import os
import time
from random import choice, shuffle
import argparse, socket
import json

BUFSIZE = 65535
tmp_port = 9989
Send_num_time = 10
Wait_time = 60

def rand_info():
    num = [str(i) for i in range(1,26)]
    shuffle(num)
    return num

def init_screen():
    global Player
    init(autoreset=True)
    os.system('clear')
    print('Welcome to '+Fore.RED+'Bingo Game!')
    print('Please input ', end='')
    print(Back.MAGENTA+Fore.BLACK+'name,your number', end='')
    print(' to join this game')
    print('Your input = ', end='')
    text = input()
    name = text.split(',')[0]
    i = 1
    if(name == ''):
        name = 'User'
    num = list(set(text.split(',')[1:]))
    if(len(num) != 25):
        print('\nYou do not provide enough numbers, we random the numbers for you.')
        num = rand_info()
#    print(Player)
#    print(name)
#    print(num)
#    print(text)
#    text = input()
#    name = text.split(';')[0]
#    num = text.split(';')[1].split(',')
    os.system("clear")
    print('Welcome '+Fore.YELLOW+name, end='')
    print(" ! Let's wait for the game start!")
    print("This is your bingo card")
    for i in range(0, len(num)):
        if (i+1)%5!=0:
            print('{:>4}'.format(num[i]), end='')
        else:
            print('{:>4}'.format(num[i]))
    return name, num

def check_bingo(bingo_card):
    board = [[0 for j in range(5)] for i in range(5)]
    for i in range(5):
        for j in range(5):
            board[i][j] = bingo_card[i*5+j]

    for row in board:
        if all(cell == 'X' for cell in row):
            return True

    for col in range(5):
        if all(board[row][col] == 'X' for row in range(5)):
            return True

    if all(board[i][i] == 'X' for i in range(5)) or all(board[i][4-i] == 'X' for i in range(5)):
        return True

    return False

def server(socket, b_socket):
    Player = {}
    num = [i for i in range(1, 26)]
    while (len(Player) < 2):
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        limit_time = int(time.time()) + Wait_time
        while(poller.poll(Wait_time*1000)):
            #b_socket.send_string("Connected to server.")
            data = socket.recv_string().split(',')
            if len(data) == 2:
                if data[0]=='Quit':
                    del Player[data[1]]
                continue
            who = data[0]
            number = data[1:]
            if who in Player:
               continue 
            Player[who] = number
            delay = limit_time - int(time.time())
            msg = f'{who} are Player {len(Player)}, Welcome! The game is expected to start in {delay} seconds'
            b_socket.send_string(msg)
            print(f'Player \033[33m{who}\033[0m join this game.')
        if len(Player) < 1:
            print('Nobody join this game')
        elif len(Player) == 1:
            b_socket.send_string(f'Only you in this game, please wait {Wait_time} seconds more.')
    print('\033[92mGame Start!\033[0m')
    b_socket.send_string('start')
    nobody_win = 1
    while len(Player) >= 1 and nobody_win:
        n = choice(num)
        if n=='X':
            continue
        print(f'Number : \033[36m{n}\033[0m') #flag
        num[num.index(n)] = 'X' # == ? #flag
        b_socket.send_string(str(n))

        for x in Player:
           Player[x][Player[x].index(str(n))] = 'X'
        poller.register(socket, zmq.POLLIN)
        limit_time = int(time.time()) + 10
        try:
            #print('\033[90mReceving ...\033[0m')
            while poller.poll(Send_num_time*1000):
                print('\033[90mReceving ...\033[0m')
                data = socket.recv_string()
                #if(data[:4] == 'Quit'):
                #    del Player[data.split(',')[1]]
                #    if(len(Player) == 0):
                #        return
                #che = 0
                if(data[:5] == 'Bingo'):
                    winner = data.split(',')[1]
                    che = check_bingo(Player[winner])
                    if che :
                        nobody_win = 0;
                        b_socket.send_string(f'Winner is {winner}')
                        break;
                    #else:
                        #text = 'You don\'t win!:('
                        #sock.sendto(text.decode(),address)
        except:
            if nobody_win:
                print('\033[90mNobody bingo\033[0m')
                b_socket.send_string('Nobody bingo.')
            #break
        #if nobody_win == 0:
        #    sock.sendto(text.encode('ascii'), (network, port))
    print('\033[92mGame End!\033[0m')
    #indata, addr = sock.recvfrom(BUFSIZE)
    #print('recvfrom client({}):{} '.format(addr, indata.decode()))

def client(socket, b_socket):
    name, nums = init_screen()
    flag = False
    player_num = 0
    socket.send_string(name + ',' + ','.join(nums))
    try:
        while True:
            indata = b_socket.recv_string()
            if(indata.split()[0] == name and indata.split()[2]=='Player'):
                player_num = int(indata.split()[3][:-1])
            if(indata[:4] == 'Quit'):
                print('The server is closed.')
                quit()
            if indata=='start':
                if player_num == 0:
                    print('Your name is used, please join this game again with oter name.')
                    quit()
                break
            if player_num == 0:
                print('Your name is used, please join this game again with oter name.')
                quit()
            print(indata)
        os.system('clear')
        print("Let's start the game!")
        while 1:
            indata = b_socket.recv_string()
            if indata[:6] == 'Winner':
                if indata.split()[2] == name:
                   print(Fore.YELLOW +'You Win!')
                else:
                    indata = indata + '.'
                    print(Fore.YELLOW+indata)
                break
            if(indata[:4] == 'Quit'):
                quit()
            if nums[nums.index(indata)] == 'X' or indata == 'start':
                continue;
            else:
                nums[nums.index(indata)]='X'
                for i in range(0, len(nums)):
                    print_red = ''
                    print_end = ''
                    if nums[i] == 'X':
                        print_red = '\033[31m'
                        print_end = '\033[0m'
                    if (i+1)%5!=0:
                        print('{}{:>4}{}'.format(print_red,nums[i],print_end), end='')
                    else:
                        print('{}{:>4}{}'.format(print_red,nums[i],print_end))
                print()
                print("=========================================")
                print()
                if check_bingo(nums) == 1:
                    print(Fore.YELLOW+"Bingo!")
                    socket.send_string('Bingo,'+name)
    except:
        socket.send_string('Quit,'+name)
