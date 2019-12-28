import urllib.request
import json
import requests
import auth

base_url = "https://api.github.com/"

# To authenticate, copy "auth.json.skeleton" as "auth.json" (included in .gitignore) and fill it in
client_id, oauth_token = auth.get_auth_data("auth.json")


def get_languages(owner, project_name):
    complete_url = f"{base_url}repos/{owner}/{project_name}/languages"
    contents = urllib.request.urlopen(complete_url).read()
    return json.loads(contents)


def getRepositoriesSince(since):
    # print("getting repo since " + str(since))
    complete_url = f"{base_url}repositories?since={since}"
    contents = requests.get(complete_url, auth=(client_id, oauth_token))
    return contents.json()


def getAllRepositories():
    local_repo = getRepositoriesSince(1)
    all_repositories = []
    all_repositories.append(get_languages(local_repo[0]['owner']['login'], local_repo[0]['name']))
    if type(local_repo) is list:
        repo_id = local_repo[len(local_repo) - 1]["id"]
    else:
        repo_id = local_repo["id"]
    while (local_repo and repo_id < 1000):
        local_repo = getRepositoriesSince(repo_id)
        repo_id = local_repo[len(local_repo) - 1]["id"]
        all_repositories.append(get_languages(local_repo[0]['owner']['login'], local_repo[0]['name']))
    return all_repositories


def write_in_file(data):
    formated_data = json.dumps(data)
    f = open("data.json", "w")
    f.write(formated_data)
    f.close()


def get_in_shape(data):
    """
      Transforme les données brutes récupérées par getAllRepositories en données utilisables simplement pour le chord diagramme et le rayon de soleil :
       - Un fichier de sortie contenant l'utilisation des langagues au format JSON pour les rayons de soleil : { "Ruby": 34, "C": 50 ...}
       - Un fichier contenant la force des liens entre languages : [{languages : {"Ruby", C++ }, "lien" : 30}, {languages : {"Ruby", Java }, "lien" : 42}, ... }
    """

    # Fichier contenant l'utilisation
    comptage = {}
    for d in data:  # Parcours de chacun des repositories
        sum_repo = 0
        for l in d.keys():
            sum_repo += d.get(l, 0)
        for l in d.keys():  # Parcours de chacun des langages utilisés
          comptage[l] = comptage.get(l, 0) + 1*(d.get(l, 0)/sum_repo)
    f = open("usage.json", "w")
    f.write(json.dumps(comptage))
    f.close()


if __name__ == "__main__":
    all_r = getAllRepositories()
    get_in_shape(all_r)
