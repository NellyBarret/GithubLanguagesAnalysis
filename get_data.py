import json
import random

import requests
from sys import stdout
from time import sleep
import pickle

from auth import get_auth_data

base_url = "https://api.github.com/"
filename = "data4.json"
# To authenticate, copy "auth.json.skeleton" as "auth.json" (included in .gitignore) and fill it in
USERNAME, ACCESS_TOKEN = get_auth_data("auth.json")


def get_repo(repo_name, repo_user):
    """Get infos about a specific repo
    @type repo_name: str
    @param repo_name: the name of the user
    @type repo_user: str
    @param repo_user: the name of the repo
    """
    complete_url = base_url + f"repos/{repo_user}/{repo_name}"
    contents = requests.get(complete_url, auth=(USERNAME, ACCESS_TOKEN))
    repo = contents.json()
    if "message" in repo:
        if "Bad credentials" in repo["message"]:
            raise Exception("Problème d'authentification")
        elif "Not Found" in repo["message"]:
            raise Exception("Repo inconnu")
    else:
        return repo


def get_repos_since(since=1):
    """Get repositoties since an id
    @type since: int
    @param since: the id where the scrapping begins
    @rtype: int and json
    @returns: the last id of the scrapped repo and the json content of scrapped repos
    """
    complete_url = base_url + "repositories?since=" + str(since)
    contents = requests.get(complete_url, auth=(USERNAME, ACCESS_TOKEN))
    while "message" in contents.json() and "rate limit" in contents.json()["message"]:
        # waiting for an hour
        for i in range(0, 3601):
            stdout.write("\r%d" % i)
            stdout.flush()
            sleep(1)
        stdout.write("\n")
        contents = requests.get(complete_url, auth=(USERNAME, ACCESS_TOKEN))
    return contents.json()[-1]["id"], contents.json()  # dernier id du since + les repos


def shape_data(repo):
    """Selects relevant fields in the repo
    @type repo: json
    @param repo: The current json repo
    @rtype: json
    @returns: a dict containing relevant fields of the repo
    """
    current_repo = {}
    fields = ["languages_url", "year", "stargazers_url", "forks_count"]
    for field in fields:
        if field == "year":
            # special handling for year field
            try:
                current_repo["year"] = repo["created_at"][:4]
            except:
                pass
        elif "_url" in field:
            # url => request
            try:
                content_field = repo[field]
                url_field = content_field
                response = requests.get(url_field, auth=(USERNAME, ACCESS_TOKEN))
                field_name = field[:-4]
                if field == "stargazers_url":
                    # special handling for stars field (need to go through each user)
                    current_repo[field_name] = len(response.json())
                else:
                    current_repo[field_name] = response.json()
            except:
                pass
        else:
            # no url => get the field without processing
            try:
                current_repo[field] = repo[field]
            except:
                pass
    return current_repo


def complete_shaped_data(until):
    """ Get full repositories data, truncated by shape_data, since an id
    :type until: int
    :param until: the id where the scrapping will ends
    :return: The json content of scrapped repos
    """
    actual = 0
    complete = []
    while actual < until:
        actual, contents = get_repos_since(actual)
        for repo in contents:
            name = repo["name"]
            user = repo["owner"]["login"]
            complete.append(shape_data(get_repo(name, user)))
    return complete


def random_shaped_data(maximum):
    """ Get full repositories data, truncated by shape_data, at a random place
    :type until: int
    :param until: the id where the scrapping will ends
    :return: The json content of scrapped repos
    """
    complete = []
    alea = random.randint(0, maximum)
    actual, contents = get_repos_since(alea)
    for repo in contents:
        name = repo["name"]
        user = repo["owner"]["login"]
        try:
            complete.append(shape_data(get_repo(name, user)))
        except:
            print("[WARN] erreur répcupération infos repo " + str(repo['id']))
            pass
    return complete


def get_in_shape(data):
    """ Transforme les données brutes récupérée en données utilisables simplement pour nos diagrammes."""

    calcul = {}

    # Premier parcours pour trouver l'ensemble des années existantes, et l'ensemble des langages existants par année
    for d in data:
        if 'year' in d:  # on a bien une année dans ce repo
            if not (d['year'] in calcul.keys()):  # Si elle n'existe pas encore, on la génère
                calcul[d['year']] = {"languages": []}
        if 'languages' in d:
            for l in d['languages']:  # Pour chacun des languages de ce repo
                if not l in calcul[d['year']]['languages']:
                    calcul[d['year']]['languages'].append(l)

    # Génération du language to index et des champs internes à chaque année (matrice et métriques), initialisés à 0
    for year in calcul.keys():
        calcul[year]['languages_to_index'] = {calcul[year]['languages'][i]: i for i in
                                              range(len(calcul[year]['languages']))}
        calcul[year]['matrix'] = [[0] * len(calcul[year]['languages']) for i in range(len(calcul[year]['languages']))]
        calcul[year]['metrics'] = {'number_of_projects': [0] * len(calcul[year]['languages']),
                                   'stars': [0] * len(calcul[year]['languages']),
                                   'forks': [0] * len(calcul[year]['languages'])}

    # Second parcours des données pour remplir les champs vides
    cpt = 0
    for d in data:
        if 'year' in d and 'languages' in d:
            for lang in d['languages']:  # Parcours des languages du dépot un à un

                # Compléter les métriques
                language_index = calcul[d['year']]['languages_to_index'][lang]
                calcul[d['year']]['metrics']['number_of_projects'][language_index] += 1
                calcul[d['year']]['metrics']['stars'][language_index] += d['stargazers']
                calcul[d['year']]['metrics']['forks'][language_index] += d['forks_count']

                # Compléter la matrice
                for lang2 in d['languages']:
                    language_index2 = calcul[d['year']]['languages_to_index'][lang2]
                    calcul[d['year']]['matrix'][language_index][language_index2] += 1

    # Calcul de l'évolution en tant que métrique
    annees = list(calcul.keys())
    annees.sort()
    calcul[annees[0]]['metrics']['evolution'] = [0] * len(calcul[annees[0]]['languages'])
    for i in range(1, len(annees)):  # La première année n'a pas d'évolution
        calcul[annees[i]]['metrics']['evolution'] = [0]*len(calcul[annees[i]]['languages'])
        for l in range(len(calcul[annees[i]]['languages'])):
            if (calcul[annees[i]]['languages'][l] in calcul[annees[i - 1]]['languages']):  # le language existait l'année dernière
                precedent_language_index = calcul[annees[i - 1]]['languages_to_index'][calcul[annees[i]]['languages'][l]]
                precedent_usage = calcul[annees[i]]['metrics']['number_of_projects'][l] / \
                                  calcul[annees[i - 1]]['metrics']['number_of_projects'][precedent_language_index]
                calcul[annees[i]]['metrics']['evolution'][l] = precedent_usage
            else:
                calcul[annees[i]]['metrics']['evolution'][l] = 0

    return calcul


if __name__ == "__main__":
    # Début janvier 2020, il y a un peu plus de 232367000 dépots sur gitlab
    # On va tirer aléatoirement dedans
    """data = []
    for i in range(15):
        print("Étape" + str(i))
        data = data + random_shaped_data(232367000)

    pickle.dump(data, open('data/pickle', 'wb'))"""
    data = pickle.load(open('data/pickle1', 'rb'))
    f = open("data/data.json", "w")
    f.write(json.dumps(get_in_shape(data)))
    f.close()
