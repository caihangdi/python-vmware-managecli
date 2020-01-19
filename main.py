#!/usr/bin/python
# -*- coding: utf-8 -*-


import getopt
import sys
from manage.message_info import get_vc_info
from manage.connect import connect
from manage.vm_manage import manage_vm

def verify_args(keys, kwargs):
    kw_keys = set(kwargs.keys())
    if keys.issubset(kw_keys):
        return
    else:
        need_args = keys - kw_keys
        print("Args %s is need" % [args for args in need_args])
        sys.exit(1)


def usage():
    print("""usage: python %s 
                              [--help]        获取帮助信息
                              [--show_vc]     展示所有的vcenter
                              [--manage_vm]   管理虚拟机
                              [--manage_host] 管理宿主机             
                """ % sys.argv[0])
    sys.exit()


def main():
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                   ["help","show_vc", "manage_vm=",
                                    "show_host", "get_vc", "get_vm",
                                    "get_vnc", "vm_name=", "vc_ip=",
                                    "vc_name=", "start_delay=",
                                    "output_csv"])
        default_value =True
        for opt_name, opt_value in opts:
            if opt_name in "--help":
                usage()
            elif opt_name in "--show_vc":
                kwargs["show_vc"] = default_value
            elif opt_name in "--manage_vm":
                kwargs["manage_vm"] = opt_value
            elif opt_name in "--show_host":
                kwargs["show_host"] = default_value
            elif opt_name in "--get_vc":
                kwargs["get_vc"] = default_value
            elif opt_name in "--get_vm":
                kwargs["get_vm"] = default_value
            elif opt_name in "--get_vnc":
                kwargs["get_vnc"] = default_value
            elif opt_name in "--vm_name":
                kwargs["vm_name"] = opt_value
            elif opt_name in "--vc_ip":
                kwargs["vc_ip"] = opt_value
            elif opt_name in "--vc_name":
                kwargs["vc_name"] = opt_value
            elif opt_name in "--start_delay":
                kwargs["start_delay"] = opt_value
            elif opt_name in "--output_csv":
                kwargs["output_csv"] = default_value
    except getopt.GetoptError as e:
        print("Invalid args: %s" % e)
        usage()

    if kwargs.has_key("show_vc"):
        get_vc_info()
    elif kwargs.has_key("manage_vm"):
        if kwargs["manage_vm"] not in ['show_vm', 'auto_start_vm',
                                       'start_vm', 'stop_vm', 'suspend_vm']:
            print("""python %s --vc_name <vc_name>/--vc_ip <vc_ip> --manage_vm
                                show_vm  展示该vcenter下的所有虚拟机 
                                auto_start_vm   设置所有开机状态虚拟机的开机自启
                                arg:    --start_delay <start_delay> 单位秒
                                        --output_csv 输出csv格式的文件
                                start_vm   开机虚拟机
                                stop_vm    关机虚拟机
                                suspend_vm   暂停虚拟机
                                arg:    --vm_name <vm_name> 虚拟机的名字           
                                """ % sys.argv[0])
        if kwargs.has_key("vc_ip"):
            keys = {"vc_ip"}
            ip, username, passwd = get_vc_info(ip=kwargs["vc_ip"])
        elif kwargs.has_key("vc_name"):
            keys = {"vc_name"}
            ip, username, passwd = get_vc_info(name=kwargs["vc_name"])
        else:
            keys = {"vc_name", "vc_ip"}
            ip, username, passwd = None, None, None
        if keys:
            verify_args(keys, kwargs)
            if ip and username and passwd:
                si = connect(ip, username, passwd)
                manage_vm(si, **kwargs)
    else:
        usage()
if __name__ == "__main__":
    main()