#!/usr/bin/python
# -*- coding: utf-8 -*-
import prettytable as pt


vcenter_message = {"test_vcenter_01": {"ip": "10.10.10.1",
                                       "username": "administrator@vsphere.local",
                                       "password": "ABC.def",
                                       "comment": "test_vcenter_01"}
                   "test_vcenter_02": {"ip": "10.10.10.2",
                                       "username": "administrator@vsphere.local",
                                       "password": "ABC.def",
                                       "comment": "test_vcenter_02"},
                   }

def get_vc_info(ip=None, name=None):
    if ip:
        for k in vcenter_message:
                if ip == vcenter_message[k]['ip']:
                    return vcenter_message[k]['ip'],\
                           vcenter_message[k]['username'],\
                           vcenter_message[k]['password']
    elif name:
        for k in vcenter_message:
                if name == k:
                    return vcenter_message[k]['ip'],\
                           vcenter_message[k]['username'],\
                           vcenter_message[k]['password']
    else:
        tb = pt.PrettyTable()
        tb.field_names = ['资源池', 'ip', '备注']
        for k in vcenter_message:
            row = []
            row.append(k)
            row.append(vcenter_message[k]["ip"])
            row.append(vcenter_message[k]["comment"])
            tb.add_row(row)
        print(tb)
