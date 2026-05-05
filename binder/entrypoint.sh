#!/bin/bash

set -e

source "${ROS_PATH}/setup.bash"

if [[ -f /workspace/ros/install/setup.bash ]]; then
    source /workspace/ros/install/setup.bash
fi

log_startup_context() {
    local log_file="/tmp/binder-startup.log"
    {
        echo "=== Binder entrypoint startup context ==="
        echo "date=$(date -Iseconds)"
        echo "pwd=$(pwd)"
        printf 'argv='
        printf '%q ' "$@"
        printf '\n'
        echo "--- selected environment ---"
        env | sort | grep -E '^(BINDER|JUPYTER|JUPYTERHUB|NB|REPO|URL|PATH|QUERY|ROBOT|TASK|ENVIRONMENT)=' || true
        echo "=== end startup context ==="
    } | tee "${log_file}" >&2
}

import_workspace() {
    local workspace_file="${JUPYTER_WORKSPACE_FILE:-/home/repo/new-workspace.jupyterlab-workspace}"

    if [[ ! -f "${workspace_file}" ]]; then
        return
    fi

    jupyter lab workspaces import "${workspace_file}" >/tmp/jupyter-workspace-import.log 2>&1 || \
        echo "Workspace import failed; see /tmp/jupyter-workspace-import.log" >&2
}

update_cognitive_architecture() {
    local repo_dir=""

    for candidate in         "/home/jovyan/libs/cognitive_robot_abstract_machine"         "/root/libs/cognitive_robot_abstract_machine"
    do
        if [[ -d "${candidate}/.git" ]]; then
            repo_dir="${candidate}"
            break
        fi
    done

    if [[ -z "${repo_dir}" ]]; then
        echo "No cognitive_robot_abstract_machine checkout found to update" >&2
        return
    fi

    echo "Updating cognitive_robot_abstract_machine in ${repo_dir}" >&2
    git -C "${repo_dir}" pull --ff-only >/tmp/cognitive-architecture-pull.log 2>&1 ||         echo "cognitive_robot_abstract_machine update failed; see /tmp/cognitive-architecture-pull.log" >&2
}

start_rviz() {
    if [[ "${AUTO_START_RVIZ:-1}" != "1" ]]; then
        return
    fi

    export DISPLAY="${RVIZ_DISPLAY:-${DISPLAY:-:1}}"
    export RVIZ_CONFIG_FILE="${RVIZ_CONFIG_FILE:-/home/jovyan/.rviz2/default.rviz}"
    export LIBGL_ALWAYS_SOFTWARE="${LIBGL_ALWAYS_SOFTWARE:-1}"
    export QT_X11_NO_MITSHM="${QT_X11_NO_MITSHM:-1}"

    fit_rviz_window() {
        local rviz_pid="$1"

        if ! command -v wmctrl >/dev/null 2>&1; then
            return
        fi

        for _ in $(seq 1 30); do
            local window_id
            window_id="$(wmctrl -lp 2>/dev/null | awk -v pid="${rviz_pid}" '$3 == pid {print $1; exit}')"
            if [[ -n "${window_id}" ]]; then
                wmctrl -i -r "${window_id}" -b add,maximized_vert,maximized_horz >/dev/null 2>&1 || true
                wmctrl -i -a "${window_id}" >/dev/null 2>&1 || true
                return
            fi
            sleep 1
        done
    }

    (
        while true; do
            if xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
                echo "Starting RViz on display ${DISPLAY}" >&2
                rviz2 -d "${RVIZ_CONFIG_FILE}" >/tmp/rviz2.log 2>&1 &
                local rviz_pid=$!
                fit_rviz_window "${rviz_pid}" &
                wait "${rviz_pid}"
                sleep 2
                continue
            fi
            echo "Waiting for display ${DISPLAY} before starting RViz" >&2
            sleep 2
        done
    ) &
}

log_startup_context "$@"
update_cognitive_architecture
import_workspace
start_rviz

exec "$@"
