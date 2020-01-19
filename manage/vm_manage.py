#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from pyVmomi import vim
import prettytable as pt
from pyVmomi import vmodl
from utils import return_none
from utils import pt2csv
from host_manage import get_hosts
from host_manage import enable_vm_auto_restart


def get_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """

    summary = virtual_machine.summary

    if summary.config.template is True:
        pass

    else:
        name = summary.config.name
        if summary.runtime.powerState == 'poweredOn':
            state = '已开机'
        elif summary.runtime.powerState == 'poweredOff':
            state = '已关机'
        elif summary.runtime.powerState == 'suspended':
            state = '已挂起'
        else:
            state = summary.runtime.powerState
        cpu = summary.config.numCpu
        memory_gb = str((summary.config.memorySizeMB) / 1024) + "GB"
        virtual_pci = summary.vm.config.hardware.device
        disks = ''
        for pci in virtual_pci:
            try:
                if pci.diskObjectId:
                    size =  int(pci.deviceInfo.summary[0:-3].replace(',', ''))/1024/1024
                    datastore = pci.backing.datastore.name
                    disk = str(size) + 'GB:' + str(datastore)
                    disks += ' ' + disk
            except Exception:
                pass
        nics = 0
        ip_list = []
        if summary.runtime.powerState == "poweredOn":
            for i in summary.vm.guest.net:
                net_tag = i.network
                nics += 1
                for j in i.ipAddress:
                    if bool(re.search('[a-z]', j)):
                        continue
                    else:
                        ip_message = str(net_tag) + ':' + str(j)
                        ip_list.append(ip_message)
            ip = ' '.join(ip_list)
        else:
            for i in summary.vm.network:
                net_tag = i.name
                nics += 1
                ip_message = net_tag + ':' + 'none_ip'
                ip_list.append(ip_message)
            ip = ' '.join(ip_list)
        vm_host = summary.runtime.host.name
        vm_info = (name, state, nics, ip, cpu, memory_gb,
                   disks, vm_host)
        return vm_info


def get_vm(content, name):
    try:
        name = unicode(name, 'utf-8')
    except TypeError:
        pass
    vm = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    for c in container.view:
        if c.name == name:
            vm = c
            break
    return vm


def get_url(si, ip, name):
    """
    Simple command-line program to generate a URL
    to open HTML5 Console in Web browser
    """
    content = si.RetrieveContent()
    vm = get_vm(content, name)
    vmid = str(vm).split(':')[1]
    vmid = vmid.replace("'", "")
    vm_ticket = vm.AcquireTicket("webmks")

    session_ticket = si.content.sessionManager.AcquireCloneTicket()

    url_60 = "https://" + str(ip) + ":9443" + "/vsphere-client/webconsole.html?vmId=" + str(vmid)
    url_60 = url_60 + "&vmName=" + vm.name + "&serverGuid=" + str(vm.config.instanceUuid) + "&locale=zh_CN&host="
    url_60 = url_60 + ip + ":" + str(vm_ticket.port) + "&sessionTicket="
    url_60 = url_60 + session_ticket + "&thumbprint=" + vm_ticket.sslThumbprint

    url_65 = "https://" + str(ip) + "/ui/webconsole.html?vmId=" + str(vmid)
    url_65 = url_65 + "&vmName=" + vm.name + "&serverGuid=" + str(vm.config.instanceUuid) + "&host="
    url_65 = url_65 + ip + ":" + str(vm_ticket.port) + "&sessionTicket="
    url_65 = url_65 + session_ticket + "&thumbprint=" + vm_ticket.sslThumbprint + "&locale=zh-CN"

    url = url_60 + "\n" + url_65
    return url


def show_vm(si):
    content = si.RetrieveContent()
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)
    children = containerView.view
    vmtb = pt.PrettyTable()
    vmtb.field_names = ['名称', '状态', '虚拟网卡数', 'IP', 'CPU',
                        '内存GB', '磁盘',  '所在主机']
    for child in children:
        try:
            if get_vm_info(child) is not None:
                vm_message = get_vm_info(child)
                vmtb.add_row(vm_message)
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
    print(vmtb)
    return vmtb


def migrate_vm(vm, datastore, target_host):
    spec = vim.vm.RelocateSpec(datastore=datastore, host=target_host)
    vm.RelocateVM_Task(spec=spec, priority="highPriority")


def config_vm(vm, memory_gb, cpu):
    spec = vim.vm.ConfigSpec(memoryMB=memory_gb*1024, numCPUs=cpu)
    vm.ReconfigVM_Task(spec=spec)

def auto_start_vm(si, start_delay=3):
    hosts = get_hosts(si)
    for host in hosts:
        enable_vm_auto_restart(host, start_delay)


def manage_vm(si, **kwargs):
    if kwargs['manage_vm'] == 'show_vm':
        try:
            if kwargs['output_csv'] is True:
                vmtb = show_vm(si).get_string()
                pt2csv(vmtb)
            else:
                show_vm(si)
        except Exception:
            show_vm(si)
    elif kwargs['manage_vm'] == 'auto_start_vm':
        if start_delay:
            auto_start_vm(si, start_delay=start_delay)
        else:
            auto_start_vm(si)
    if kwargs.has_key('vm_name'):
        content = si.RetrieveContent()
        vm = get_vm(content, kwargs['vm_name'])
        if kwargs['manage_vm'] == 'start_vm':
            vm.PowerOnVM_Task()
        elif kwargs['manage_vm'] == 'stop_vm':
            vm.PowerOffVM_Task()
        elif kwargs['manage_vm'] == 'suspend_vm':
            vm.SuspendVM_Task()