import os
import json
import ast


def get_all_repos():
    all_repositories = []
    d="."
    folders = [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]  # list all folders in current dir
    print(folders)

    for folder in folders:
        if "__" not in folder and "." not in folder:
            for file in os.listdir("./"+folder):
                print(folder,"/",file)
                f = open(folder+"/"+file, 'r')
                file_content = json.loads(f.read())
                print(type(file_content))
                print(file_content)
                # objects = ast.literal_eval(file_content.)
                # print(type(objects))
                # print(objects)
                all_repositories.extend(file_content)
                print(all_repositories)
    # for folder in os.listdir("."):
    #     for file in os.listdir(folder):
    #         f = open(file, 'r')
    #         file_content = f.readlines()
    #         print(file_content)
    #         all_repositories.append(file_content)


if __name__ == "__main__":
    fruits = "['apple', 'orange', 'banana']"
    fruits = ast.literal_eval(fruits)
    print(fruits)
    get_all_repos()
