#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyVmomi import vim
from utils import pt2csv

def get_hosts(si):
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.HostSystem], True)
    obj = [host for host in container.view]
    return obj


def enable_vm_auto_restart(host, start_delay):
    print "Enabling Auto Restart for Host"
    print "The Selected Host is \n" + host.name
    print "Setting the Selected Host default AutoStartManager"
    hostDefSettings = vim.host.AutoStartManager.SystemDefaults()
    hostDefSettings.enabled = True
    hostDefSettings.startDelay = int(start_delay)
    print"virtual machines and applying Auto Start settings"
    order = 1
    for vhost in host.vm:
        spec = host.configManager.autoStartManager.config
        spec.defaults = hostDefSettings
        auto_power_info = vim.host.AutoStartManager.AutoPowerInfo()
        auto_power_info.key = vhost
        print "The VM   is updated if On" + vhost.name
        print "VM Status is " + vhost.runtime.powerState
        if vhost.runtime.powerState == "poweredOff":
            auto_power_info.startAction = 'None'
            auto_power_info.waitForHeartbeat = 'no'
            auto_power_info.startDelay = -1
            auto_power_info.startOrder = -1
            auto_power_info.stopAction = 'None'
            auto_power_info.stopDelay = -1
        elif vhost.runtime.powerState == "poweredOn":
            # note use of constant instead of string
            auto_power_info.startAction = 'powerOn'
            auto_power_info.startDelay = -1
            auto_power_info.startOrder = -1
            auto_power_info.stopAction = 'None'
            auto_power_info.stopDelay = -1
            auto_power_info.waitForHeartbeat = 'no'
            spec.powerInfo = [auto_power_info]
            order = order + 1
            print "Apply Setting to Host"
            host.configManager.autoStartManager.ReconfigureAutostart(spec)


def get_host_info(host):
    """
    Print information for a particular esxi host or recurse into a
    folder with depth protection
    """


    host_info = (host, cpu, memory_gb,
                 datastore, vswitch)
    return host_info


def show_host(si):
    content = si.RetrieveContent()
    container = content.rootFolder
    viewType = [vim.vim.HostSystem]
    recursive = True
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)
    children = containerView.view
    vmtb = pt.PrettyTable()
    vmtb.field_names = ['ESXi主机', 'CPU核数', '内存GB',
                        'Datastore', 'vSwitch']
    for child in children:
        try:
            if get_vm_info(child) is not None:
                vm_message = get_host_info(child)
                vmtb.add_row(vm_message)
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
    print(vmtb)
    return vmtb


def manage_vm(si, **kwargs):
    if kwargs['manage_host'] == 'show_host':
        if kwargs['output_csv'] is True:
            vmtb = show_host(si).get_string()
            pt2csv(vmtb)
        else:
            show_host(si)