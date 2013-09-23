dnsAgent
========

dnsAgent is a tools which can forwarding DNS requests to TCP mode, and prevent DNS spoofing, and increase the speed by cache.

Usage
-----

1. Start daemon

        # python dnsAgent.py


2. Edit /etc/resolv.conf

        # echo "nameserver 127.0.0.1" > /etc/resolv.conf


    
Speed
-----

**First request**

    xx@creac ~ $ time nslookup www.google.com
    Server:		127.0.0.1
    Address:	127.0.0.1#53

    Non-authoritative answer:
    Name:	www.google.com
    ...
    Address: 74.125.128.103

    real	0m0.108s
    user	0m0.009s
    sys     0m0.006s
    
**Second request**

    xx@creac ~ $ time nslookup www.google.com
    Server:		127.0.0.1
    Address:	127.0.0.1#53
    
    Non-authoritative answer:
    Name:	www.google.com
    ...
    Address: 74.125.128.103
    
    real	0m0.015s
    user	0m0.008s
    sys 	0m0.006s

Tips
----
1. Support Python 2.6 and 2.7

2. Install gevent to improve performance


