#!/usr/bin/python
import sys
import os
import logging
import socket
import struct
import SocketServer
import sqlite3
try:
    import gevent.monkey
except ImportError:
    gevent = None

dns = (
        ('8.8.8.8',53),
        ('8.8.4.4',53),
)

pidfile = '/var/run/dnsAgent.pid'

logging.basicConfig(
        level    = logging.DEBUG,
        filename = '/tmp/dnsAgent.log',
        filemode = 'a',
        datefmt  = '%Y-%m-%d %H:%M:%S',
        format   = '%(asctime)s %(levelname)-8s %(message)s',
)

class cache(object):
    def __init__(self):
        self.db = sqlite3.connect(":memory:",isolation_level=None)
        self.db.text_factory = str
        cursor = self.db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS T_CACHE (K BLOB PRIMARY KEY,V BLOB)')
        cursor.execute('PRAGMA journal_mode = off')
        cursor.close()
    def get(self,K):
        cursor = self.db.cursor()
        try:
            cursor.execute('SELECT V FROM T_CACHE WHERE K = ?',(K,))
            v = cursor.fetchall()
            if v:return v[0][0]
        except IndexError:
            pass
        finally:
            cursor.close()
    def put(self,K,V):
        cursor = self.db.cursor()
        try:
            cursor.execute('INSERT INTO T_CACHE (K,V) VALUES (?,?)',(K,V))
        except sqlite3.IntegrityError:
            cursor.execute('UPDATE T_CACHE SET V = ? WHERE K = ?',(V,K))
        finally:
            cursor.close()

class DNSServer(SocketServer.BaseRequestHandler):
    allow_reuse_address = True
    daemon_threads = True
    dns_cache = cache()

    def handle(self):
        data,sk = self.request
        if not data:return
        response = self._query(data)
        if response:sk.sendto(response,self.client_address)

    def _query(self,data):
        ID,K = data[:2],data[2:]
        V = self.dns_cache.get(K)
        if V:return ''.join([ID,V])
        query = ''.join([struct.pack('>H',len(data)),data])
        for s in dns:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(5)
            try:
                sk.connect(s)
                sk.send(query)
                response = sk.recv(2048)
            except Exception as e:
                logging.error('connect %s:%i error:%s'%(s[0],s[1],e))
                response = None
            finally:
                sk.close()
            if response:
                self.dns_cache.put(K,response[4:])
                return response[2:]

if __name__ == '__main__':
    try:
        pid = os.fork()
        if pid > 0:sys.exit(0)
        elif pid == 0:
            os.chdir('/')
            os.umask(0)
            os.setsid()
            pid = os.fork()
            if pid > 0:sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork error:%s\n'%e)
        sys.exit(1)
    pid = os.getpid()
    logging.info('start daemon, pid:%i'%pid)
    with open(pidfile,'w') as pf:pf.write(str(pid))
    try:
        gevent.monkey.patch_all(dns=gevent.version_info[0] >= 1)
        logging.info('Using gevent')
    except:
        logging.info('Using thread')
    try:
        server = SocketServer.ThreadingUDPServer(('localhost', 53), DNSServer)
        server.serve_forever()
        server.shutdown()
    except Exception as e:
        logging.warn('daemon has exited: %s'%e)
    finally:
        os.remove(pidfile)

