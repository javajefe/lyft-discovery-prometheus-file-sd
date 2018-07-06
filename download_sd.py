import json
import logging
import os
import requests
import sys
import threading, functools, time

class PrometheusFileSdDownlowdTask:
    
    def __init__(self, serviceDiscoveryURL, repo_name, out_file_prefix):
        self.serviceDiscoveryURL = serviceDiscoveryURL
        self.repo_name = repo_name
        self.out_file_prefix = out_file_prefix
        self.connection_timeout = 5.0
        self.buckets = {}

    def __download_repo(self):
        response = requests.get("{}/v1/registration/repo/{}".format(self.serviceDiscoveryURL, self.repo_name), timeout=self.connection_timeout)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise ValueError("Bad response: {}".format(response.status_code))

    def __transformHostToPrometheusFileSD(self, host_data, port):
        return {
            "targets": ["{}:{}".format(host_data["ip_address"], port)], 
            "labels": {
                "local_cluster": host_data["service"], 
                "instance": host_data["tags"]["instance_id"],
                }
            }

    def __transformToPrometheusFileSD(self, repo_data):
        if not repo_data["hosts"]:
            raise ValueError("Empty response")
        for host in repo_data["hosts"]:
            metrics_ports = host["tags"]["metrics_ports"]
            if not metrics_ports:
                raise ValueError("metrics_ports is mandatory field in {}".format(host))
            for port in metrics_ports.split(","):
                if int(port) not in self.buckets.keys():
                    self.buckets[int(port)] = []
                self.buckets[int(port)].append(self.__transformHostToPrometheusFileSD(host, port))

    def download(self):
        logger.debug("------------------- Downloading -------------------")
        try:
            self.buckets = {}
            self.__transformToPrometheusFileSD(self.__download_repo())
            for port, conf in self.buckets.items():
                js = json.dumps(conf, indent=4)
                os.umask(0)
                file_name = "{}_{}.json".format(self.out_file_prefix, port)
                with open(os.open(file_name, os.O_CREAT | os.O_WRONLY, 0o777), 'w') as file:
                    file.write(js)
        except Exception as ex:
            logger.exception(ex)
        return 'Ok'

class PeriodicTimer(object):
    def __init__(self, interval, callback):
        self.interval = interval

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if result:
                self.thread = threading.Timer(self.interval,
                                              self.callback)
                self.thread.start()

        self.callback = wrapper

    def start(self):
        self.thread = threading.Timer(self.interval, self.callback)
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.NOTSET)
    logger = logging.getLogger()
    downloader = PrometheusFileSdDownlowdTask(sys.argv[1], sys.argv[2], sys.argv[3])
    timer = PeriodicTimer(int(sys.argv[4]), downloader.download)
    timer.start()
