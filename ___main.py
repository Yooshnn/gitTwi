import os
import tweepy
import requests
import base64
from github import Github, InputGitTreeElement
from pprint import pprint
from pathlib import Path

def run():
    tweepy_consumer_key = "***"
    tweepy_consumer_secret = "***"
    tweepy_access_token = "***"
    tweepy_access_token_secret = "***"
    tweepy_auth = tweepy.OAuthHandler(tweepy_consumer_key, tweepy_consumer_secret)
    tweepy_auth.set_access_token(tweepy_access_token, tweepy_access_token_secret)
    tweepy_api = tweepy.API(tweepy_auth)

    # Github username
    username = "***"
    password = "***" # use Personal access token instead!

    # pygithub object
    g = Github(username, password)
    repo = g.get_user().get_repo("***") # your repository name goes here

    commit_message = "***"
    master_ref = repo.get_git_ref('heads/master')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()

    # get list of uploadable files
    curPath = Path.cwd()
    fList = []
    fnList = []
    for p in curPath.iterdir():
        if p.is_file():
            ext = str(p).split(".")[-1]
            if ext == "py":
                if p.name == "___main.py": continue
                fList.append(str(curPath / p.name))
                fnList.append(p.name)
            elif ext == "cpp":
                fList.append(str(curPath / p.name))
                fnList.append(p.name)

    if len(fList) == 0:
        print("NO FILE DETECTED!")
        return

    for i, entry in enumerate(fList):
        with open(entry) as input_file:
            data = input_file.read()
        if entry.endswith('.png'):
            data = base64.b64encode(data)
        element = InputGitTreeElement(fnList[i], '100644', 'blob', data)
        element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)

    print("PUSH COMPLETE")
    print(*fnList)

    print("UPDATING TWITTER...")
    twitter_msg = "I uploaded "
    if len(fnList) > 20:
        twitter_msg += " ".join(fnList[:20])
        twitter_msg += " and " + str(len(fnList) - 20) + " more"
    else:
        twitter_msg += ", ".join(fnList)
    twitter_msg += " on my github!\n"
    twitter_msg += "https://github.com/Yooshnn/BOJ-Solution"
    tweepy_api.update_status(twitter_msg)

run()
