#!/bin/bash

# Launch the ROS core and web tools when containter starts
source ${HOME}/workspace/ros/devel/setup.bash
roscore &
roslaunch --wait rvizweb rvizweb.launch &

# Add other startup programs here

# The following line will allow the binderhub start Jupyterlab, should be at the end of the entrypoint.
exec "$@"