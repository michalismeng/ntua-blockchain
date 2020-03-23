import requests
from settings import bootstrap_ip, bootstrap_port
import jsonpickle as jp

def unicast_bootstrap(api, message):
    return unicast((bootstrap_ip, bootstrap_port), api, message)

def unicast(host, api, message):
    ip, port = host
    message = jp.encode(message)
    response = requests.post('http://{}:{}/{}'.format(ip, port, api), message)
    return response.json()


def broadcast(hosts, api, message):
    responses = []
    timeouts = []
    message = jp.encode(message)

    for ip, port in hosts:
        try:
            response = requests.post('http://{}:{}/{}'.format(ip, port, api), message)
            responses.append(response.status_code == 200)

        except requests.exceptions.Timeout:
            timeouts.append((ip, port))
    
    return len(timeouts) == 0 and all(responses)

