# -*- coding: utf-8 -*-

from socket import *
from myThreadPool import BoundedThreadPoolExecutor
from Public_Class import*
import send_email
import base64
import auth
#import re

def Login_server(connection_limit, process_limit, waiting_limit):
    HOST = '0.0.0.0'
    PORT = 25
    ADDR = (HOST, PORT)
    tcpSerSock = socket(AF_INET, SOCK_STREAM) #创建套接字
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpSerSock.bind(ADDR)   #绑定IP和端口
    tcpSerSock.listen(connection_limit)    #监听端口，最多20人排队
    client_listener = BoundedThreadPoolExecutor(max_workers=process_limit, max_waiting_jobs=waiting_limit )
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
    letter={'mail_from':'','rcpt_to': '', 'text': '' }
    username=''
    passwd=''
    command=''
    login =False
    ehlo=False
    tcpCliSock.send(('220 Mail Server\r\n').encode("ascii"))
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
        '''
            Respond to the commands
        '''
        if command.upper()[0:4]==('HELO'):
            ehlo=True
            tcpCliSock.send(('250 Hello '+command[5:]+'\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()[0:4]==('EHLO'):
            ehlo=True
            tcpCliSock.send(('''250-Welcome to smtp.{domainname} server\r\n250-AUTH LOGIN PLAIN\r\n250-AUTH=LOGIN PLAIN\r\n250-PIPELINING\r\n250-SIZE 10485760\r\n250 8BITMIME'''.format(domainname=public.domainname)+'\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()==('AUTH LOGIN'):
            if not ehlo:
                tcpCliSock.send(('503 Error: send HELO/EHLO first\r\n').encode("ascii"))
                continue
            tcpCliSock.send(('334 VXNlcm5hbWU6\r\n').encode("ascii"))
            while True:
                data = tcpCliSock.recv(BUFSIZ)
                for char in data:
                    if (char>=32 and char<=126) or char==10 or char==13:
                        username=username+chr(char)
                if not username[-2:]=='\r\n':
                    continue
                else:
                    username=username[:-2]
                    break
            username=base64.b64decode(username).decode() #用户名
            tcpCliSock.send(('334 UGFzc3dvcmQ6\r\n').encode("ascii"))
            while True:
                data = tcpCliSock.recv(BUFSIZ)
                for char in data:
                    if (char>=32 and char<=126) or char==10 or char==13:
                        passwd=passwd+chr(char)
                if not passwd[-2:]=='\r\n':
                    continue
                else:
                    passwd=passwd[:-2]
                    break
            passwd=base64.b64decode(passwd).decode() #密码
            if auth.auth(username,passwd):
                tcpCliSock.send(('235 auth successfully\r\n').encode("ascii"))
                login=True
            else:
                tcpCliSock.send(('530 Access denied\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()==('AUTH PLAIN'):
            if not ehlo:
                tcpCliSock.send(('503 Error: send HELO/EHLO first\r\n').encode("ascii"))
                continue
            tcpCliSock.send(('334').encode("ascii"))
            while True:
                data = tcpCliSock.recv(BUFSIZ)
                for char in data:
                    if char>=32 and char<=126 or char==0:
                        mess=mess+chr(char)
                if not mess[-2:]=='\r\n':
                    continue
                else:
                    mess=mess[:-2]
                    break
            username=mess.split('\x00')[1]
            passwd=mess.split('\x00')[2]
            if auth.auth(username,passwd):
                tcpCliSock.send(('235 auth successfully\r\n').encode("ascii"))
                login=True
            else:
                tcpCliSock.send(('530 Access denied\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()[0:11]=='MAIL FROM: ':
            if not (login and ehlo):
                tcpCliSock.send(('503 Error: need EHLO and AUTH first !\r\n').encode("ascii"))
                command=''
                continue
            letter['mail_from']=''
            letter['mail_from']=command[11:]
            tcpCliSock.send(('250 OK\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()[0:9]=='RCPT TO: ':
            if not (login and ehlo):
                tcpCliSock.send(('503 Error: need EHLO and AUTH first !\r\n').encode("ascii"))
                command=''
                continue
            letter['rcpt_to']=letter['rcpt_to']+command[9:]
            tcpCliSock.send(('250 OK\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()=='DATA':
            if not (login and ehlo):
                tcpCliSock.send(('503 Error: need EHLO and AUTH first !\r\n').encode("ascii"))
                command=''
                continue
            tcpCliSock.send(('354 Start mail input; end with <CRLF>.<CRLF>\r\n').encode("ascii"))
            while True:
                data = tcpCliSock.recv(BUFSIZ)
                letter['text']=letter['text']+data.decode("utf-8")
                if letter['text'][-5:]=='\r\n.\r\n':
                    tcpCliSock.send(('250 Ok: queued\r\n').encode("ascii"))
                    letter['text']=letter['text'][:-5]
                    break
            send_email.send_email(letter)
            command=''
            continue
        elif command.upper()=='QUIT':
            tcpCliSock.send(('221 Bye\r\n').encode("ascii"))
            command=''
            break
        elif command.upper()=='NOOP':
            tcpCliSock.send(('250 Ok\r\n').encode("ascii"))
            command=''
            continue
        elif command.upper()=='RSET':
            tcpCliSock.send(('250 Ok\r\n').encode("ascii"))
            letter={}
            command=''
            continue
        else:
            tcpCliSock.send(('502 Error: command not implemented\r\n').encode("ascii"))
            command=''
            continue
    tcpCliSock.close()
