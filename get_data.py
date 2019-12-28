import urllib.request
import json
from random import randrange
import requests
import os
from github import Github
import auth

base_url = "https://api.github.com/"
filename = "data3.json"
ACCESS_TOKEN = 'XXX'
g = Github(ACCESS_TOKEN)
# To authenticate, copy "auth.json.skeleton" as "auth.json" (included in .gitignore) and fill it in
client_id, oauth_token = auth.get_auth_data("auth.json")


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
    contents = requests.get(complete_url, auth=(client_id, oauth_token))
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


def write_in_file(data):
    formated_data = json.dumps(data)
    f = open("data.json", "w")
    f.write(formated_data)
    f.close()


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


def get_languages2(owner_name, project_name):
    """
    Get the list of languages of a project.
    :param owner_name: the owner of the project.
    :param project_name: the name of the project.
    :return: the JSON list of the languages that appear in the project.
    """
    complete_url = base_url + "repos/" + owner_name + "/" + project_name + "/languages"
    # XXX must be replaced by the Oauth token
    contents = requests.get(complete_url, auth=('NellyBARRET', 'XXX'))
    return contents.json()


def get_stars(owner_name, project_name):
    """
    Get the number of stars of a project.
    :param owner_name: the owner of the project.
    :param project_name: the name of the project.
    :return: the JSON list of the languages that appear in the project.
    """
    complete_url = base_url + "repos/" + owner_name + "/" + project_name
    # XXX must be replaced by the Oauth token
    contents = requests.get(complete_url, auth=('NellyBARRET', 'XXX'))
    print(contents.json())
    return contents.json()["stargazers_count"]


def get_test():
    fields = ["id", "created_at", "language", "languages_url", "stargazers_url", "size"]

    while True:
        complete_url = base_url + "repos/NellyBARRET/GithubLanguagesAnalysis"
        contents = requests.get(complete_url, auth=('NellyBARRET', 'XXX'))
        current_repo = {}
        for field in fields:
            content_field = contents.json()[field]
            if type(content_field) is str and base_url in content_field:
                # lien => faire une requete
                url_field = content_field
                response = requests.get(url_field, auth=('NellyBARRET', 'XXX'))

                if field == "stargazers_url":
                    current_repo[field] = []
                    for i in range(len(response.json())):
                        # parcours de tous les utilisateurs qui ont mis des etoiles
                        current_repo[field].append({"id": response.json()[i]["id"], "login": response.json()[i]["login"]})
                else:
                    current_repo[field] = response.json()
            else:
                # pas de lien => recuperer directement le champ
                current_repo[field] = contents.json()[field]
        print(current_repo)
        break


def get_repositories_since(since):
    print("getting repo since " + str(since))
    complete_url = base_url + "repositories?since=" + str(since)

    # XXX must be replaced by the Oauth token
    contents = requests.get(complete_url, auth=('NellyBARRET', 'XXX'))

    # contents = requests.get(complete_url)
    return contents.json()


def get_all_repositories(maxi):
    local_repo = get_repositories_since(1)
    print(local_repo)
    if "message" in local_repo and "Bad credentials" in local_repo["message"]:
        print("Erreur lors de l'authentification. Penser a mettre le token d'authentification")
        return
    else:
        all_repositories = [local_repo[0]]
        if type(local_repo) is list:
            repo_id = local_repo[len(local_repo) - 1]["id"]
        else:
            repo_id = local_repo["id"]
        while local_repo and repo_id < maxi:
            local_repo = get_repositories_since(repo_id)
            repo_id = local_repo[len(local_repo) - 1]["id"]
            all_repositories.append(local_repo[0])
        return all_repositories


def write_in_file(data):
    print("begin writing")
    # f=open(filename,"w+")
    formatted_data = json.dumps(data, indent=4)
    f = open(filename, "w")
    f.write(formatted_data)
    f.close()
    print("finished writing")


def get_attribute_from_file(attribute):
    with open(filename, 'r') as data_file:
        json_data = data_file.read()
    data = json.loads(json_data)
    result = []
    for project_object in data:
        print(project_object)
        owner_name = project_object["owner"]["login"]
        project_name = project_object["name"]
        if "language" in attribute:
            result.append(get_languages(owner_name, project_name))
        elif "star" in attribute:
            result.append(get_stars(owner_name, project_name))
        else:
            raise Exception("Bad attribute. Usage: language, star")
    print(result)
    return result


def search_github(keywords):
    query = '+'.join(keywords) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')

    print(f'Found {result.totalCount} repo(s)')

    for repo in result:
        print(repo)
        print(f'{repo.clone_url}, {repo.stargazers_count} stars')


# TODO:
#  * created_at


def get_all_languages(maxi):
    local_repo = get_repositories_since(1)
    print(local_repo)
    if "message" in local_repo and "Bad credentials" in local_repo["message"]:
        print("Erreur lors de l'authentification. Penser a mettre le token d'authentification")
        return
    else:
        all_repositories = [local_repo[0]]
        if type(local_repo) is list:
            repo_id = local_repo[len(local_repo) - 1]["id"]
        else:
            repo_id = local_repo["id"]
        while local_repo and repo_id < maxi:
            local_repo = get_repositories_since(repo_id)
            repo_id = local_repo[len(local_repo) - 1]["id"]
            all_repositories.append(local_repo[0])
        return all_repositories


if __name__ == "__main__":
    get_test()
    # print(g.get_user().get_repos())
    # search_github("chatbot")
    # get all data and write it in a JSON file
    # max_id = 100
    # all_r = get_all_repositories(max_id)
    # write_in_file(all_r)

    # get a specific attribute for each project
    # get_attribute_from_file("language")




if __name__ == "__main__":
    all_r = getAllRepositories()
    print(all_r)
    get_in_shape(all_r)
