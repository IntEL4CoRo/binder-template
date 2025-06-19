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