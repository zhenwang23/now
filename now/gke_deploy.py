import json
from os.path import expanduser as user

import cowsay

from now.deployment.flow import cmd
from now.dialog import prompt_plus


def ask_projects(options):
    options = sorted(options, key=lambda x: x.lower())
    questions = [
        {
            'type': 'list',
            'name': 'project',
            'message': 'What project you want to use for kubernetes deployment?',
            'choices': options,
        }
    ]
    return prompt_plus(questions, 'project')


def ask_regions(options):
    questions = [
        {
            'type': 'list',
            'name': 'region',
            'message': 'Which region to chose?',
            'choices': options,
            'filter': lambda val: val.lower(),
        }
    ]
    return prompt_plus(questions, 'region')


def ask_zones(options):
    questions = [
        {
            'type': 'list',
            'name': 'zone',
            'message': 'Which zone you would like to select?',
            'choices': options,
        }
    ]
    return prompt_plus(questions, 'zone')


# Google cloud authentication ->
def init_gcloud(gcloud_path):
    cmd(f'{gcloud_path} auth login', std_output=True)


# List the projects and present it as options to user
def get_project(gcloud_path):
    project_list = []
    output, _ = cmd(f'{gcloud_path} projects list --format=json')
    projects = output.decode('utf-8')
    projects = json.loads(projects)
    for proj in projects:
        project_list.append(proj['projectId'])

    return ask_projects(project_list)


def get_region(gcloud_path):
    regions_list = []
    output, _ = cmd(f'{gcloud_path} compute regions list --format=json')
    regions = output.decode('utf-8')
    regions = json.loads(regions)
    for region in regions:
        regions_list.append(region['name'])

    return ask_regions(regions_list)


def get_zone(region, gcloud_path):
    zones_list = []
    output, _ = cmd(f'{gcloud_path} compute zones list --format=json')
    zones = output.decode('utf-8')
    zones = json.loads(zones)
    for zone in zones:
        if region in zone['name']:
            zones_list.append(zone['name'])

    return ask_zones(zones_list)


def final_confirmation():
    questions = [
        {
            'type': 'list',
            'name': 'proceed',
            'message': 'Creating a cluster will create some costs. '
            'Are you sure you want to continue? '
            'Prices can be checked here: '
            'https://cloud.google.com/kubernetes-engine/pricing',
            'choices': [
                {'name': '💸🔥 yes', 'value': True},
                {'name': ':⛔ no', 'value': False},
            ],
        }
    ]
    proceed = prompt_plus(questions, 'proceed')
    if proceed:
        print('Another authentication step is required')
    else:
        cowsay.cow('see you soon 👋')
        exit(0)


def create_gke_cluster():
    gcloud_path, _ = cmd('which gcloud')
    if not gcloud_path:
        gcloud_path = user('~/.cache/jina-now/google-cloud-sdk/bin/gcloud')
    application_name = 'jina-now'
    init_gcloud(gcloud_path)
    proj = get_project(gcloud_path)
    cmd(f'{gcloud_path} config set project {proj}')
    region = get_region(gcloud_path)
    cmd(f'{gcloud_path} config set compute/region {region}')
    zone = get_zone(region, gcloud_path)
    cmd(f'{gcloud_path} config set compute/zone {zone}')
    final_confirmation()
    cmd(
        f'/bin/bash ./now/scripts/gke_deploy.sh {application_name} {gcloud_path}',
        std_output=True,
    )
    print('True')


if __name__ == '__main__':
    create_gke_cluster()
