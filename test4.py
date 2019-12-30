import json
import requests
import os
import auth
from datetime import datetime, date
import time
from sys import stdout
from time import sleep

base_url = "https://api.github.com/"
FILENAME = "shaped_data.json"
USER_TOKEN = "NellyBARRET"
ACCESS_TOKEN = '4bd9e8825dfcbad7a55d377d76b8d15eb9df7139'
fields = ["id", "name", "created_at", "year", "language", "languages_url", "stargazers_url", "size"]


def get_repo(repo_name, repo_user):
    """Get infos about a specific repo
    @type repo_name: str
    @param repo_name: the name of the user
    @type repo_user: str
    @param repo_user: the name of the repo
    """
    complete_url = base_url + f"repos/{repo_user}/{repo_name}"
    contents = requests.get(complete_url, auth=(USER_TOKEN, ACCESS_TOKEN))
    repo = contents.json()
    if "message" in repo:
        if "Bad credentials" in repo["message"]:
            raise Exception("Problème d'authentification")
        elif "Not Found" in repo["message"]:
            raise Exception("Repo inconnu")
    else:
        return repo


def get_since(since=1):
    """Get repositoties since an id
    @type since: int
    @param since: the id where the scrapping begins
    @rtype: int and json
    @returns: the last id of the scrapped repod and the json content of scrapped repos
    """
    print("getting repo since " + str(since))
    complete_url = base_url + "repositories?since=" + str(since)
    contents = requests.get(complete_url, auth=(USER_TOKEN, ACCESS_TOKEN))
    print(contents.json())
    while "message" in contents.json() and "rate limit" in contents.json()["message"]:
        print("LIMITE")
        # waiting for an hour
        for i in range(0, 3601):
            stdout.write("\r%d" % i)
            stdout.flush()
            sleep(1)
        stdout.write("\n")
        contents = requests.get(complete_url, auth=(USER_TOKEN, ACCESS_TOKEN))
    return contents.json()[-1]["id"], contents.json()  # dernier id du since + les repos


def shape_data(repo):
    """Selects relevant fields in the repo
    @type repo: json
    @param repo: The current json repo
    @rtype: json
    @returns: a dict containing relevant fields of the repo
    """
    current_repo = {}
    for field in fields:
        content_field = repo[field]
        if "_url" in field:  # type(content_field) is str and base_url in content_field:
            # lien => faire une requete
            url_field = content_field
            response = requests.get(url_field, auth=('NellyBARRET', ACCESS_TOKEN))
            field_name = field[:-4]

            if field == "stargazers_url":
                current_repo[field_name] = []
                for i in range(len(response.json())):
                    # parcours de tous les utilisateurs qui ont mis des etoiles
                    current_repo[field_name].append(
                        {"id": response.json()[i]["id"], "login": response.json()[i]["login"]})
            else:
                current_repo[field_name] = response.json()
        else:
            # pas de lien => recuperer directement le champ
            current_repo[field] = repo[field]
    return current_repo


def write_in_file(file, data, add_coma=True):
    """Write some data in a specified file
    @type file: a file (object, not filename)
    @param file: the file where to write
    @type data: str or json
    @param data: the data to write in the file
    @type add_coma: boolean
    @param add_coma: True to add a coma after data, False else
    """
    formatted_data = json.dumps(data, indent=4)
    file.write(formatted_data)
    if add_coma:
        file.write(",")


def clear_file(filename):
    """Clears the file from everything
    @type filename: str
    @param filename: the filename of the file to clear
    """
    f = open(filename, "w")
    f.write("")
    f.close()


def get_all_repos():
    all_repositories = []
    files = []
    for folder in os.listdir("."):
        for file in os.listdir(folder):
            f = open(file, 'r')
            file_content = f.readlines()
            print(file_content)
            files.append(file_content)


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
    last_since = 1
    count = 0
    while True:
        try:
            today = date.today()
            day = today.strftime("%b-%d-%Y")
            os.mkdir(day)
        except OSError:
            print("Creation of the directory %s failed" % day)
        now = datetime.now()
        filename = now.strftime("%b-%d-%Y_%H-%M-%S") + ".json"
        complete_filename = os.path.join(day, filename)
        print(filename)
        print("ici")
        clear_file(complete_filename)
        f = open(complete_filename, "a")
        f.write("[")
        last_since, data = get_since(last_since)
        for i in range(len(data)):
            repo = data[i]
            name = repo["name"]
            user = repo["owner"]["login"]
            complete_repo = get_repo(name, user)
            try:
                shaped_repo = shape_data(complete_repo)
            except:
                pass
            else:
                if i == len(data) - 1:
                    coma = False
                else:
                    coma = True
                write_in_file(f, shaped_repo, coma)
                count += 1
            print("repo", repo["id"], "count", count)
        f.write("]")
        f.close()
