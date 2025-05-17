@classmethod
def create(cls, context, name, flavor_id, image_id, databases, users,
           datastore, datastore_version, volume_size, backup_id,
           availability_zone=None, nics=None,
           configuration_id=None, slave_of_id=None, cluster_config=None,
           replica_count=None, volume_type=None, modules=None,
           locality=None, region_name=None, access=None):
    """Create a new instance using the middleware instead of Nova."""
    from trove.common import clients
    
    # Create middleware client
    middleware_client = clients.create_middleware_client(context)
    
    # Create instance via middleware
    result = middleware_client.create_instance(name)
    
    if result['status'] != 'created':
        raise exception.InstanceCreationError(
            "Failed to create instance via middleware: %s" % result.get('error', 'Unknown error'))
    
    # Create database record
    db_info = DBInstance.create(
        name=name,
        flavor_id=flavor_id,
        tenant_id=context.project_id,
        volume_size=volume_size,
        datastore_version_id=datastore_version.id,
        task_status=InstanceTasks.BUILDING,
        configuration_id=configuration_id,
        slave_of_id=slave_of_id,
        cluster_id=cluster_config.get('id') if cluster_config else None,
        shard_id=cluster_config.get('shard_id') if cluster_config else None,
        type=cluster_config.get('instance_type') if cluster_config else None,
        region_id=region_name,
        access=access
    )
    
    # Store container ID and IP
    db_info.compute_instance_id = result['cid']
    db_info.hostname = result['ip']
    db_info.save()
    
    # Create service status
    service_status = InstanceServiceStatus.create(
        instance_id=db_info.id,
        status=srvstatus.ServiceStatuses.NEW
    )
    
    # Add modules if specified
    if modules:
        cls.add_instance_modules(context, db_info.id, modules)
    
    return SimpleInstance(context, db_info, service_status) 