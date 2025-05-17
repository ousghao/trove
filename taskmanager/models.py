class BuiltInstanceTasks(BuiltInstance, NotifyMixin, ConfigurationMixin):
    """Task manager for built instances."""
    
    def delete_async(self):
        """Delete the instance using middleware."""
        from trove.common import clients
        
        # Get middleware client
        middleware_client = clients.create_middleware_client(self.context)
        
        # Delete instance via middleware
        result = middleware_client.delete_instance(self.compute_instance_id)
        
        if result['status'] != 'deleted':
            raise exception.InstanceDeletionError(
                "Failed to delete instance via middleware: %s" % result.get('error', 'Unknown error'))
        
        # Update database record
        self.db_info.deleted = True
        self.db_info.deleted_at = timeutils.utcnow()
        self.db_info.save()
        
        # Send notification
        self.send_usage_event('delete') 