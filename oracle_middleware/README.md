# Oracle Middleware for Trove

This middleware service provides container-based Oracle database instances for Trove, replacing the default Nova VM-based implementation.

## Integration with DevStack

1. Add to your `local.conf`:
```ini
enable_plugin trove https://github.com/YOUR_USERNAME/trove.git
```

2. Run DevStack:
```bash
./stack.sh
```

The middleware service will be automatically installed and started after Trove services.

## Verification

1. Check service status:
```bash
systemctl status oracle-middleware
```

2. Check logs:
```bash
tail -f /var/log/trove/oracle-middleware.log
```

3. Test the API:
```bash
curl http://localhost:8000/status/test
```

4. Create an Oracle instance:
```bash
# Create datastore version
trove-manage datastore_update oracle "" 1
trove-manage datastore_version_update oracle 1.0 oracle 1.0 "oracle" "oracle" 1

# Create instance
trove create test-oracle 1 --size 1 --datastore oracle --datastore-version 1.0
```

## Troubleshooting

1. If service fails to start:
```bash
journalctl -u oracle-middleware
```

2. If middleware is not accessible:
```bash
curl -v http://localhost:8000/status/test
```

3. Check Docker status:
```bash
systemctl status docker
docker ps | grep oracle
```

## Manual Service Management

Start service:
```bash
sudo systemctl start oracle-middleware
```

Stop service:
```bash
sudo systemctl stop oracle-middleware
```

Restart service:
```bash
sudo systemctl restart oracle-middleware
```

View logs:
```bash
 