# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

'''
Created on Apr 13, 2015

@author: nate
'''


class AbstractPlugin( object ):
    '''
    This is an abstract class to define what methods need
    to be overridden by a class that wishes to be a plugin

    Attributes
    ----------
    :type pos_arg_str: dict
    :attr pos_arg_str: User-visible positional argument names.
    '''

    pos_arg_str = {'credential': "CREDENTIAL", 'export_name': "EXPORT_NAME", 'name': "NAME",
        'task_id': "TASK_ID", 'volume_id': "VOLUME_ID", 'volume_name': "VOLUME_NAME"}

    continuous_protection_str = "continuous_protection"
    force_str = "force"
    priority_str = "priority"
    iops_guarantee_str = "iops_min"
    iops_limit_str = "iops_max"
    media_policy_str = "tiering_policy"
    volume_name_str = "volume_name"
    volume_id_str = "volume_id"
    volume_ids_str = "volume_ids"
    format_str = "format"
    fix_flag_str = "fix"
    name_str = "name"
    data_str = "data"
    type_str = "type"
    size_str = "size"
    size_unit_str = "size_unit"
    snapshot_id_str = "snapshot_id"
    time_str = "time"
    retention_str = "retention"
    node_id_str = "node_id"
    node_ids_str = "node_ids"
    discovered_str = "discovered"
    added_str = "added"
    all_str = "all"
    services_str = "services"
    service_str = "service"
    service_id_str = "service_id"
    state_str = "state"
    domain_name_str = "domain_name"
    domain_id_str = "domain_id"
    recurrence_rule_str = "recurrence_rule"
    frequency_str = "frequency"
    day_of_month_str = "day_of_month"
    day_of_week_str = "day_of_week"
    day_of_year_str = "day_of_year"
    week_str = "week"
    month_str = "month"
    hour_str = "hour"
    minute_str = "minute"
    policy_id_str = "policy_id"    
    timeline_preset_str = "data_protection_preset_id"
    qos_preset_str = "qos_preset_id"
    safeguard_preset_str = "safeguard_preset_id"
    user_name_str = "username"
    user_id_str = "user_id"
    tenant_id_str = "tenant_id"
    block_size_str= "block_size"
    block_size_unit_str = "block_size_unit"
    max_obj_size_str = "max_object_size"
    max_obj_size_unit_str = "max_object_size_unit"
    metrics_str = "metrics"
    start_str = "start"
    end_str = "end"
    points_str = "points"
    most_recent_str = "most_recent"
    size_for_value_str = "size_for_value"
    incoming_creds_str = "incoming_credentials"
    outgoing_creds_str = "outgoing_credentials"
    lun_permissions_str = "lun_permissions"
    initiators_str = "initiators"
    encryption_str = "encryption"
    compression_str = "compression"
    
    use_acls_str = "acls"
    use_root_squash_str = "root_squash"
    synchronous_str = "sync"
    clients = "clients"

    credential_str = "credential"
    hostname_str = "hostname"
    id_str = "id"
    incremental_str = "incremental"
    password_str = "password"
    port_str = "port"
    protocol_str = "protocol"
    remote_om_str = "remote_om"
    remote_volume_name_str = "remote_volume_name"
    s3_access_key_str = "s3_access_key"
    s3_bucket_name_str = "s3_bucket_name"
    s3_object_prefix_str = "s3_object_prefix"
    s3_secret_key_str = "s3_secret_key"
    url_str = "url"
    username_str = "username"

    zone_name = "name"
    zone_id = "id"
    zone_type = "type"
    zone_vip = "vip"
    zone_service_ids = "service_ids"
    zone_ids = "ids"
    zone_iface = "iface"

    def __init__(self):
        '''
        constructor
        '''
        self.__session = None

    def build_parser(self, parentParser, session): 
        raise NotImplementedError( "Required method for an FDS CLI plugin.")
    
    def detect_shortcut(self, args):
        raise NotImplementedError( "Required method for an FDS CLI plugin.")
    
    @property
    def arg_str(self):
        return "-"
    
    @property
    def session(self):
        return self.__session
    
    @session.setter
    def session(self, session):
        self.__session = session

    def add_force_arg(self, parser):
        '''Any command that might prompt for confirmation should support --force flag.
        '''
        parser.add_argument("-f", "--force", help=("Suppress confirmation prompt(s) when deleting objects."),
            action="store_true")

    def add_format_arg(self, parser):
        '''
        Add the format argument to the passed in parser
        '''
        parser.add_argument("-" + AbstractPlugin.format_str, help=("Specify the result format"),
            choices=["json","tabular"], required=False)

    def prompt(self, query_str):
        '''Prompt for confirmation.

        Recommended for highly destructive commands.
        Any command that might prompt for confirmation should support --force flag.

        Parameters
        ----------
        :type query_str: string
        :param query_str: The text to display to user in the prompt

        Returns
        -------
        :type bool
        '''
        response = raw_input('%s [yes/no]: ' % query_str)
        try:
            if response in ['yes', 'YES', 'y', 'Y', 'Yes']:
                return True
        except ValueError:
            return False
        return False
