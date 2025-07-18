import time, os, hashlib, re, requests

def get_hash(filename):
    return hashlib.md5(filename.encode('utf-8')).hexdigest()

def get_path(filename):
    return "cache/" + get_hash(filename)

def make_cache_file(filename):
    user = open(get_path(filename), "w", encoding='utf-8')
    user.write(str(int(time.time())))
    user.close()

def cache_file_exists(filename):
    return os.path.isfile(get_path(filename))

def within_24h(filename):
    
    user = open(get_path(filename), "r", encoding='utf-8')
    file_time = int(user.read())
    user.close()

    print(file_time)

    if len(str(file_time)) == 0:
        return False

    if (int(time.time()) - 10800) > file_time:
        return False
    return True

def too_many_requests(filename):
  
    if not cache_file_exists(filename):
        make_cache_file(filename)
        return False
    else:
        if within_24h(filename):
            return True
        else:
            make_cache_file(filename)
            return False

def key_valid(key):
    return re.search("^[A-Za-z0-9]{35,50}$", key)

def pod_valid(key):
    regexp = "itr-[a-f0-9]{32}-[a-f0-9]{6,12}-[a-z0-9]{5}"
    return re.search(regexp, key)

def server_connection(url, api_key):

    if not key_valid(api_key):
        return False

    url = url + "api/server/ping"
    API_KEY = api_key

    payload = {}
    headers = {
        'x-api-key': API_KEY,
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        return True
    return False