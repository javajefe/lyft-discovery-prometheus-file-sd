# lyft-discovery-prometheus-file-sd
Exporter from [lyft/discovery](https://github.com/lyft/discovery) to Prometheus file_sd format.

Prometheus supports number of service-discovery mechanisms. One of them is [file-based](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#file_sd_config). To be able to use lyft/dyscovery as a service discovery for Prometheus we can simply periodically download full list of services metadata from the lyft/discovery and convert it into Prometheus file_sd format. That is exactly the purpose of this simple tool.

The tool periodically downloads metadata from Lyft/discovery, converts it into Prometheus file_sd format and stores set of files (one per metrics port, see also [lyft-discovery-registrator](https://github.com/javajefe/lyft-discovery-registrator)) into `/tmp/out` directory, so file names look like `/tmp/out/file_sd_8001.json`, `/tmp/out/file_sd_10000.json`. That directory can be mounted to Prometheus container and consumed by file_sd mechanism.

Environment variables for Docker container:
* `DISCOVERY_URL` - URL of [Lyft/discovery](https://github.com/lyft/discovery)
* `SERVICE_REPO_NAME` - service repository name in Lyft/discovery
* `REFRESH_INTERVAL` - refresh interval in seconds, default is 10
