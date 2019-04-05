# -*- coding: utf-8 -*-

import os
from socket import *
from myThreadPool import BoundedThreadPoolExecutor
from Public_Class import*
import auth
from hashlib import md5
#import re

def Login_server(connection_limit, process_limit, waiting_limit):
    HOST = '0.0.0.0'
    PORT = 110
    ADDR = (HOST, PORT)
    tcpSerSock = socket(AF_INET, SOCK_STREAM) #创建套接字
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpSerSock.bind(ADDR)   #绑定IP和端口
    tcpSerSock.listen(connection_limit)    #监听端口，最多20人排队
    client_listener = BoundedThreadPoolExecutor(max_workers=process_limit, max_waiting_jobs=waiting_limit )
    global method
    method=['CAPA','TOP','UIDL','USER','STAT','LIST','DELE','NOOP','REST','RETR']
    while True:
        print('waiting for connection...')
        tcpCliSock, addr = tcpSerSock.accept()    #建立连接
        print('...connected from:', addr)
        while True:
            client_listener.submit(Connect_client, (tcpCliSock))
            tcpCliSock, addr = tcpSerSock.accept() 
            print('...connected from:', addr)
    tcpSerSock.close()

def Connect_client(tcpCliSock):
    BUFSIZ = 1024
    command=''
    login =False
    tcpCliSock.send(('+OK Mail Server\r\n').encode("ascii"))
    while True:
        '''
            Combine bytes into commands
        '''
        data = tcpCliSock.recv(BUFSIZ)
        if data==b'':
            break

        for char in data:
            if (char>=32 and char<=126) or char==10 or char==13:
                command=command+chr(char)
        if not command[-2:]=='\r\n':
            continue
        else:
            command=command[:-2]
        command=command.strip().split(' ')
        '''
            Respond to the commands
        '''
        if len(command)==3:
            if command[0].upper()=='TOP':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                try:
                    letter_id=int(command[1]-1)
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    command=''
                    continue
                except IndexError:
                    tcpCliSock.send(('-Err Index Error\r\n').encode("ascii"))
                with open(letter[letter_id],'r') as f:
                    letter_text=f.read
                tcpCliSock.send('+OK\r\n'.encode("ascii"))
                tcpCliSock.send((letter_text.split('\r\n\r\n')[0]+'\r\n\r\n'+'\r\n'.join(letter_text.split('\r\n\r\n')[1].split('\r\n')[:int(command[2])])+'\r\n\r\n\r\n.\r\n').encode("ascii"))
                command=''
                continue
            else:
                tcpCliSock.send(('-ERR Unknown command\r\n').encode("ascii"))
                command=''
                continue
        elif len(command)==2:
            if command[0].upper()==('USER'):
                user=True
                tcpCliSock.send('+OK welcome to mail.{}\r\n'.format(public.domainname).encode("ascii"))
                username=command[1]
                command=''
                continue
            elif command[0].upper()==('PASS'):
                if not user:
                    tcpCliSock.send(('-ERR USER first\r\n').encode("ascii"))
                    command=''
                    continue
                passwd=command[1]
                if auth.auth(username,passwd):
                    login=True
                    user_dir=os.path.join(public.mailbox_path,username)
                    emails=os.listdir(user_dir)
                    for i in range(len(emails)):
                        emails[i]=os.path.join(user_dir,emails[i])
                    emails.sort(key=lambda x: os.path.getctime(x),reverse = True)
                    for i in range(len(emails)):
                        email_size=os.path.getsize(emails[i])
                        emails[i]=(emails[i],email_size)
                        emails_size+=email_size
                    emails_original=emails
                    emails_delete=[]
                    tcpCliSock.send('+OK Welcome\r\n'.encode("ascii"))
                else:
                    tcpCliSock.send(('-ERR invalid username or password\r\n').encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='RETR':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                try:
                    letter_id=int(command[1]-1)
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    command=''
                    continue
                with open(letter[letter_id],'r') as f:
                    letter_text=f.read
                tcpCliSock.send(letter_text.encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='LIST':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                try:
                    if int(command[1])>len(emails):
                        tcpCliSock.send(('-Err Index Error\r\n').encode("ascii"))
                    command=''
                    continue
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    command=''
                    continue
                tcpCliSock.send('+OK {} messages ({} octets)\r\n'.format(len(emails),emails_size).encode("ascii"))
                tcpCliSock.send('{} {}\r\n.\r\n'.format(int(command[1]),emails[int(command[1]-1)][1]).encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='UIDL':
                try:
                    with open(emails[int(command[1]-1)][0], 'rb') as f:
                        tcpCliSock.send('+OK {} {}\r\n'.format(int(command[1]),md5(f.read()).hexdigest()).encode("ascii"))
                        command=''
                        continue
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    command=''
                    continue
                except IndexError:
                    tcpCliSock.send(('-Err Index Error\r\n').encode("ascii"))
                    command=''
                    continue
            elif command[0].upper()=='TOP':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                try:
                    letter_id=int(command[1]-1)
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    command=''
                    continue
                except IndexError:
                    tcpCliSock.send(('-Err Index Error\r\n').encode("ascii"))
                    command=''
                    continue
                with open(letter[letter_id],'r') as f:
                    letter_text=f.read
                tcpCliSock.send('+OK\r\n'.encode("ascii"))
                tcpCliSock.send((letter_text.split('\r\n\r\n')[0]+'\r\n\r\n\r\n.\r\n').encode("ascii"))
                command=''
                continue
            else:
                tcpCliSock.send(('-ERR Unknown command\r\n').encode("ascii"))
                command=''
                continue
            
        elif len(command)==1:
            if command[0].upper()=='CAPA':
                tcpCliSock.send('+OK capability\r\n'+'\r\n'.join(method)+'\r\n.\r\n'.encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='STAT':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                tcpCliSock.send('+OK {} {}\r\n'.format(len(emails),emails_size).encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='UIDL':
                tcpCliSock.send('+OK {} messages ({} octets)\r\n'.format(len(emails),emails_size).encode("ascii"))
                for i in range(len(emails)):
                    with open(emails[i][0], 'rb') as f:
                        tcpCliSock.send('{} {}\r\n'.format(i,md5(f.read()).hexdigest()).encode("ascii"))
                tcpCliSock.send('.\r\n'.format(len(emails),emails_size).encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='LIST':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                tcpCliSock.send('+OK {} messages ({} octets)\r\n'.format(len(emails),emails_size).encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='DELE':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                try:
                    email_delete=emails.pop(int(command[1])-1)
                    emails_delete.appened(email_delete)
                    emails_size-=email_delete[1]
                except ValueError:
                    tcpCliSock.send(('-Err Syntax Error\r\n').encode("ascii"))
                    continue
                except IndexError:
                    tcpCliSock.send(('-Err Index Error\r\n').encode("ascii"))
                    continue
                tcpCliSock.send(('+OK 1 Deleted\r\n').encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='QUIT':
                tcpCliSock.send(('+OK Bye\r\n').encode("ascii"))
                for email in emails_delete:
                    os.remove(email[0])
                command=''
                break
            elif command[0].upper()=='NOOP':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                tcpCliSock.send('+OK {} messages ({} octets)\r\n'.format(len(emails),emails_size).encode("ascii"))
                command=''
                continue
            elif command[0].upper()=='REST':
                if not login:
                    tcpCliSock.send(('-Err Auth first\r\n').encode("ascii"))
                    command=''
                    continue
                emails=emails_original
                emails_delete=[]
                tcpCliSock.send(('250 Ok\r\n').encode("ascii"))
                command=''
                continue
            else:
                tcpCliSock.send(('-ERR Unknown command\r\n').encode("ascii"))
                command=''
                continue
    tcpCliSock.close()
