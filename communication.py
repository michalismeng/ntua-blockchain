import requests

def broadcast(hosts, message, api):
    responses = []
    timeouts = []
    for host in hosts:
        try:
            print('http://{}:{}/'.format(host['ip'], host['port']) + api)
            response = requests.post('http://{}:{}/'.format(host['ip'], host['port']) + api, json = message)
            responses.append(response.status_code == 200)
        except requests.exceptions.Timeout:
            timeouts.append(host)
    
    return len(timeouts) == 0 and all(responses)

