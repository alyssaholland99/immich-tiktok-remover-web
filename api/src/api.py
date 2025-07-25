from flask import Flask, jsonify, request
import subprocess, os, validators, time, re, requests

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from helpers import *

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.route('/status', methods=['GET'])
@limiter.limit("1/second")
def get_status():

    single_break = "<br>"
    double_break = "<br><hr><br>"

    api_status = "API Status: up" + double_break

    api_status += "Web & API server date and time:" +  get_api_status_command("date") + double_break

    api_status += "Working directory:" +  get_api_status_command("pwd") + double_break

    api_status += "Systemd Site File:" + get_api_status_command("cat /etc/systemd/system/itr-site.service") + double_break
    
    api_status += "Systemd API File:" + get_api_status_command("cat /etc/systemd/system/itr-api.service") + double_break
    
    api_status += "Systemd GC File:" + get_api_status_command("cat /etc/systemd/system/itr-gc.service") + double_break

    api_status += "Git log:" + get_api_status_command("git show --summary") + double_break

    api_status += "Current dir ls:" + get_api_status_command("ls") + double_break

    return api_status, 200

@app.route('/remove', methods=['POST'])
@limiter.limit("6/minute")
def remove_tiktoks():

    payload = request.get_json()
    immich_url = payload['immich_url']
    immich_api_key = payload['immich_api_key']
    repeat = payload['repeat']

    if immich_url[-1] != "/":
        immich_url += "/"

    if not key_valid(immich_api_key):
        return 'Not a valid API key', 400

    filename = "{}_{}".format(immich_url, immich_api_key)

    if too_many_requests(filename):
        return 'You can only use this service once every 3 hours', 429

    if not validators.url(immich_url):
        return 'Not a valid URL', 400
    
    if not server_connection(immich_url, immich_api_key):
        return 'Invalid server details, please check your input', 400
    

    # Unused as gc has taken over this
    # if cache_file_exists(filename):
    #    os.system('helm uninstall {} -n immich-tiktok-remover-api'.format(("immich-tiktok-remover-" + get_hash(filename))[:53]))

    fullname_override = "itr-" + get_hash(filename)
    secret_name = "immich-tiktok-remover-" + get_hash(filename)

    restart_timeout = "86400"

    if 'alyssaserver.co.uk' in immich_url:
        restart_timeout = "3600"

    hashed_deployment = ("itr-" + get_hash(filename))[:53]

    if repeat:
        os.system('helm upgrade --set IMMICH_URL={} --set IMMICH_API={} --set-string RESTART_TIMEOUT={} --set fullnameOverride={} --set SECRET_NAME={} --set image.tag=stable -n immich-tiktok-remover-api -i {} ../immich-tiktok-remover/'.format(immich_url, immich_api_key, restart_timeout, fullname_override, secret_name, hashed_deployment))
        print('helm upgrade --set IMMICH_URL={} --set IMMICH_API={} --set "RESTART_TIMEOUT=!!string {}" --set fullnameOverride={} --set SECRET_NAME={} --set image.tag=stable -n immich-tiktok-remover-api -i {} ../immich-tiktok-remover/'.format(immich_url, immich_api_key, restart_timeout, fullname_override, secret_name, hashed_deployment))
    else:
        os.system('helm upgrade --set IMMICH_URL={} --set IMMICH_API={} --set fullnameOverride={} --set SECRET_NAME={} --set image.tag=kube_testing -n immich-tiktok-remover-api -i {} ../immich-tiktok-remover/'.format(immich_url, immich_api_key, fullname_override, secret_name, hashed_deployment))

    return 'Starting process...\nConnected to your Immich instance.\nContainer Started.\nKeep an eye on your Immich instance, the tool is currently running.\nDeployment ID: ' + hashed_deployment, 200

@app.route('/logs', methods=['GET'])
@limiter.limit("2/second")
def kube_logs():

    immich_tiktok_pods = os.popen("kubectl get pods -n immich-tiktok-remover-api --no-headers | awk '{print $1}'").read()

    pod_id = ""
    for pod in immich_tiktok_pods.splitlines():
        if request.args.get('pod_id') == pod.rsplit("-", 2)[0]:
            pod_id = pod

    if pod_id == "":
        return "This pod no longer exists. Please submit a new pod request.", 404

    if not pod_valid(pod_id):
        return 'Not a valid pod', 400

    immich_tiktok_pods = os.popen("kubectl get pods -n immich-tiktok-remover-api --no-headers | awk '{print $1}'").read().splitlines()

    command = 'kubectl logs {} -n immich-tiktok-remover-api --timestamps --tail 200 | tr -d \'█\''.format(pod_id)

    pod_logs = os.popen(command).read()

    pod_log_filter = ""

    for l in pod_logs.splitlines():
        if not "Progress:" in l:
            pod_log_filter += l + '<br>'

    pod_log_filter = pod_log_filter.replace("Neither CUDA nor MPS are available - defaulting to CPU. Note: This module is much faster with a GPU.", "")

    pod_log_filter = pod_log_filter.replace("[1;32;40m", "").replace("[0m", "")

    if pod_log_filter == "":
        pod_log_filter = "Pod initialising... Please wait."

    return pod_log_filter, 200

if __name__ == '__main__':
    app.run(host="192.168.0.126")
