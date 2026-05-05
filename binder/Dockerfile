# Dockerfile of the base image: https://github.com/IntEL4CoRo/jupyter-ros2/blob/main/Dockerfile
FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root
#============= Install extra software packages =============#
# RUN apt update && apt install -y curl
RUN apt update && apt install -y --no-install-recommends     graphviz     libgraphviz-dev     pkg-config     python3-dev     build-essential &&     rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt
#===========================================================#
# ------------------------------------------------------------
# Required
# ------------------------------------------------------------
USER root
RUN apt update && apt install -y --no-install-recommends \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-hardware-interface \
    ros-jazzy-controller-manager \
    ros-jazzy-control-msgs \
    ros-jazzy-xacro \
    ros-jazzy-rqt-joint-trajectory-controller \
    python3-vcstool \
    nodejs \
    npm \
    wmctrl && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Install demo repository and cram code
# ------------------------------------------------------------

RUN python3 -m pip install poetry
RUN set -ex && \
    poetry config virtualenvs.create false && \
    mkdir -p ${HOME}/libs && cd ${HOME}/libs && \
    git clone --branch vrb-action-cores --single-branch https://github.com/sunava/cognitive_robot_abstract_machine.git && \
    cd cognitive_robot_abstract_machine && \
    git pull && \
    git clone https://github.com/sunava/pycram_object_gap_demo.git pycram/resources/pycram_object_gap_demo && \
    sed -i '/^[[:space:]]*random_events[[:space:]]*=.*$/d' pyproject.toml && \
    poetry install && \
    mkdir -p /workspace/ros/src && \
    cd /workspace/ros/src && \
    git clone -b ros-jazzy --single-branch https://github.com/code-iai/iai_maps.git && \
    git clone -b ros-jazzy-main --single-branch https://github.com/code-iai/iai_pr2.git && \
    git clone -b ros-jazzy --single-branch https://github.com/code-iai/iai_robots.git && \
    git clone -b ros2-jazzy --single-branch https://github.com/code-iai/iai_stretch.git && \
    git clone -b ros2-jazzy --single-branch https://github.com/code-iai/hsr_description.git && \
    git clone -b ros2-main --single-branch https://github.com/code-iai/iai_tiago_description.git && \
    git clone -b ros2-master --single-branch https://github.com/realsenseai/realsense-ros.git && \
    git clone -b jazzy --single-branch https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git && \
    git clone https://github.com/maltehue/ros2_robotiq_gripper.git && \
    rm -rf ros2_robotiq_gripper/robotiq_driver \
           ros2_robotiq_gripper/robotiq_drivers \
           ros2_robotiq_gripper/robotiq_controllers \
           ros2_robotiq_gripper/robotiq_hardware_tests  \
           realsense-ros/realsense2_ros_mqtt_bridge  \
           realsense-ros/realsense2_rgbd_plugin  \
           realsense-ros/realsense2_camera_msgs \
           realsense-ros/realsense2_camera && \
    find /workspace/ros/src -type f -name package.xml -path '*/robotiq_driver/package.xml' -execdir touch COLCON_IGNORE \; && \
    git clone https://github.com/sunava/isr_testbed.git && \
    git clone https://github.com/ipa320/cob_simulation.git && \
    cd /workspace/ros && \
    . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build --symlink-install \
      --packages-skip cob_gazebo_tools cob_gazebo_objects cob_gazebo_worlds cob_gazebo cob_bringup_sim cob_simulation && \
    echo "source /workspace/ros/install/setup.bash" >> /root/.bashrc

# ------------------------------------------------------------
# ROS2 workspace: giskardpy_ros (clone, deps, build)
# ------------------------------------------------------------
RUN pip install xacro

ARG ROS_DISTRO=jazzy
ENV ROS_DISTRO=${ROS_DISTRO}


RUN pip install "setuptools<81"

USER root
# Copy content to the image
ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
COPY . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR}

# Set JupyterLab default directory
WORKDIR ${REPO_DIR}

# Set VSCODE default directory
ENV CODE_WORKING_DIRECTORY=${REPO_DIR}

# Copy RViz config
COPY default.rviz /home/jovyan/.rviz2/default.rviz
RUN mkdir -p /home/jovyan/.ipython/profile_default/startup /root/.ipython/profile_default/startup
RUN cd ${REPO_DIR}/binder/desktop-widget && \
    npm install && \
    npm run build && \
    jupyter labextension install . --no-build && \
    jupyter lab build --minimize=False

# The entrypoint of the docker image
COPY binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
