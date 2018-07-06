import json
import logging
import requests
import sys
import threading, functools, time

class PrometheusFileSdDownlowdTask:
    
    def __init__(self, serviceDiscoveryURL, repo_name, out_file):
        self.serviceDiscoveryURL = serviceDiscoveryURL
        self.repo_name = repo_name
        self.out_file = out_file
        self.connection_timeout = 5.0

    def __download_repo(self):
        response = requests.get("{}/v1/registration/repo/{}".format(self.serviceDiscoveryURL, self.repo_name), timeout=self.connection_timeout)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise ValueError("Bad response: {}".format(response.status_code))

    def __transformHostToPrometheusFileSD(self, host_data):
        return {
            "targets": [host_data["ip_address"]], 
            "labels": {
                "local_cluster": host_data["service"], 
                "instance": host_data["tags"]["instance_id"],
                }
            }

    def __transformToPrometheusFileSD(self, repo_data):
        if not repo_data["hosts"]:
            raise ValueError("Empty response")
        return [self.__transformHostToPrometheusFileSD(host) for host in repo_data["hosts"]]

    def download(self):
        try:
            js = json.dumps(self.__transformToPrometheusFileSD(self.__download_repo()), indent=4)
            with open(self.out_file, 'w') as file:
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
