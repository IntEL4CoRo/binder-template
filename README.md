
# binder-template

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=lab/workspaces/new-workspace)

## Introduction

This is a template repository for creating Virtual Research Labs(VRL) as part of the [EASE Virtual Research Building (VRB)](https://vrb.ease-crc.org/) project.

This template provides a foundation for running robotics research Jupyter Notebooks on Binderhub, enabling researchers to share interactive experiments and demonstrations.

### Launcher Options

Click one of the following links to launch the lab:

| Links | Description |
|--------|-------------|
| [**JupyterLab**](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=lab/workspaces/new-workspace) | Full-featured IDE with notebook editor, terminal, and file browser | [Launch](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=lab/workspaces/new-workspace) |
| [**VSCode**](https://binder.intel4coro.de/v2/gh/IntEL4CoRo/binder-template.git/main?urlpath=vscode) | Browser-based code editor with full VSCode experience |

### Launcher URL Parameters

The launch URL consists of several parts:

```
https://binder.intel4coro.de/v2/gh/{USER}/{REPO}/{BRANCH}?urlpath={INTERFACE}/{PATH}
```

- `{USER}` - GitHub username or organization
- `{REPO}` - Repository name  
- `{BRANCH}` - Branch name (usually `main`), tag or git commit hash (e.g., `27ba27a`)
- `{INTERFACE}` - Interface type: `lab` (JupyterLab) or `vscode`
- `{PATH}` - Path to your notebook file, only applicable when using JupyterLab (e.g., `urlpath=lab/tree/notebooks/mujoco.ipynb`), the `/tree` prefix is required. 
   > Note: With the {PATH}, it only opens the specified file in JupyterLab after the lab starts, it does NOT execute the code automatically.

### Quick Tips

- **JupyterLab** is recommended for notebook development and interactive computing
- **VSCode** is better if you prefer a full-featured code editor with debugging

## Create a new VRB lab from this template

Follow these steps to create your own VRB lab using this template

### Step 1: Create a GitHub Repository

1. Log in to [GitHub](https://github.com/).
2. Navigate to the [binder-template](https://github.com/IntEL4CoRo/binder-template) repository.
3. Click the **Use this template** button (green) to create a new repository.
   - Alternatively, you can **Fork** the repository if you want to sync with future updates.
4. Name your new repository (e.g., `my-robotics-lab`).
5. Set visibility `Public` and click **Create repository**.

### Step 2: Clone Your Repository

You can work with your repository either locally or using GitHub Codespace:

#### Option A: Clone your newly created repository to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/your-repo-name.git
   cd your-repo-name
   ```

#### Option B: GitHub Codespace

1. In your GitHub repository, click the **Code** button (green).
2. Select the **Codespaces** tab.
3. Click **Create codespace on main**.
4. Wait for the codespace to build (first time takes a few minutes).
5. Once ready, you'll have a full VS Code environment in your browser.

### Step 3: Config Your Repository

1. Add your own Jupyter Notebooks, Python code, URDF and other files to the repository, modify the `README.MD`.
1. Modify the [requirements.txt](requirements.txt) to install additional Python packages your project needs:

   ```txt
   # Example:
   numpy
   pandas
   matplotlib
   ```
1. Configure Docker Environment

    If your project requires additional system packages (e.g., FFmpeg, ROS, or other APT packages) or build a ROS2 workspace, modify the [binder/Dockerfile](binder/Dockerfile):

    ```dockerfile
    # Example:
    USER root
    RUN apt update && apt install -y ffmpeg
    RUN mkdir -p ${REPO_DIR}/ros2_ws/src && \
        cd ${REPO_DIR}/ros2_ws/src && \
        git clone --depth=1 https://github.com/ros/ros_tutorials.git && \
        cd ${REPO_DIR}/ros2_ws && \
        rosdep update && apt update && \
        rosdep install --from-paths src -y && \
        colcon build --symlink-install
    ```

#### **Use other base docker image (Advanced)**

The current template uses the following base Docker image: `intel4coro/jupyter-ros2:jazzy-py3.12`

This base image includes:
- **ROS 2 Jazzy** - Robot Operating System 2 (Jazzy distribution)
- **Python 3.12** - Installed via conda
- **JupyterLab** - Notebook environment
- **Conda/Mamba** - Package manager
- **VSCode Server** - Browser-based VSCode
- **VNC Desktop** - Virtual desktop for running linux native graphical applications like MuJoCo viewer, Rviz, Gazebo

It is possible to use use other base images such as your own built docker images, official ROS images, just replace the base image in dockerfile and:

1. **Install JupyterLab**
1. **Expose port 8888**

Example Dockerfile using ROS1 official image:

```dockerfile
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

### Step 4: Commit Your Changes and Push to GitHub

After making changes to your repository, you need to commit and push them to GitHub.

#### Option A: Using Git Commands(Local Development)

1. **Check the status of your changes:**

   ```bash
   git status
   ```

2. **Add the files you want to commit:**

   ```bash
   # Add all changed files
   git add .

   # Or add specific files
   git add notebooks/my-notebook.ipynb
   git add requirements.txt
   ```

3. **Commit your changes with a message:**

   ```bash
   git commit -m "Add MuJoCo robot simulation notebook"
   ```

4. **Push your changes to GitHub:**

   ```bash
   git push origin main
   ```

#### Option B: Using GitHub Codespace

1. Click the **Source Control** icon in the left sidebar (or press `Ctrl+Shift+G`).
2. You will see a list of changed files under "Changes".
3. Click the **+** button next to each file to stage it (or click "Stage All Changes").
4. Enter a commit message in the text box at the top.
5. Click the **Commit** button (checkmark icon).
6. Click **Sync Changes** to push to GitHub.

### Step 5: Build Your Lab on Binder

Once your repository is ready, you can launch it using the URL format described in the [Quick Start](#launcher-url-parameters) section.

**Example:**

```
https://binder.intel4coro.de/v2/gh/my-gihub-username/my-robotics-lab/main?urlpath=lab/tree/notebooks/my-notebook.ipynb
```

> **Note:** The first time you launch, the server will build the Docker image, which may take a while. Subsequent launches will be faster.

**Branch vs Commit Hash vs Tag**

| Reference Type | Example | Behavior |
|----------------|---------|----------|
| Branch name | `main` | Binder checks for updates on every launch. If new commits exist, it rebuilds the image. |
| Commit hash | `27ba27a` | Locks to a specific commit. No rebuilds even if new commits are pushed. |
| Tag | `v1.0` | Locks to a specific tag. Stable release version. |

**When to use each:**

- **Branch name** (e.g., `main`): Use for development. Each launch checks for updates.
- **Commit hash**: Use when you need a stable, reproducible environment. Example: `27ba27a`
- **Tag**: Use for releases. Create a tag: `git tag v1.0 && git push origin v1.0`

### Step 6: Verify Your Lab

If the Docker build succeeds and you can access the JupyterLab interface normally, your VRB Lab is ready and you can start testing your code.

**Troubleshooting:**

- **Build failed**: Check the build error logs and modify `binder/Dockerfile` accordingly
  
  Common build problems and solutions:
   | Issue | Solution |
   |-------|----------|
   | apt install fails | Run `apt update` before `apt install -y` and ensure packages exist in Ubuntu/Debian repositories |
   | Permission denied | Add `USER root` before RUN commands in Dockerfile |
   | fatal: Could not read from remote repository... | Make sure the repository URL you use for `git clone` is HTTPS instead of the SSH/git protocol. The same applies to any submodule URLs defined in `.gitmodules`|
  | returned a non-zero code | It means the bash command failed during execution. Check the full build log with to see the exact error. The actual error message might be hidden further up in the logs, which can make it easy to miss.  |
  | no such file or directory | The directory state is not preserved between two `RUN` instructions. For example, if you `cd` into a directory in the first `RUN`, and execute a script from that directory in the second `RUN`, it will fail. You need to either combine them into a multi-line `bash` command or use the `WORKDIR` instruction. |
  

- **Timeout error**: Refresh the page, and try again.
- **Image builds successfully but fails to start and keep seeing timeout error**: Check if you have added a foreground script in `binder/entrypoint.sh`

## Optimizing Docker Build Time (Advanced)

To reduce build time, it's important to understand the Docker build cache mechanism:

**How Docker Build Cache Works:**

Docker caches each step (instruction) in your Dockerfile. When you rebuild:
- If a step hasn't changed, Docker uses the cached result
- If any step changes, ALL subsequent steps will be re-executed (no cache)

**Key Principle: Order Matters!**

Put time-consuming steps that rarely change near the TOP of your Dockerfile. Put frequently changing steps near the BOTTOM.

Example:

```dockerfile
FROM intel4coro/jupyter-ros2:jazzy-py3.12

# These steps are cached and rarely change - put them FIRST

# This step downloads 2GB assets, better not to rerun it everytime. 
RUN git clone --depth=1 https://github.com/google-deepmind/mujoco_menagerie.git

# This copies your repo - changes often, put it LATER
COPY . ${REPO_DIR}/

# Any step after COPY runs EVERY time - cannot use cache

```

**Why This Matters:**

- `COPY . ${REPO_DIR}/` copies your repository files to the container
- Any step AFTER this line will ALWAYS re-run when you push code changes
- Steps BEFORE this line can use cache if unchanged

**Best Practices:**

1. **Clone large repos first** - Put `git clone` BEFORE `COPY . ${REPO_DIR}/`
2. **Install system packages early** - Put `apt install` commands before the COPY
3. **Install Python packages early** - Put `pip install` before the COPY
4. **Only put repo-specific steps after COPY** - Things that need your latest code

## Local Development

Besides launching on Binder, you can also develop and test your lab locally using Docker. This is useful for debugging and iterative development.

### Prerequisites

Before starting, ensure you have a linux machine with the following installed:

| Tool | Description | Installation |
|------|-------------|--------------|
| **Docker** | Container runtime | [Get Docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | Tool for defining multi-container apps | [Get Docker Compose](https://docs.docker.com/compose/install/) |

> **Note:** Add your user to the `docker` group to run Docker without sudo:
> ```bash
> sudo usermod -aG docker $USER
> ```

### Development Workflow

1. **Navigate to your repository directory:**
   ```bash
   cd /path/to/your-repo
   ```

2. **Build and start the container:**
   ```bash
   docker compose -f ./binder/docker-compose.yml up --build
   ```

   This will:
   - Build the Docker image based on your `binder/Dockerfile`
   - Start a container with JupyterLab, VSCode Server, and VNC
   - Map ports 8888 (JupyterLab)

3. **Access the development environment:**

   | Service | URL | Description |
   |---------|-----|-------------|
   | **JupyterLab** | http://localhost:8888 | Notebook interface |


4. **Edit files locally** using your favorite IDE (VSCode, PyCharm, etc.)

   **Changes are reflected automatically:**
   - If you modify Python files in your repo, changes appear immediately in the container (the repo is mounted as a volume)
   - For Dockerfile changes, you'll need to rebuild: 
      ```
      docker compose -f ./binder/docker-compose.yml down
      docker compose -f ./binder/docker-compose.yml up --build
      ```

   **File Permissions issue**:

   Since the container runs as **root user**, any files created inside the container will be owned by root. This can cause permission issues when you try to edit or delete these files on your host machine.

   **Solution:**

   Change ownership of your project directory:
   ```bash
   sudo chown -R $USER:$USER /path/to/your-repo
   ```

4. **Stop and delete the container:**
   ```bash
   docker compose -f ./binder/docker-compose.yml down
   ```

### Using Host Display

Instead of using the built-in VNC desktop, you can run GUI applications (like MuJoCo viewer) directly on your host machine's display. This provides better performance and a more native experience.

**Setup Steps:**

1. **Allow X11 connections from Docker:**
   ```bash
   # On host machine (Linux)
   xhost +local:docker
   ```

2. **Edit `binder/docker-compose.yml` and uncomment the Host Display section:**

   ```yaml
    # ... existing config ...
    # Use Host Display
      - /tmp/.X11-unix:/tmp/.X11-unix:rw  # X11 socket for GUI apps
    environment:
      - DISPLAY=${DISPLAY}  # Use host display for GUI apps
   ```
 3. Docker compose down and up again.

### GPU Configuration

If you have an NVIDIA GPU, you can configure Docker to use it for accelerated computation (e.g., for MuJoCo, PyTorch, TensorFlow).

Install NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

Edit `binder/docker-compose.yml` and uncomment the GPU section:

```yaml
services:
  binder-template:
    # ... existing config ...
    # GPU support
     - NVIDIA_DRIVER_CAPABILITIES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Then compose down and up:
```bash
docker compose -f ./binder/docker-compose.yml down
docker compose -f ./binder/docker-compose.yml up --build
```

**Verify GPU Access:**

Inside the container terminal, verify GPU is available:
```bash
# Check NVIDIA driver
nvidia-smi
```


### Troubleshooting


| Issue | Solution |
|-------|----------|
| Port already in use | Stop other services using port 8888 or change port mappings in `docker-compose.yml` |
| Permission denied | Run Docker without sudo or fix file permissions |
| Container exits immediately | Check logs: `docker compose logs` |
| Changes not reflected | Ensure volume mount is correct in `docker-compose.yml` |
