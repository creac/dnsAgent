dnsAgent
========

dnsAgent is a tools which can forwarding DNS requests to TCP mode, and prevent DNS spoofing, and increase the speed by cache.

Usage
-----

**Tip: Currently only supports python 2.6 and 2.7**

I. Start daemon

    # python dnsAgent.py


II. Edit /etc/resolv.conf

    # echo "nameserver 127.0.0.1" > /etc/resolv.conf

