#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl
import ssl


def connect(host, username, password):
    si = None
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        si = SmartConnect(host=host, user=username, pwd=password,
                          port=443, connectionPoolTimeout=30)
    except IOError:
        pass
    return si