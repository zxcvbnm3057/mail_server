from socket import *
from myThreadPool import BoundedThreadPoolExecutor
#import re

def Login_server(connection_limit, process_limit, waiting_limit):
    HOST = '0.0.0.0'
    PORT = 25
    ADDR = (HOST, PORT)
    tcpSerSock = socket(AF_INET, SOCK_STREAM)   #创建套接字
    tcpSerSock.bind(ADDR)   #绑定IP和端口
    tcpSerSock.listen(connection_limit)    #监听端口，最多20人排队
    executor = BoundedThreadPoolExecutor(max_workers=process_limit, max_waiting_jobs=waiting_limit )
    while True:
        print('waiting for connection...')
        tcpCliSock, addr = tcpSerSock.accept()    #建立连接
        print('...connected from:', addr)
        while True:
            executor.submit(Connect_client, (tcpCliSock))
            tcpCliSock, addr = tcpSerSock.accept() 
            print('...connected from:', addr)
    tcpSerSock.close()

def Connect_client(tcpCliSock):
    BUFSIZ = 1024
    command=''
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
        if command.upper()[0:4]==('HELO' or 'EHLO'):
            tcpCliSock.send(('250 Hello '+command[5:]+'\r\n').encode("ascii"))
        elif command.upper()[0:11]=='MAIL FROM: ':
            letter={'mail_from':'','rcpt_to': '', 'text': '' }
            letter['mail_from']=command[11:]
            tcpCliSock.send(('250 OK\r\n').encode("ascii"))
        elif command.upper()[0:9]=='RCPT TO: ':
            letter['rcpt_to']=letter['rcpt_to']+command[9:]
            tcpCliSock.send(('250 OK\r\n').encode("ascii"))
        elif command.upper()=='DATA':
            tcpCliSock.send(('354 Start mail input; end with <CRLF>.<CRLF>\r\n').encode("ascii"))
            while True:
                data = tcpCliSock.recv(BUFSIZ)
                letter['text']=letter['text']+data.decode("utf-8")
                if letter['text'][-5:]=='\r\n.\r\n':
                    tcpCliSock.send(('250 Ok: queued\r\n').encode("ascii"))
                    letter['text']=letter['text'][:-5]
                    break
        elif command.upper()=='QUIT':
            tcpCliSock.send(('221 Bye\r\n').encode("ascii"))
            #调用发送邮件
            break
        elif command.upper()=='NOOP':
            tcpCliSock.send(('250 Ok\r\n').encode("ascii"))
        elif command.upper()=='RSET':
            tcpCliSock.send(('250 Ok\r\n').encode("ascii"))
            letter={'mail_from':'','rcpt_to': '', 'text': '' }
        else:
            tcpCliSock.send(('502 Error: command not implemented\r\n').encode("ascii"))
        command=''
    tcpCliSock.close()
