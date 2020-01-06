import json
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
    fields = ["language", "year", "stargazers_url", "forks_count"]
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


def get_in_shape(data):
    """ Transforme les données brutes récupérée en données utilisables simplement pour nos diagrammes. Le format des données est le suivant :
      data = {
        "matrix": [],
        "languages": [],
        "languageToIndex": {},
        "metrics": {
          "numberOfProjects": []
        }
      }"""

    # Pour l'utilisation
    comptage = {}

    # Pour la matrice
    abscisse = {}
    matrice = {}
    cpt = 0

    # Pour les métriques
    metrics = {}

    # Premier parcours pour trouver l'ensemble des langages existants. C'est un double parcours pour simplifier le code de la matrice après
    for d in data:
        if 'language' in d:
            if not d['language'] in abscisse:
                abscisse[d['language']] = cpt

    # Puis calcul de l'ensemble des données
    for d in data:

        # Calcul de l'utilisation de chacun des langages
        if 'language' in d and 'year' in d:
            languages = d['language']
            annee = d['year']
            if not (annee in comptage):
                comptage[annee] = {}
            sum_repo = 0
            for l in languages.keys():
                sum_repo += languages.get(l, 0)
            for l in languages.keys():  # Parcours de chacun des langages utilisés
                comptage[annee][l] = comptage[annee].get(l, 0) + 1 * (languages.get(l, 0) / sum_repo)

        # Calcul de la matrice du nombre de projets en commun pour chaque langage
        if 'language' in d and 'year' in d:
            languages = d['language']
            annee = d['year']
            if not (annee in matrice):
                matrice[annee] = [[0] * len(abscisse)] * len(abscisse)
            for l1 in languages.keys():
                for l2 in languages.keys():
                    matrice[abscisse[l1], abscisse[l2]] += 1

        # Calcul des métriques pour chaque language
        for l in abscisse.keys():
            metrics[l] = {"nb_projects": 0, "stars": 0, "forks": 0}
        if 'language' in d:
            metrics[d['langage']] = {"nb_projects": metrics[d['langage']]['nb_projects'] + 1,
                                     "stars": metrics[d['langage']]['stars'] + d['stargazers'],
                                     "forks": metrics[d['langage']]['forks'] + d['forks_count']}

    # Et enfin, mise en forme des données comme prévu, et export des données dans un fichier
    abscisseIndex = {abscisse[i]: i for i in range(len(abscisse))}
    data = {"matrix": matrice,
            "languages": abscisse,
            "languageToIndex": abscisseIndex,
            "metrics": {"nb_projects": [metrics[lg]['nb_projects'] for lg in abscisse],
                        "cumulated_use_pourcentage": [comptage[lg] for lg in abscisse],
                        "stars": [metrics[lg]['stargazers'] for lg in abscisse],
                        "forks": [metrics[lg]['forks'] for lg in abscisse]}}
    f = open("data/data.json", "w")
    f.write(json.dumps(data))
    f.close()


if __name__ == "__main__":
    data = complete_shaped_data(700)
    pickle.dump(data, open('data/pickle', 'wb'))
    print(data)
    data = pickle.load(open('data/pickle', 'rb'))
    get_in_shape(data)
