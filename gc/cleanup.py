import os


def cleanup():
    immich_tiktok_pods = os.popen("kubectl get pods -n immich-tiktok-remover-api --no-headers | awk '{print $1}'").read()

    for pod in immich_tiktok_pods.splitlines():
        if ("Invalid API key" in os.popen("kubectl logs {} --tail 12 -n immich-tiktok-remover-api".format(pod)).read()) or ("immich_end" in os.popen("kubectl logs {} --tail 12 -n immich-tiktok-remover-api".format(pod)).read()):
            deployment_name = pod.split("-")[0] + "-" + pod.split("-")[1]
            os.popen("kubectl delete deployment {} -n immich-tiktok-remover-api".format(deployment_name))
            print("Deleted deployment {}".format(deployment_name))
            os.popen("kubectl delete secret {}-auth -n immich-tiktok-remover-api".format(deployment_name.replace("itr", "immich-tiktok-remover")))
            print("Deleted secret for {}".format(deployment_name))
        else:
            print("{} is still running".format(pod))

cleanup()
