def create_middleware_client(context):
    """Creates a client for the Oracle middleware service."""
    import requests
    from trove.common import cfg
    
    CONF = cfg.CONF
    
    # Get middleware URL from config
    middleware_url = CONF.get('oracle_middleware_url', 'http://localhost:8000')
    
    class MiddlewareClient:
        def __init__(self, base_url):
            self.base_url = base_url
            
        def create_instance(self, name):
            """Create a new Oracle instance via middleware."""
            response = requests.post(
                f"{self.base_url}/deploy_oracle",
                json={"name": name}
            )
            return response.json()
            
        def get_status(self, container_id):
            """Get status of an Oracle instance."""
            response = requests.get(
                f"{self.base_url}/status/{container_id}"
            )
            return response.json()
            
        def delete_instance(self, container_id):
            """Delete an Oracle instance."""
            response = requests.delete(
                f"{self.base_url}/delete/{container_id}"
            )
            return response.json()
    
    return MiddlewareClient(middleware_url) 