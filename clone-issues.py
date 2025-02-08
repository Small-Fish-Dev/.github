import json
import subprocess
import time

ORG_NAME = "Small-Fish-Dev"
ORG_DATA_REPO = f'{ORG_NAME}/.github'
HELPER_REPO = f"{ORG_NAME}/default_labels_repo"


def get_repo_label_names(repo):
    x = subprocess.run([
        'gh', 'label', 'list', '-R', repo, '--json', 'name'
    ], capture_output=True, text=True)

    if x.returncode != 0:
        raise Exception('failed to get repo labels!')

    y = json.loads(x.stdout)
    r = []

    for i in y:
        r.append(i['name'])

    return r


def create_private_repo(repo, ignore_error=True):
    x = subprocess.run([
        'gh', 'repo', 'create', repo, '--private'
    ])

    if x.returncode != 0 and not ignore_error:
        raise Exception('failed to create repo!')


def delete_repo(repo, ignore_error=True):
    x = subprocess.run([
        'gh', 'repo', 'delete', repo, '--yes'
    ])

    if x.returncode != 0 and not ignore_error:
        raise Exception('failed to delete repo!')


def clone_labels(repo_from, repo_to):
    x = subprocess.run([
        'gh', 'label', 'clone', repo_from, '-R', repo_to, '-f'
    ])

    if x.returncode != 0:
        raise Exception(f'failed to clone labels!')


def delete_label(repo, label):
    x = subprocess.run([
        'gh', 'label', 'delete', label, '-R', repo, '--yes'])
    if x.returncode != 0:
        raise Exception(f'failed to remove label!')


def wipe_labels(repo):
    for i in get_repo_label_names(repo):
        delete_label(repo, i)


# Create a new helper repo that we'll delete later
# The repo will be created with our org's default labels
print("creating helper repo...")
create_private_repo(HELPER_REPO)

# Remove all existing labels from the .github repo
wipe_labels(ORG_DATA_REPO)

# Wait a second for things to complete
print("waiting a second...")
time.sleep(1)

# Copy the labels from the helper repo to the .github repo
print("copying labels from the helper repo to the .github repo...")
clone_labels(HELPER_REPO, ORG_DATA_REPO)

# Delete the helper repo
delete_repo(HELPER_REPO)

# Figure out the repos we want to update
repos_to_update = ['Small-Fish-Dev/Sauna', 'Small-Fish-Dev/SaunaUnity', 'Small-Fish-Dev/blocks-and-bullets',
                   'Small-Fish-Dev/boxfish', 'Small-Fish-Dev/Fishley', 'Small-Fish-Dev/deathcard', 'Small-Fish-Dev/harbinger', 'Small-Fish-Dev/hamsteria']

# Get the list of org scope labels
org_labels = get_repo_label_names(ORG_DATA_REPO)

for repo in repos_to_update:
    # Make sure all the org labels exist in this repo
    clone_labels(ORG_DATA_REPO, repo)

    # Get the labels we have in this repo
    repo_labels = get_repo_label_names(repo)

    # Remove all labels that shouldn't exist
    for label in repo_labels:
        if label not in org_labels:
            delete_label(repo, label)
