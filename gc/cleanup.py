import os


def cleanup():
    immich_tiktok_pods = os.popen("kubectl get pods -n immich-tiktok-remover-api --no-headers | awk '{print $1}'").read()

    for pod in immich_tiktok_pods.splitlines():
        if "Invalid API key" in os.popen("kubectl logs {} --tail 12 -n immich-tiktok-remover-api".format(pod)).read():
            os.popen("kubectl delete deployment {} -n immich-tiktok-remover-api".format(pod[:-9]))
            print("Deleted deployment {}".format(pod[:-9]))
        else:
            print("{} is still running".format(pod))

cleanup()