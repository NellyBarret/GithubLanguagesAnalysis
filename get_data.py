import urllib.request
import json
from random import randrange
import requests
import os
from github import Github
import auth

base_url = "https://api.github.com/"
filename = "data4.json"
# To authenticate, copy "auth.json.skeleton" as "auth.json" (included in .gitignore) and fill it in
#client_id, oauth_token = auth.get_auth_data("auth.json")
USER_TOKEN = "NellyBARRET"
ACCESS_TOKEN = '4bd9e8825dfcbad7a55d377d76b8d15eb9df7139'


def get_languages(owner, project_name):
    complete_url = f"{base_url}repos/{owner}/{project_name}/languages"
    contents = urllib.request.urlopen(complete_url).read()
    return json.loads(contents)


def get_year(owner, project_name):
    """
    TODO : récupération de l'année du projet
    """
    if randrange(1, 1000) < 500:
        return 2010
    else:
        if randrange(1, 1000) < 500:
            return 2011
        else:
            return 2012


def getRepositoriesSince(since):
    # print("getting repo since " + str(since))
    complete_url = f"{base_url}repositories?since={since}"
    contents = requests.get(complete_url, auth=(USER_TOKEN, ACCESS_TOKEN))
    return contents.json()


def getGoodInfos(repo):
    repo = {'year': get_year(repo[0]['owner']['login'], repo[0]['name']),
              'languages': get_languages(repo[0]['owner']['login'], repo[0]['name'])}
    return repo


def getAllRepositories():
    local_repo = getRepositoriesSince(1)
    all_repositories = []
    all_repositories.append(getGoodInfos(local_repo))
    if type(local_repo) is list:
        repo_id = local_repo[len(local_repo) - 1]["id"]
    else:
        repo_id = local_repo["id"]
    while (local_repo and repo_id < 1000):
        local_repo = getRepositoriesSince(repo_id)
        repo_id = local_repo[len(local_repo) - 1]["id"]
        all_repositories.append(getGoodInfos(local_repo))
    return all_repositories


def get_in_shape(data):
    """
      Transforme les données brutes récupérées par getAllRepositories en données utilisables simplement pour le chord diagramme et le rayon de soleil :
       - Un fichier de sortie contenant l'utilisation des langagues au format JSON pour les rayons de soleil : { "Ruby": 34, "C": 50 ...}
       - Un fichier contenant la force des liens entre languages : {('Ruby', 'C'): 26, ('php', 'Ruby'): 55, ...}
    """

    # Fichier contenant l'utilisation, répartie par année
    comptage = {}
    for d in data:  # Parcours de chacun des repositories
        languages = d['languages']
        annee = d['year']
        if not(annee in comptage):
            comptage[annee] = {}
        sum_repo = 0
        for l in languages.keys():
            sum_repo += languages.get(l, 0)
        for l in languages.keys():  # Parcours de chacun des langages utilisés
            comptage[annee][l] = comptage[annee].get(l, 0) + 1 * (languages.get(l, 0) / sum_repo)
    f = open("usage.json", "w")
    f.write(json.dumps(comptage))
    f.close()


if __name__ == "__main__":
    all_r = getAllRepositories()
    print(all_r)
    get_in_shape(all_r)
