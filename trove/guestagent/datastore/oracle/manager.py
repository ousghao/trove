import requests
import logging
from trove.common import cfg
from trove.guestagent.datastore.manager import Manager
from trove.guestagent.datastore.service import DatastoreService

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class OracleManager(Manager):
    """Oracle Manager implementation."""

    def __init__(self):
        super(OracleManager, self).__init__()
        self.middleware_url = CONF.oracle_middleware_url

    def _call_middleware(self, method, endpoint, **kwargs):
        """Make a call to the middleware API."""
        url = f"{self.middleware_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error calling middleware: {str(e)}")
            raise

    def create_instance(self, context, instance_id, flavor, volume_size, databases=None,
                       users=None, restore_point=None, backup_id=None, overrides=None,
                       cluster_config=None, snapshot=None):
        """Create a new Oracle instance."""
        LOG.info(f"Creating Oracle instance {instance_id}")
        data = {
            "name": instance_id,
            "flavor": flavor,
            "volume_size": volume_size,
            "databases": databases,
            "users": users,
            "restore_point": restore_point,
            "backup_id": backup_id,
            "overrides": overrides,
            "cluster_config": cluster_config,
            "snapshot": snapshot
        }
        return self._call_middleware("POST", f"/v1.0/{context.project_id}/instances", json=data)

    def delete_instance(self, context, instance_id):
        """Delete an Oracle instance."""
        LOG.info(f"Deleting Oracle instance {instance_id}")
        return self._call_middleware("DELETE", f"/v1.0/{context.project_id}/instances/{instance_id}")

    def get_instance(self, context, instance_id):
        """Get instance details."""
        LOG.info(f"Getting Oracle instance {instance_id}")
        return self._call_middleware("GET", f"/v1.0/{context.project_id}/instances/{instance_id}")

    def list_instances(self, context):
        """List all Oracle instances."""
        LOG.info("Listing Oracle instances")
        return self._call_middleware("GET", f"/v1.0/{context.project_id}/instances")

    def get_datastore_versions(self, context):
        """Get available datastore versions."""
        LOG.info("Getting Oracle datastore versions")
        return self._call_middleware("GET", f"/v1.0/{context.project_id}/datastore_versions") 