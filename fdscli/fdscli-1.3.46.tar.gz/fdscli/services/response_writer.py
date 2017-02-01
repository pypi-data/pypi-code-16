# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
import tabulate
import json
import time
import datetime

from collections import OrderedDict

from fdscli.utils.converters.volume.recurrence_rule_converter import RecurrenceRuleConverter
from fdscli.model.health.health_category import HealthCategory
from fdscli.utils.byte_converter import ByteConverter
from fdscli.model.task.safeguard_task_status import SafeGuardTaskType
from fdscli.model.task.completion_status import CompletionStatus

class ResponseWriter():
    '''Pretty printing utility for a variety of model objects or collections of model objects.
    '''

    @staticmethod
    def write_not_implemented(args=None):
        print("\nThis feature is not yet available, but the fine people at Formation Data System are working tirelessly to make this a reality in the near future.\n")
    
    @staticmethod
    def writeTabularData( data, headers="keys" ):
        '''
        Parameters
        ----------
        :type data: list of lists or another tabular data type

        :param headers: A list of column headers
        '''
        if ( len(data) == 0 ):
            return
        else:
            print(tabulate.tabulate( data, headers=headers ))
            print("\n")
        
    @staticmethod
    def writeJson( data ):
        print("\n" + json.dumps( data, indent=4, sort_keys=True ) + "\n")
        
    @staticmethod
    def prep_volume_for_table( session, response ):
        '''
        making the structure table friendly
        '''        
        
        prepped_responses = []
        
        # Some calls return a singular volume instead of a list, but if we put it in a list we can re-use this algorithm
        if ( isinstance( response, dict ) ):
            response = [response]
        
        for volume in response:
            
            #figure out what to show for last firebreak occurrence
            safeguard_settings = volume.safeguard_settings
            safeguard_type = "None"
            
            if ( safeguard_settings is not None ):
                safeguard_type = volume.safeguard_settings.safeguard_type
                
            
            #sanitize the IOPs guarantee value
            iopsMin = volume.qos_policy.iops_min
            
            if ( iopsMin == 0 ):
                iopsMin = "None"
                
            #sanitize the IOPs limit
            iopsLimit = volume.qos_policy.iops_max
            
            if ( iopsLimit == 0 ):
                iopsLimit = "Unlimited"

            ov = OrderedDict()
            
            ov["ID"] = volume.id
            ov["Name"] = volume.name
            
            if ( session.is_allowed( "TENANT_MGMT" ) ):
                if volume.tenant is not None:
                    ov["Tenant"] = volume.tenant.name
                else:
                    ov["Tenant"] = ""
                    
                
            ov["State"] = volume.status.state
            ov["Type"] = volume.settings.type
            
            bytesUsed = ByteConverter.convertBytesToString( volume.status.current_usage.get_bytes(), 2 )
            allocated = ""
            
            if hasattr( volume.settings, "capacity"):
                all_str = ByteConverter.convertBytesToString( volume.settings.capacity.size, 0 )
                allocated = " / {}".format( all_str )
            
            ov["Usage"] = bytesUsed + allocated 
            ov["Safeguard Type"] = safeguard_type
            ov["Priority"] = volume.qos_policy.priority
            ov["IOPs Guarantee"] = iopsMin
            ov["IOPs Limit"] = iopsLimit
            ov["Media Policy"] = volume.media_policy
            
            prepped_responses.append( ov )
        #end of for loop 
            
        return prepped_responses
    
    @staticmethod
    def prep_snapshot_for_table( session, response ):
        '''
        Take the snapshot response and make it consumable for a table
        '''
        
        #The tabular format is very poor for a volume object, so we need to remove some keys before display
        resultList = []
        
        for snapshot in response:
            
            created = time.localtime( snapshot.created )
            created = time.strftime( "%c", created )
            
            retentionValue = snapshot.retention
            
            if ( retentionValue == 0 ):
                retentionValue = "Forever"
            
            ov = OrderedDict()
            
            ov["ID"] = snapshot.id
            ov["Name"] = snapshot.name
            ov["Created"] = created
            ov["Retention"] = retentionValue
            
            resultList.append( ov )   
        #end for loop
        
        return resultList

    @staticmethod
    def prep_snapshot_policy_for_table( session, response ):
        ''' 
        Take a snapshot policy and format it for easy display in a table
        '''
        
        results = []
        
        for policy in response:
            
            retentionValue = policy.retention_time_in_seconds
            
            if ( retentionValue == 0 ):
                retentionValue = "Forever"
        
            ov = OrderedDict()
            
            if policy.id != None:
                ov["ID"] = policy.id
            
            if ( policy.name != None and policy.name != "" ):
                ov["Name"] = policy.name

            ov["Retention"] = retentionValue
            ov["Recurrence Rule"] = RecurrenceRuleConverter.to_json( policy.recurrence_rule )
            
            results.append( ov )
        # end of for loop
        
        return results
            
    
    @staticmethod
    def prep_domains_for_table( session, response ):
        '''
        Take the domain JSON and turn it into a table worthy presentation
        '''
        results = []
        
        for domain in response:
            
            ov = OrderedDict()
            
            ov["ID"] = domain.id
            ov["Name"] = domain.name
            ov["Site"] = domain.site
            ov["State"] = domain.state
            
            results.append( ov )
        #end of for loop
        
        return results
    
    
    @staticmethod
    def prep_events_for_table( session, events ):
        '''
        Converts each event to an ordered dictionary for tabular display.

        Parameters
        ----------
        :type events: list(``model.event.Event``)
        :param events: List of event objects

        Returns
        -------
        :type list(``collections.OrderedDict``)
        '''
        results = []

        for event in events:

            ov = OrderedDict()

            if hasattr(event, "uuid") and event.uuid == -1:
                # event timestmap is returned as a dict with seconds and nanos
                # where seconds is the number of seconds since the epoch; and nanos
                # is the number of nanoseconds elapsed in the current second.
                creation_time = ResponseWriter.convert_java_instant( event.event_content.timestamp )
                creation_time_s = creation_time.strftime("%Y-%m-%d %H:%M:%S.%f")

                ov["Event Creation Time"] = creation_time_s
                ov["Severity"] = event.event_content.descriptor.severity
                ov["Categories"] = event.event_content.descriptor.categories
                ov["Message"] = event.event_message

            else:
                print("Found legacy event JSON message! \n {}".format(event.uuid))
                # event timestmap is returned in epoch millis
                # previous to build 13075 it was returned as an int value
                # but is now returned as a string
                etime_l = long(event.creation_time)
                etime_s = etime_l / 1000.0

                creation_time = datetime.datetime.fromtimestamp(etime_s)
                creation_time_s = creation_time.strftime("%Y-%m-%d %H:%M:%S.%f")
                ov["Event Creation Time"] = creation_time_s
                ov["Severity"] = event.severity

                # v08 model only supported a single category, but event
                # service model is a list
                ov["Categories"] = event.categories

                # default message contains the pre-formatted message
                ov["Message"] = event.default_message

            results.append( ov )

        return results

    @staticmethod
    def convert_java_instant( instant ):
        etime_s = long(instant["seconds"])
        etime_n = long(instant["nanos"])
        etime_micros = (etime_n / 1000)
        
        ds = datetime.datetime.fromtimestamp(etime_s)
        ds = ds.replace(hour=ds.hour,
                        minute=ds.minute,
                        second=ds.second,
                        microsecond=etime_micros)
        return ds        

    @staticmethod
    def prep_node_for_table( session, response ):
        '''
        Take nodes and format them to be listed in a table
        '''
        
        results = []
        
        for node in response:
            
            ov = OrderedDict()
            
            ov["ID"] = node.id
            ov["Name"] = node.name
            ov["State"] = node.state
            ov["IP V4 Address"] = node.address.ipv4address
            
            results.append( ov )
        
        return results
    
    @staticmethod
    def prep_services_for_table( session, response ):
        '''
        The service model is not yet sensible so we need to do some munging to get anything
        useful to the Screen.
        '''
        results = []
        
        for node in response:
            
            # we'll need this data for each service
            
            services = node.services
            
            for service_type in services:
                
                for service in services[service_type]:
                    
                    ov = OrderedDict()
                    ov["Node ID"] = node.id
                    ov["Node Name"] = node.name
                    ov["Service Type"] = service.name
                    ov["Service ID"] = service.id
                    ov["State"] = service.status.state
                    
                    results.append( ov )
                    
                # end of individual service for loop
            #end of service_typess for loop
            
        #end of nodes for loop
        
        return results

    @staticmethod
    def prep_safeguard_tasks_for_table( session, response ):
        '''Prep a list of SafeGuard task status records for tabular printing
        '''
        results = []

        for task_with_status in response:

            ov = OrderedDict()
            ov["Type"] = SafeGuardTaskType.getTableDisplayString(task_with_status.task_type)
            ov["Volume ID"] = task_with_status.volume_id
            ov["Remote Cloud"] = task_with_status.endpoint
            if task_with_status.bucket_name is not None:
                ov["Remote Volume/Bucket"] = task_with_status.bucket_name
            else:
                ov["Remote Volume/Bucket"] = task_with_status.exported_name

            ov["Percent Complete"] = int(task_with_status.percent_complete)
            ov["Status"] = str(task_with_status.status)
            if task_with_status.time_started > 0:
                request_time = time.localtime( long(task_with_status.time_started) )
                request_time = time.strftime( "%c", request_time )
                ov["Request Time"] = request_time
            else:
                ov["Request Time"] = 'unknown'

            ov["Task ID"] = task_with_status.uuid

            results.append( ov )

        return results

    @staticmethod
    def prep_safeguard_task_errors_for_table( session, response ):
        '''Prep a list of SafeGuard task errors for tabular printing
        '''
        results = []

        for task_with_status in response:

            if not task_with_status.status == CompletionStatus.failed:
                if not task_with_status.status == CompletionStatus.abandoned:
                    continue

            if task_with_status.error_type is None:
                continue

            ov = OrderedDict()
            ov["Task ID"] = task_with_status.uuid
            ov["Volume ID"] = task_with_status.volume_id
            ov["Remote Cloud"] = task_with_status.endpoint
            if task_with_status.bucket_name is not None:
                ov["Remote Volume/Bucket"] = task_with_status.bucket_name
            else:
                ov["Remote Volume/Bucket"] = task_with_status.exported_name

            ov["Error Type"] = task_with_status.error_type
            ov["Error Message"] = task_with_status.error_text

            results.append( ov )

        return results

    @staticmethod
    def prep_f1credentials_for_table( session, named_credentials ):
        '''Prepare a list of remote OM credentials for tabular printing

        Parameters
        ----------
        :type named_credentials: list(``model.common.NamedCredential``)

        Returns
        -------
        :type list(``collections.OrderedDict``)
        '''
        results = []

        for named_credential in named_credentials:

            ov = OrderedDict()
            ov["Named Credential ID"] = named_credential.digest
            ov["User ID"] = named_credential.user_id
            ov["Name"] = named_credential.name
            ov["OM Url"] = named_credential.url
            results.append( ov )

        return results

    @staticmethod
    def prep_s3credentials_for_table( session, named_credentials ):
        '''Prepare a list of S3 named credentials for tabular printing

        Parameters
        ----------
        :type named_credentials: list(``model.common.NamedCredential``)

        Returns
        -------
        :type list(``collections.OrderedDict``)
        '''
        results = []

        for named_credential in named_credentials:

            ov = OrderedDict()
            ov["Named Credential ID"] = named_credential.digest
            ov["User ID"] = named_credential.user_id
            ov["Name"] = named_credential.name
            ov["Url"] = named_credential.url
            ov["Bucket Name"] = named_credential.bucketname
            if named_credential.s3credentials is not None:
                ov["S3 Access Key"] = named_credential.s3credentials.access_key_id
                ov["S3 Secret Key"] = named_credential.s3credentials.secret_key
            results.append( ov )

        return results

    @staticmethod
    def prep_qos_presets( presets):
        '''
        Prep a list of qos presets for tabular printing
        '''
        
        results = []
        
        for preset in presets:
            
            ov = OrderedDict()
            
            iops_guarantee = preset.iops_guarantee
            
            if iops_guarantee == 0:
                iops_guarantee = "None"
                
            iops_limit = preset.iops_limit
            
            if iops_limit == 0:
                iops_limit = "Forever"
            
            ov["ID"] = preset.id
            ov["Name"] = preset.name
            ov["Priority"] = preset.priority
            ov["IOPs Guarantee"] = iops_guarantee
            ov["IOPs Limit"] = iops_limit
            
            results.append( ov )
            
        return results
    
    @staticmethod
    def prep_qos_for_table( qos ):
        '''
        Makes a table for the QOS object
        '''
        
        ov = OrderedDict()
        
        preset_id = qos.preset_id
        
        if ( preset_id == None ):
            preset_id = "None"
        
        if ( preset_id != "None" ):
            ov["Preset ID"] = preset_id
            
        ov["Priority"] = qos.priority
        ov["IOPs Guarantee"] = qos.iops_min
        ov["IOPs Limit"] = qos.iops_max
        
        results = [ov]
        
        return results
            
    @staticmethod
    def prep_safeguard_presets(presets):
        '''
        Prepare a list of safeguard presets for tabular printing

        Parameters
        ----------
        :type presets: list(``model.volume.SafeGuardPreset``)

        Returns
        -------
        :type list(``collections.OrderedDict``)
        '''
        results = []
        for preset in presets:

            ov = OrderedDict()

            if preset.id != None:
                ov["ID"] = preset.id

            if ( preset.name != None and preset.name != "" ):
                ov["Name"] = preset.name

            ov["Recurrence Rule"] = RecurrenceRuleConverter.to_json( preset.recurrence_rule )

            results.append( ov )

        return results

    @staticmethod
    def prep_subscriptions_for_table(subscriptions, credentials):
        '''
        Converts each subscription to an ordered dictionary for tabular display.

        Parameters
        ----------
        :type subscriptions: list(``model.volume.Subscription``)
        :param subscriptions: List of subscription objects

        :type credentials: dict(``model.common.NamedCredential``)
        :param credentials: Dictionary of named credential objects keyed by digest

        Returns
        -------
        :type list(``collections.OrderedDict``)
        '''
        results = []

        for subscription in subscriptions:

            if subscription.named_credential.name is None or len(subscription.named_credential.name) == 0:
                # Attempt named credential look-up and assignment
                if subscription.named_credential.digest in credentials:
                    subscription.named_credential = credentials[subscription.named_credential.digest]

            ov = OrderedDict()

            ov["Subscription ID"] = subscription.digest
            ov["Volume ID"] = subscription.volume_id

            if subscription.named_credential.name is None or len(subscription.named_credential.name) == 0:
                # Named credential was not immediately available
                ov["SafeGuard Type" ] = ''
            else:
                # Named credential is available
                if subscription.named_credential.isS3Credential() == True:
                    ov["SafeGuard Type"] = 'CDM-Snap'
                else:
                    ov["SafeGuard Type"] = 'CDR-Snap'

            ov["Name"] = subscription.name
            if subscription.recurrence_rule.is_empty() == True:
                ov["Recurrence Rule"] = "All Snapshots"
            else:
                ov["Recurrence Rule"] = RecurrenceRuleConverter.to_json( subscription.recurrence_rule )

            if subscription.named_credential.name is None or len(subscription.named_credential.name) == 0:
                # Named credential was not immediately available
                ov["Named Credential"] = subscription.named_credential.digest
                ov["Remote Volume/Bucket"] = ''
            else:
                # Named credential is available
                ov["Named Credential"] = subscription.named_credential.name
                if subscription.named_credential.isS3Credential() == True:
                    ov["Remote Volume/Bucket"] = subscription.named_credential.bucketname
                else:
                    ov["Remote Volume/Bucket"] = subscription.remote_volume

            results.append( ov )

        return results

    @staticmethod
    def prep_users_for_table(users):
        '''
        Put the list of users in a nice readable tabular format
        '''
        
        d_users = []
        
        for user in users:
            ov = OrderedDict()
            
            ov["ID"] = user.id
            ov["Username"] = user.name
            
            d_users.append( ov )
            
        return d_users
        
    @staticmethod
    def prep_tenants_for_table(tenants):
        '''
        Scrub the tenant objects for a readable tabular format
        '''
        
        d_tenants = []
        
        for tenant in tenants:
            ov = OrderedDict()
            
            ov["ID"] = tenant.id
            ov["Name"] = tenant.name
            d_tenants.append( ov )
            
        return d_tenants
    
    @staticmethod
    def prep_system_health_for_table(health):
        
#         if not isinstance(health, SystemHealth):
#             raise TypeError()
        
        ov = OrderedDict()
        
        cap_record = None
        service_record = None
        fb_record = None
        
        for record in health.health_records:
            if record.category == HealthCategory.CAPACITY:
                cap_record = record
            elif record.category == HealthCategory.SERVICES:
                service_record = record
            elif record.category == HealthCategory.FIREBREAK:
                fb_record = record
                
        
        ov["Overall"] = health.overall_health
        ov["Capacity"] = cap_record.state
        ov["Services"] = service_record.state
        ov["Firebreak"] = fb_record.state
        
        results =[ov]
        
        return results

    @staticmethod
    def prep_exports_for_table( session, exports ):
        '''
        Prep a list of exported volume records for tabular printing.

        Returns
        -------
        list(OrderedDict)
        '''
        results = []

        for exported_volume in exports:

            ov = OrderedDict()
            creation_time = time.localtime( long(exported_volume.creation_time) )
            creation_time = time.strftime( "%c", creation_time )
            ov["Export Name"] = exported_volume.obj_prefix_key
            ov["Type"] = exported_volume.source_volume_type
            ov["Source Volume Name"] = exported_volume.source_volume_name
            ov["Source Volume Id"] = exported_volume.source_volume_id
            if exported_volume.source_snapshot_id == 0:
                ov["Source Snapshot Id"] = ""
            else:
                ov["Source Snapshot Id"] = exported_volume.source_snapshot_id
            ov["Source Domain Id"] = exported_volume.source_domain_id
            ov["Export Time"] = creation_time
            # TODO: response does not include blob count yet
            # ov["Blob Count"] = exported_volume.blob_count
            results.append( ov )

        return results

    @staticmethod
    def prep_zone_for_table(session, response):
        '''
        Take the zone response and make it consumable for a table
        '''

        resultList = []

        for zone in response:

            ov = OrderedDict()

            ov["ID"] = zone.zid
            ov["Name"] = zone.name
            ov["Type"] = zone.ztype
            ov["State"] = zone.state
            if len(zone.iface) == 0:
                ov["Interface"] = "Default"
            else:
                ov["Interface"] = zone.iface
            ov["VIP"] = zone.zvip
            ov["AM1"] = zone.amList[0]
            ov["AM2"] = zone.amList[1]

            resultList.append(ov)
            # end for loop

        return resultList

