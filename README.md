# binder-template

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main)

This is a template repo for running robotics research Jupyter Notebooks on Binderhub.

## Quick Start

### Launcher Urls

- JupyterLab: https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=lab/tree/notebooks/mujoco.ipynb

- VScode: https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=vscode?folder=/home/jovyan/work

## Create a new VRB lab from this template

1. Login to Github.

1. Use this template repository to create a new repository or fork it. Forking will make it easier to sync with future updates.

1. Clone your git repo, add your notebooks, python code, other files to the repo.

1. Modify the [requirements.txt](requirements.txt) to install additional python packages.

1. Modify the [binder/Dockerfile](binder/Dockerfile) if your project needs additional APT packages.

    Examples:

    ```Dockerfile
    USER root
    RUN apt update
    RUN apt install -y ffmpeg
    ```

1. Launch your VRB lab instance, replacing the placeholder content inside the curly braces `{}` with your actual information, and open in web browser.

    ```
    https://binder.dev.intel4coro.de/v2/gh/{YOUR_GITHUB_USER_NAME}/{YOUR_REPO_NAME}/main?urlpath=lab/tree/{PATH_TO_NOTEBOOK}
    ```

    The first time it is launched, it will take some time to build the Docker image.

## Use custom base docker image

You can also other based images, such as your own built docker images or official ROS images.
And a few additional steps are required:

1. Install JupyterLab
1. Expose port 8888

Example Dockerfile use ROS1 official image:

```Dockerfile
FROM ros:noetic-ros-base

ENV SHELL=/bin/bash
ENV DEBIAN_FRONTEND=noninteractive

# Install jupyterlab and git
RUN apt-get update && apt-get install -y python3-pip git
RUN pip3 install jupyterlab

# Expose port for jupyterlab
EXPOSE 8888

# Copy repo to the image (optional)
ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
COPY . ${REPO_DIR}/
WORKDIR ${REPO_DIR}
# The entrypoint of the docker image
COPY binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## Development

### Run and build docker image Locally (Under repo directory)

- Build and run docker image:

  ```bash
  docker compose -f ./binder/docker-compose.yml up --build
  ```

- Open Web browser and go to http://localhost:8888/

- To stop and remove container:

  ```bash
  docker compose -f ./binder/docker-compose.yml down
  ```
