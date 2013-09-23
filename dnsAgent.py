#!/usr/bin/python
import sys
import os
import logging
import socket
import struct
import SocketServer
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

cache = {}

class DNSServer(SocketServer.BaseRequestHandler):
    allow_reuse_address = True
    daemon_threads = True

    def handle(self):
        data,sk = self.request
        if not data:return
        response = self._query(data)
        sk.sendto(response,self.client_address)

    def _query(self,data):
        tid,body = data[:2],data[2:]
        if body in cache:return ''.join([tid,cache[body]])
        query = ''.join([struct.pack('>H',len(data)),data])
        for s in dns:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(5)
            try:
                sk.connect(s)
                sk.send(query)
                response = sk.recv(2048)
                cache[body] = response[4:]
            except Exception:
                pass
            finally:
                sk.close()
            if response:return response[2:]

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

