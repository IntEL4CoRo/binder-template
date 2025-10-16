# binder-template

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main)

This is a template repo for running robotics research Jupyter Notebooks on Binderhub.

Tutorials can be found here: https://vib.ai.uni-bremen.de/page/softwaretools/cloud-based-robotics-platform#zero-to-binder

## ROS2

To use ROS2, change the base image in the [Dockerfile](binder/Dockerfile), available image:

- intel4coro/base-notebook:jazzy
- intel4coro/base-notebook:humble

And edit the [entrypoint.sh](binder/entrypoint.sh) to:

```bash
#!/bin/bash
source ${ROS_PATH}/setup.bash

exec "$@"
```

## Use custom base docker image

You can also other based images, such as your own built docker images or official ROS images.
And a few additional steps are required:

1. Create a non-root user
1. Install JupyterLab
1. Expose port 8888

Example Dockerfile use ROS official image:

```Dockerfile
FROM ros:noetic-ros-base

USER root
ENV SHELL=/bin/bash
ENV DEBIAN_FRONTEND=noninteractive

# Create non-root user "jovyan"
ENV NB_USER=jovyan
ENV USER=${NB_USER}
RUN adduser --disabled-password \
    --gecos "Default user" \
    ${NB_USER}

# Install jupyterlab and git
USER root
RUN apt-get update && apt-get install -y python3-pip git
RUN pip3 install jupyterlab

# Expose port for jupyterlab
EXPOSE 8888

# Copy repo to the image (optional)
USER ${NB_USER}
ENV REPO_DIR=/home/${NB_USER}/work
RUN mkdir -p ${REPO_DIR}
WORKDIR ${REPO_DIR}
COPY --chown=${NB_USER}:users . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR}
# The entrypoint of the docker image
COPY --chown=${NB_USER}:users binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## Development

### Run and build docker image Locally (Under repo directory)

- To make the current directory writable inside the container:

  ```bash
  chmod -R g+w ./
  ```

- Build and run docker image:

  ```bash
  export GID=$(id -g) && \
  docker compose -f ./binder/docker-compose.yml up --build
  ```

- Open Web browser and go to http://localhost:8888/

- To stop and remove container:

  ```bash
  docker compose -f ./binder/docker-compose.yml down
  ```
