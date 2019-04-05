import dns.resolver
from socket import *
from myThreadPool import BoundedThreadPoolExecutor
from Public_Class import*
import auth
import time

def send_email(email):
    rcpt_addr=email['rcpt_to'].strip('<>').split('@')[1]
    if rcpt_addr==public.domainname:
        email_poster.submit(send_email_local,(email))
    else:
        email_poster.submit(send_email_remote,*(email, rcpt_addr))
        
def init(connection_limit, process_limit, waiting_limit):
    global email_poster,tcpCliSocks
    tcpCliSocks=[object]*process_limit
    HOST = '0.0.0.0'
    PORT = 25
    ADDR = (HOST, PORT)
    for i in range(process_limit):
        tcpCliSocks[i] = socket(AF_INET, SOCK_STREAM)
        tcpCliSocks[i].setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        tcpCliSocks[i].bind(ADDR)   #绑定IP和端口
    email_poster=BoundedThreadPoolExecutor(max_workers=process_limit, max_waiting_jobs=waiting_limit )
    
def send_email_local(email):
    rcpt_addr=email['rcpt_to'].strip('<>').split('@')[0]
    if auth.get_username(rcpt_addr):
        with open(os.path.join(public.mailbox_path,rcpt_addr,str(int(time.time()))),'w') as f:
            f.write(email['text'])
    else:
        pass#退信

def send_email_remote(email,rcpt_addr):
    print('begin')
    BUFSIZ = 1024
    MX = dns.resolver.query(rcpt_addr, 'MX')
    rcpt_ip=gethostbyname(str(MX[0].exchange))
    tcpCliSock=tcpCliSocks.pop()
    tcpCliSock.connect((rcpt_ip,25))
    rec_data=tcpCliSock.recv(BUFSIZ)
    post_data='EHLO '+public.domainname+'\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    if not rec_data[:3]=='250':
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not rec_data[:3]=='250':
            return
    print('helo')
    post_data='MAIL FROM: '+email['mail_from']+'\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    if not rec_data[:3]=='250':
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not rec_data[:3]=='250':
            return
    print('mail')
    post_data='RCPT TO: '+email['rcpt_to']+'\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    if not rec_data[:3]=='250':
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not rec_data[:3]=='250':
            return
    print('rept')
    post_data='DATA\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    if not rec_data[:3]=='354':
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not rec_data[:3]=='354':
            return
    print('data')
    post_data=email['text']+'\r\n.\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    print(rec_data)
    if not (rec_data[:3]=='354' or rec_data[:3]=='250'):
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not (rec_data[:3]=='354' or rec_data[:3]=='250'):
            return
    print('send')
    post_data='QUIT\r\n'
    tcpCliSock.send(post_data.encode("utf-8"))
    rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
    if not rec_data[:3]=='221':
        tcpCliSock.send(post_data.encode("utf-8"))
        rec_data=tcpCliSock.recv(BUFSIZ).decode("utf-8")
        if not rec_data[:3]=='221':
            return
    print('quit')
    tcpCliSocks.append(tcpCliSock)
    print('OK')
        
def test():
    init(2,2,2)
    public.domainname='adidasbangbangtang.cn'
    email={'mail_from':'<root@adidasbangbangtang.cn>','rcpt_to': '<1476707699@qq.com>', 'text': 'content-type:text/plain;charset=utf-8\r\n这是一封测试邮件' }
    #rcpt_addr=email['rcpt_to'].strip('<>').split('@')[1]
    #send_email_remote(email, rcpt_addr)
    send_email(email)
