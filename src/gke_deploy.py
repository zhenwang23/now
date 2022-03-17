import json
import subprocess
import time

import cowsay
from src.deployment.flow import cmd
from src.dialog import prompt_plus


def auth_cmd(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    time.sleep(2)
    print('Enter verification code: ')
    process.communicate()


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
            'message': 'Which region do chose?',
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
def init_gcloud():
    auth_cmd('gcloud auth login')


# List the projects and present it as options to user
def get_project():
    project_list = []
    output, _ = cmd('gcloud projects list --format=json')
    projects = output.decode('utf-8')
    projects = json.loads(projects)
    for proj in projects:
        project_list.append(proj['projectId'])

    return ask_projects(project_list)


def get_region():
    regions_list = []
    output, _ = cmd('gcloud compute regions list --format=json')
    regions = output.decode('utf-8')
    regions = json.loads(regions)
    for region in regions:
        regions_list.append(region['name'])

    return ask_regions(regions_list)


def get_zone(region):
    zones_list = []
    output, _ = cmd('gcloud compute zones list --format=json')
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
    application_name = 'jina-now'
    init_gcloud()
    proj = get_project()
    cmd(f'gcloud config set project {proj}')
    region = get_region()
    cmd(f'gcloud config set compute/region {region}')
    zone = get_zone(region)
    cmd(f'gcloud config set compute/zone {zone}')
    final_confirmation()
    # with yaspin(custom_spinner().weather, text="create cluster") as spinner:
    cmd(
        f'/bin/bash ./src/scripts/gke_deploy.sh {application_name}',
        output=False,
        error=False,
    )
    # spinner.ok('🌥')


if __name__ == '__main__':
    create_gke_cluster()
