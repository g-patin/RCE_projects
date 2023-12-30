import requests
import json
import base64
import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import re
from tqdm.auto import tqdm
from tqdm.contrib import tzip

from ipywidgets import Layout, Button, Box
import ipywidgets as ipw
from IPython.display import display, clear_output


def create_jupyter_notebook(file_path, print_message):
    # Create the notebook content
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "outputs": [],
                "source": ["# Imports"]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "outputs": [],
                "source": [
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "from glob import glob\n",                    
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "outputs": [],
                "source": ["# Process functions"]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "outputs": [],
                "source": [
                    f"print('{print_message}')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.7.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    # Create the notebook file
    with open(file_path, 'w') as f:
        # Write the notebook content as JSON
        json.dump(notebook_content, f, indent=2)


def create_github_repository(username, token, repo_name, readme=True, readme_text='', folders=True):
    """Create a repository on Github

    Parameters
    ----------
    username : str
        Username of the Github account where the repository will be created
    token : str
        Personal access token in order to authentify yourself on Github
    repo_name : str
        Name of the repository
    readme : bool, optional
        When True, it adds the text provided by the argument 'readme_text', by default True
    readme_text : str, optional
        Text will be inserted in the readme file when the previous argument is set to True, by default ''
    folders : bool, optional
        When True, it creates folders 'figures' and 'notebooks' in the repository, by default True
    """
    

    # Define the API endpoint for creating a repository
    url = f"https://api.github.com/user/repos"

    # Define the headers with your personal access token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Define the repository data
    data = {
        "name": repo_name,
        "auto_init": True,
        "private": False,  # You can set this to True if you want a private repository
    }

    # Create the repository
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully on GitHub.")

        if folders:
            create_folders_in_repository(token, username, repo_name)
            add_readme_to_folders(token, username, repo_name)

        if readme:
            add_text_to_readme(token, username, repo_name, readme_text=readme_text) 
        
    else:
        print(f"Failed to create repository. Status code: {response.status_code}")
        print(response.text)


def create_folders_in_repository(token, username, repo_name):
    # Define the API endpoint for creating a file in the repository (to ensure folder creation)
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents"

    # Define the headers with your personal access token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Define the file data for 'notebooks' and 'figures' (empty files)
    file_data = [
        {
            "path": "notebooks/.placeholder",
            "message": "Create placeholder file for notebooks folder",
            "content": base64.b64encode(b"").decode(),  # Empty content
        },
        {
            "path": "figures/.placeholder",
            "message": "Create placeholder file for figures folder",
            "content": base64.b64encode(b"").decode(),  # Empty content
        },
    ]

    # Create the placeholder files in 'notebooks' and 'figures' directories
    for data in file_data:
        response = requests.put(url + f"/{data['path']}", headers=headers, json=data)

        if response.status_code == 201:
            print(f"Folder '{data['path']}' created successfully.")
        else:
            print(f"Failed to create folder '{data['path']}'. Status code: {response.status_code}")
            print(response.text)


def add_text_to_readme(token, username, repo_name, readme_text):
    # Define the API endpoint for retrieving the README.md file
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/README.md"

    # Define the headers with your personal access token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Retrieve the current README.md content and sha
    response = requests.get(readme_url, headers=headers)

    if response.status_code == 200:
        readme_data = response.json()
        sha = readme_data['sha']

        readme_content = readme_text
        # Read text from a .txt file and set it as the new content of README.md
        #with open("readme_content.txt", "r") as file:
        #   readme_content = file.read()

        encoded_content = base64.b64encode(readme_content.encode()).decode()

        data = {
            "message": "Update README.md",
            "content": encoded_content,
            "sha": sha
        }

        # Update the README.md file with the new content
        update_response = requests.put(readme_url, headers=headers, json=data)

        if update_response.status_code == 200:
            print("Content added to README.md successfully.")
        else:
            print(f"Failed to update README.md. Status code: {update_response.status_code}")
            print(update_response.text)
    else:
        print(f"Failed to retrieve README.md. Status code: {response.status_code}")
        print(response.text)


def add_readme_to_folders(token, username, repo_name):
    # Define the headers with your personal access token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Define the README.md content for the 'notebooks' and 'figures' directories
    readme_content = "This is the README for the folder."

    encoded_content = base64.b64encode(readme_content.encode()).decode()

    # Define the API endpoint for creating a README.md file in 'notebooks' and 'figures'
    readme_data = [
        {
            "path": "notebooks/README.md",
            "message": "Create README.md for notebooks folder",
            "content": encoded_content,
        },
        {
            "path": "figures/README.md",
            "message": "Create README.md for figures folder",
            "content": encoded_content,
        },
    ]

    # Create the README.md files in 'notebooks' and 'figures' directories
    for data in readme_data:
        response = requests.put(
            f"https://api.github.com/repos/{username}/{repo_name}/contents/{data['path']}",
            headers=headers,
            json=data,
        )

        if response.status_code == 201:
            print(f"README.md created for '{data['path']}' successfully.")
        elif response.status_code == 409:
            print(f"README.md already exists for '{data['path']}' in the repository.")
        else:
            print(f"Failed to create README.md for '{data['path']}'. Status code: {response.status_code}")
            print(response.text)


