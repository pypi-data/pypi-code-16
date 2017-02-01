# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs

from tacker_horizon.openstack_dashboard import api
from tacker_horizon.openstack_dashboard.dashboards.nfv.vnffgmanager \
    import tables
from tacker_horizon.openstack_dashboard.dashboards.nfv.vnffgmanager.tables \
    import VNFFGManagerItem
from tacker_horizon.openstack_dashboard.dashboards.nfv.vnffgmanager.tables \
    import VNFFGManagerItemList


class VNFFGManagerTab(tabs.TableTab):
    name = _("VNFFGManager Tab")
    slug = "vnffgmanager_tab"
    table_classes = (tables.VNFFGManagerTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_vnffgmanager_data(self):
        try:
            self._has_more = True
            VNFFGManagerItemList.clear_list()
            vnffgs = api.tacker.vnffg_list(self.request)
            for vnffg in vnffgs:
                try:
                    vnffg_desc_str = vnffg['description']
                except KeyError:
                    vnffg_desc_str = ""

                obj = VNFFGManagerItem(vnffg['name'],
                                       vnffg_desc_str,
                                       vnffg['status'],
                                       vnffg['id'])
                VNFFGManagerItemList.add_item(obj)
            return VNFFGManagerItemList.VNFFGLIST_P
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


class VNFFGManagerTabs(tabs.TabGroup):
    slug = "vnffgmanager_tabs"
    tabs = (VNFFGManagerTab,)
    sticky = True


class VNFFGDetailsTabs(tabs.TabGroup):
    slug = "VNFFG_details"
    sticky = True
