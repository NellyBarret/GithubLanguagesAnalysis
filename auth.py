import json

def get_auth_data(auth_file):
    auth_data = json.loads(open(auth_file,"r").read())
    return auth_data["client_id"], auth_data["oauth_token"]
