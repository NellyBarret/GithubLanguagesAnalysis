import urllib.request
import json
import requests
import os
from github import Github

base_url = "https://api.github.com/"
filename = "data3.json"
ACCESS_TOKEN = 'XXX'
g = Github(ACCESS_TOKEN)

def get_languages(owner_name, project_name):
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


