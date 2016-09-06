#! /usr/bin/env python

from base64 import b64decode
from github import Github

with open('access-token.txt') as token_file:
    token = token_file.read().strip()

api = Github(token)
site = api.get_repo('nottrobin/gh-cms-example-site')


def create_branch(branch_name):
    return site.create_git_ref(
        'refs/heads/{branch_name}'.format(**locals()),
        site.get_branch('master').commit.sha
    )


def commit_change(branch_name):
    index_file = site.get_contents('index.html')
    index_content = b64decode(index_file.content)
    updated_content = index_content.replace('<html>', '<html lang="en">')

    return site.update_file(
        path='/index.html',
        message='Add language to markup',
        content=updated_content,
        sha=index_file.sha,
        branch=branch_name
    )


def create_pull_request(branch_name):
    return site.create_pull(
        title="Add language to markup",
        body=(
            "# Description\n\nAdd `lang=en` to the HTML tag.\n"
            "# QA\n\nThis will literally change nothing of significance."
        ),
        base="master",
        head=branch_name
    )

branch_name = "add-language"
create_branch(branch_name)
commit_change(branch_name)
pull = create_pull_request(branch_name)

print pull.html_url
