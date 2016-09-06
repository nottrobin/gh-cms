#! /usr/bin/env python3

# Core moduels
from base64 import b64decode

# Third party modules
from flask import Flask
from github import Github
from yaml import load

config = load(open('config.yaml'))

api = Github(config['access-token'])
site = api.get_repo(config['repository'])


def create_branch(branch_name):
    return site.create_git_ref(
        'refs/heads/{branch_name}'.format(**locals()),
        site.get_branch(site.default_branch).commit.sha
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
        base=site.default_branch,
        head=branch_name
    )


def capitalise_first_letter(string):
    for index, char in enumerate(string):
        if not char.isdigit() and char != ' ':
            break

    return string[:index] + string[index:].capitalize()


def read_config():
    config_file = site.get_contents('gh-cms.yaml')
    return load(b64decode(config_file.content))


def find_includes_for_file(filepath):
    # Check file exists
    site.get_contents(filepath + '.html')

    includes = site.get_dir_contents('/_includes/' + filepath)

    editable_includes = []
    for include in includes:
        if include.name[-3:] == '.md':
            human_name = capitalise_first_letter(
                include.name.replace('.md', '').replace('-', ' ')
            )
            editable_includes.append(
                {
                    'human_name': human_name,
                    'path': include.path,
                    'filename': include.name
                }
            )

    return editable_includes

config = read_config()
editable_paths = config['editable_paths']

app = Flask(__name__)


@app.route("/")
def index():
    output = "<h1>Editable pages</h1>"
    output += "<ul>"

    for path in editable_paths:
        output += '<li><a href="/edit/{path}">{path}</a></li>'.format(
            path=path.strip('/')
        )

    output += "<ul>"

    return output


@app.route("/edit/<path>")
def edit(path):
    includes = find_includes_for_file(path)
    output = "<h1>Editing {path}</h1>".format(**locals())
    output += "<ul>"

    for include in includes:
        output += "<li>{name}</li>".format(name=include['human_name'])

    output += "</ul>"

    return output


if __name__ == "__main__":
    app.run()

# Site flow:
# - Start a new branch, or continue an existing one
# - Show top level list of editable files
#   - commits on the right hand side, with files edited
# - Show edit screen for all file parts
#   - create new commit on the right hand side
