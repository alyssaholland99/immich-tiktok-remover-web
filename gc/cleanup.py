import os


def cleanup():
    immich_tiktok_pods = os.popen("kubectl get pods -n immich-tiktok-remover-api --no-headers | awk '{print $1}'").read()

    for pod in immich_tiktok_pods.splitlines():
        if ("Invalid API key" in os.popen("kubectl logs {} --tail 12 -n immich-tiktok-remover-api".format(pod)).read()) or ("immich_end" in os.popen("kubectl logs {} --tail 12 -n immich-tiktok-remover-api".format(pod)).read()):
            deployment_name = pod.split("-")[0] + "-" + pod.split("-")[1]
            os.popen("kubectl delete deployment {} -n immich-tiktok-remover-api".format(deployment_name)).read()
            print("Deleted deployment {}".format(deployment_name))
            os.popen("kubectl delete secret {}-auth -n immich-tiktok-remover-api".format(deployment_name.replace("itr", "immich-tiktok-remover"))).read()
            print("Deleted secret for {}".format(deployment_name))
            release_secrets = os.popen("kubectl get secrets -n immich-tiktok-remover-api | grep {}".format(deployment_name)).read()
            for secret in release_secrets.splitlines():
                os.popen("kubectl delete secret {} -n immich-tiktok-remover-api".format(secret))
                print("Deleted {} for {}".format(secret, deployment_name))
        else:
            print("{} is still running".format(pod))

cleanup()
