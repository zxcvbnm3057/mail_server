# -*- coding: UTF-8 -*-
from threading import Thread
from Public_Class import*
import smpt_server
import pop_server
import get_email
import send_email
import auth

def get_configs():
    '''
    this function is used to get settings at startup
    '''

    '''
    These are the default Settings,
    and you can customize these Settings in
    
    '''
    connection_limit= 20
    process_limit = 100
    waiting_limit = process_limit*2
    domainname = 'example.com'
    db_user = "user"
    db_passwd = "passwd"
    db_name = ""
    db_host = "localhost"
    mailbox_path = '/var/spool/mail/'
    '''
    Read from the definition Settings here
    '''
    try:
        with open('config.conf','r') as f:
            settings=f.read()
            exec(setting)
    except:
        raise FileNotFoundError('Fail to read setting config')
    globals().update(locals())

def main():
    '''
    This function is used to start all the program modules
    '''
    public.domainname=domainname
    public.mailbox_path=mailbox_path
    #auth.init(db_host,db_name,db_user,db_passwd)
    #send_email.init(connection_limit, process_limit, waiting_limit)
    smpt_login_server = Thread(target=smpt_server.Login_server,args=(connection_limit, process_limit, waiting_limit))
    Sending_server = Thread(target=send_email.init,args=(connection_limit, process_limit, waiting_limit))
    pop_login_server = Thread(target=smpt_server.Login_server,args=(connection_limit, process_limit, waiting_limit))
    #Receiving_server = Thread(func='子进程函数名',args=())
    smpt_login_server.setDaemon(True)
    Sending_server.setDaemon(True)
    pop_login_server.setDaemon(True)
    #Receiving_server.setDaemon(True)
    smpt_login_server.start()
    Sending_server.start()
    pop_login_server.start()
    #Receiving_server.start()

if __name__ == '__main__':
    get_configs()
    main()
