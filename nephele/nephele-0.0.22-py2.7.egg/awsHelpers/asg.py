def getInstanceIds(asgClient,asgName):
    #print "getInstanceIds: client:{} asgName:{}".format(asgClient,asgName)
    asgDescription = asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName])
    #print "asgDescription: {}".format(asgDescription)
    instances = asgDescription['AutoScalingGroups'][0]['Instances']
    instanceIds = [instance['InstanceId'] for instance in instances]
    return instanceIds
