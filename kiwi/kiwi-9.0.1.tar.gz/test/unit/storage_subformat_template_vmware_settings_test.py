from mock import patch

import mock

from .test_helper import *

from kiwi.storage.subformat.template.vmware_settings import (
    VmwareSettingsTemplate
)


class TestVmwareSettingsTempla(object):
    def setup(self):
        self.vmware = VmwareSettingsTemplate()

    def test_get_template_default(self):
        assert self.vmware.get_template().substitute(
            virtual_hardware_version='8',
            display_name='some-display-name',
            guest_os='suse',
            disk_id='0',
            vmdk_file='myimage.vmdk'
        )

    def test_get_template_with_periphery(self):
        assert self.vmware.get_template(
            memory_setup=True, cpu_setup=True, network_setup=True,
            iso_setup=True
        ).substitute(
            virtual_hardware_version='8',
            display_name='some-display-name',
            guest_os='suse',
            disk_id='0',
            vmdk_file='myimage.vmdk',
            nic_id='0',
            memory_size='4096',
            number_of_cpus='2',
            iso_id='0'
        )

    def test_get_template_scsi_disk(self):
        assert self.vmware.get_template(
            disk_controller='lsilogic'
        ).substitute(
            virtual_hardware_version='8',
            display_name='some-display-name',
            guest_os='suse',
            disk_id='0',
            scsi_controller_name='lsilogic',
            vmdk_file='myimage.vmdk'
        )

    def test_get_template_scsi_iso(self):
        assert self.vmware.get_template(
            iso_setup=True, iso_controller='scsi'
        ).substitute(
            virtual_hardware_version='8',
            display_name='some-display-name',
            guest_os='suse',
            disk_id='0',
            vmdk_file='myimage.vmdk',
            iso_id='0'
        )

    def test_get_template_custom_network(self):
        assert self.vmware.get_template(
            network_setup=True, network_mac='custom',
            network_connection_type='link', network_driver='foo'
        ).substitute(
            virtual_hardware_version='8',
            display_name='some-display-name',
            guest_os='suse',
            disk_id='0',
            vmdk_file='myimage.vmdk',
            nic_id='0',
            mac_address='98:90:96:a0:3c:58',
            network_connection_type='link',
            network_driver='foo'
        )
