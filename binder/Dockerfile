# Lightweight Binder image: JupyterLab + VNC Desktop + VSCode Server
# No ROS, no MuJoCo, no heavy dependencies pre-installed.
# Based on bare Ubuntu 24.04 with uv-managed Python.
FROM ubuntu:24.04

LABEL maintainer="IntEL4CoRo" \
      description="Lightweight Binder image with JupyterLab, VNC Desktop, and VSCode Server"

ENV DEBIAN_FRONTEND=noninteractive \
    SHELL=/bin/bash \
    DISPLAY=:1.0

# System dependencies + VNC server + lightweight desktop
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo git curl vim ca-certificates tmux \
    xfce4 xfce4-terminal \
    xubuntu-icon-theme \
    tigervnc-standalone-server \
    dbus-x11 \
     # Disable the automatic screenlock since the account password is unknown
    && apt-get -y -qq remove xfce4-screensaver \
    && rm -rf /var/lib/apt/lists/*

# UV (Python package manager) + Python
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv venv /opt/venv --python 3.12
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
# Make pip/pip3 delegate to uv pip
RUN printf '#!/bin/sh\nexec uv pip "$@"\n' > /usr/local/bin/pip \
    && chmod +x /usr/local/bin/pip \
    && ln -s /usr/local/bin/pip /usr/local/bin/pip3

# code-server (VSCode in browser)
RUN curl -fsSL https://code-server.dev/install.sh | sh
RUN code-server --install-extension ms-python.python \
  && code-server --install-extension ms-toolsai.jupyter

# Tell the Python extension about the uv-managed venv
RUN mkdir -p /root/.local/share/code-server/User \
    && printf '{\n  "python.defaultInterpreterPath": "/opt/venv/bin/python",\n  "python.venvPath": "/opt",\n  "python.venvFolders": ["venv"]\n}\n' \
       > /root/.local/share/code-server/User/settings.json

# JupyterLab + proxy integrations
RUN uv pip install \
    jupyterlab \
    jupyter-server-proxy \
    jupyter-remote-desktop-proxy \
    git+https://github.com/yxzhan/jupyter-code-server.git

# Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash

EXPOSE 8888

ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
WORKDIR ${REPO_DIR}

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install -r /tmp/requirements.txt

COPY . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR}

ENV CODE_WORKING_DIRECTORY=${REPO_DIR}

COPY binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
