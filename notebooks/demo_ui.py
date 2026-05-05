import logging
import os
import shutil
import signal
import subprocess
import threading
import warnings

logging.disable(logging.CRITICAL)
os.environ.setdefault("PYTHONWARNINGS", "ignore")
from base64 import b64encode
from json import dumps as json_dumps
from pathlib import Path

import ipywidgets as widgets
from IPython.display import HTML, Markdown, display
import sys

import numpy as np

logging.getLogger("solvers").setLevel(logging.ERROR)
logging.getLogger("polytope").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=r".*cvxopt\.glpk.*")
warnings.filterwarnings("ignore", message=r".*scipy\.optimize\.linprog.*")


ROBOTS = ("pr2", "hsrb", "stretch", "tiago", "g1", "justin")
ACTIONS = ("cut", "mix", "wipe")
ENVIRONMENTS = ("apartment", "kitchen", "isr")
ACTION_DEFAULT_OBJECT_KIND = {
    "cut": "bread",
    "mix": "bowl",
    "wipe": "wipe",
}
VIDEO_FILES = (
    ("PR2 Real", "assets/cuttin_real_pr2.mp4"),
    ("G1 Simulation", "assets/g1_simu.mp4"),
    ("Multiple Robots", "assets/all_robots.mp4"),
)
FAQ_ITEMS = (
    (
        "How do I start the demo?",
        "Choose a robot, action, and environment, then click Start Demo.",
    ),
    (
        "Why do I see multiple items?",
        "When multiple items appear, select a different environment to reset the publisher."
    ),
    (
        "Why does the demo take a moment to appear?",
        "RViz and the underlying demo process need a few seconds to start.",
    ),
    (
        "Why is the camera wrong?",
        "The camera is attached to a link, so you may need to adjust it slightly yourself. When you choose a different environment, it will jump again.",
    ),
)


def _default_object_kind_for_action(action):
    return ACTION_DEFAULT_OBJECT_KIND.get(action, "bread")


CURRENT_DEMO_SELECTION = {}
BACKGROUND_IMAGE_PATH = (
    Path(__file__).resolve().parent.parent.joinpath("img", "ease-background.png")
)
LOGO_IMAGE_PATH = Path(__file__).resolve().parent.parent.joinpath("img", "aicor-logo.png")
RVIZ_CONFIG_DIRECTORY = Path(__file__).resolve().parent / "rviz"
ACTIVE_RVIZ_CONFIG_PATH = Path("/home/jovyan/.rviz2/default.rviz")
SHARED_RVIZ_CONFIG_PATH = RVIZ_CONFIG_DIRECTORY / "shared.rviz"
DEMO_MODULE_SEARCH_PATHS = (
    Path("/home/jovyan/libs/cognitive_robot_abstract_machine/pycram/demos"),
    Path(__file__).resolve().parents[2]
    / "cognitive_robot_abstract_machine"
    / "pycram"
    / "demos",
)

for demo_path in DEMO_MODULE_SEARCH_PATHS:
    if demo_path.is_dir() and str(demo_path) not in sys.path:
        sys.path.insert(0, str(demo_path))


def _rviz_pids():
    result = subprocess.run(
        ["pgrep", "-f", "(^|/)rviz2($| )"], capture_output=True, text=True, check=False
    )
    return [int(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def _is_rviz_running():
    return bool(_rviz_pids())


def _rviz_config_matches(config_path):
    if not ACTIVE_RVIZ_CONFIG_PATH.is_file():
        return False
    return ACTIVE_RVIZ_CONFIG_PATH.read_bytes() == config_path.read_bytes()


def _reload_rviz_for_environment(environment):
    if not SHARED_RVIZ_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Shared RViz config not found: {SHARED_RVIZ_CONFIG_PATH}"
        )

    ACTIVE_RVIZ_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config_matches = _rviz_config_matches(SHARED_RVIZ_CONFIG_PATH)
    if not config_matches:
        shutil.copyfile(SHARED_RVIZ_CONFIG_PATH, ACTIVE_RVIZ_CONFIG_PATH)

    if _is_rviz_running():
        return "preserved"
    return "seeded"


def _style_label(value):
    return value.replace("_", " ").title()


def _demo_pythonpath():
    paths = [str(path) for path in DEMO_MODULE_SEARCH_PATHS if path.is_dir()]
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if current_pythonpath:
        paths.append(current_pythonpath)
    return os.pathsep.join(paths)


def _build_demo_subprocess_command():
    return [
        sys.executable,
        "-u",
        "-c",
        (
            "import json, logging, os, warnings; "
            "logging.disable(logging.CRITICAL); "
            "warnings.filterwarnings('ignore'); "
            "from thesis_single_object import run_single_object_demo; "
            "selection = json.loads(os.environ['DEMO_UI_SELECTION']); "
            "run_single_object_demo("
            "action=selection['action'], "
            "robot_name=selection['robot'], "
            "environment_name=selection['environment'], "
            "object_kind=selection['object_kind'])"
        ),
    ]


def _inject_styles(include_background=True):
    background_image = ""
    if include_background and BACKGROUND_IMAGE_PATH.exists():
        background_image = b64encode(BACKGROUND_IMAGE_PATH.read_bytes()).decode("ascii")
    background_layer = (
        f',\n                    url("data:image/png;base64,{background_image}")'
        if background_image
        else ""
    )

    style_template = """
            <style>
            .demo-shell {
                --demo-ink: #17324d;
                --demo-muted: #64748b;
                --demo-accent: #2f6fa3;
                --demo-accent-soft: #e9f3fb;
                --demo-card: #ffffff;
                --demo-line: #e7edf3;
                --demo-surface: #f7fafc;
                font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
                color: var(--demo-ink);
                position: relative;
                background:
                    linear-gradient(180deg, rgba(251, 253, 255, 0.96) 0%, rgba(244, 248, 251, 0.97) 100%);
                border: 1px solid var(--demo-line);
                border-radius: 24px;
                box-shadow: 0 16px 36px rgba(31, 52, 84, 0.08);
                padding: 30px;
                overflow: hidden;
            }
            .demo-shell::before {
                content: "";
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(247, 250, 252, 0.84) 100%)__BACKGROUND_LAYER__;
                background-position: center top, calc(50% + 240px) -56px;
                background-repeat: no-repeat;
                background-size: auto, 112% auto;
                opacity: 0.72;
                pointer-events: none;
            }
            .demo-shell > * {
                position: relative;
                z-index: 1;
            }
            .demo-shell h1,
            .demo-shell h2,
            .demo-shell h3,
            .demo-shell p {
                margin: 0;
            }
            .demo-hero {
                display: grid;
                gap: 10px;
                margin-bottom: 24px;
                width: min(100%, 520px);
            }
            .demo-logo-wrap {
                display: flex;
                justify-content: center;
                margin-bottom: 22px;
            }
            .demo-logo {
                width: min(100%, 360px);
                height: auto;
                display: block;
                filter: drop-shadow(0 10px 20px rgba(23, 50, 77, 0.12));
            }
            .demo-kicker {
                display: inline-flex;
                width: fit-content;
                padding: 7px 13px;
                border-radius: 999px;
                background: #edf3f8;
                color: #6a7f93;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            .demo-title {
                font-size: 26px;
                font-weight: 700;
                line-height: 1.08;
                letter-spacing: -0.03em;
                max-width: none;
            }
            .demo-copy {
                max-width: 64ch;
                color: var(--demo-muted);
                line-height: 1.55;
                font-size: 15px;
            }
            .demo-card {
                background: var(--demo-card);
                border: 1px solid var(--demo-line);
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 8px 20px rgba(30, 58, 95, 0.04);
            }
            .demo-controls {
                width: min(100%, 560px);
            }
            .demo-scenario-card {
                width: min(100%, 520px);
            }
            .demo-card-title {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 6px;
            }
            .demo-card-copy {
                color: var(--demo-muted);
                font-size: 14px;
                line-height: 1.5;
                margin-bottom: 14px;
            }
            .demo-ui .widget-label {
                color: var(--demo-muted);
                font-size: 13px;
                font-weight: 600;
                min-width: 90px;
            }
            .demo-ui .widget-dropdown select,
            .demo-ui .widget-select select {
                border-radius: 12px;
                border: 1px solid var(--demo-line);
                box-shadow: none;
                background: var(--demo-surface);
                font-size: 14px;
                color: var(--demo-ink);
            }
            .demo-ui .widget-toggle-buttons {
                width: 100%;
            }
            .demo-ui .widget-toggle-buttons .widget-toggle-button {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 999px !important;
                border: 1px solid var(--demo-line) !important;
                margin-right: 8px;
                margin-bottom: 8px;
                background: #f7fafc;
                color: var(--demo-ink);
                font-weight: 600;
                padding: 7px 15px;
                text-align: center !important;
                line-height: 1.2 !important;
                min-height: 40px;
                transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease, border-color 160ms ease;
            }
            .demo-ui .widget-toggle-buttons .widget-toggle-button.mod-active {
                background: linear-gradient(135deg, #2f6fa3 0%, #4d8fc4 100%);
                color: white;
                border-color: transparent !important;
                box-shadow: 0 10px 20px rgba(47, 111, 163, 0.22);
                transform: translateY(-1px);
            }
            .demo-start .widget-button {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: auto;
                min-width: 220px;
                border: 0;
                border-radius: 14px;
                padding: 12px 18px;
                background: linear-gradient(135deg, #c8574f 0%, #dd7463 100%);
                color: white;
                font-weight: 700;
                letter-spacing: 0.01em;
                text-align: center !important;
                line-height: 1.2 !important;
                box-shadow: 0 12px 22px rgba(200, 87, 79, 0.24);
            }
            .demo-summary {
                display: grid;
                gap: 10px;
            }
            .demo-badge-grid {
                display: grid;
                gap: 10px;
            }
            .demo-badge {
                display: grid;
                gap: 4px;
                padding: 12px 14px;
                border-radius: 14px;
                background: var(--demo-surface);
                border: 1px solid var(--demo-line);
            }
            .demo-badge-label {
                color: var(--demo-muted);
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            .demo-badge-value {
                font-size: 18px;
                font-weight: 700;
            }
            .demo-note {
                padding: 12px 14px;
                border-radius: 14px;
                background: var(--demo-accent-soft);
                color: #244f74;
                font-size: 13px;
                line-height: 1.5;
            }
            .demo-running-note {
                margin-top: 14px;
                padding: 16px 18px;
                border-radius: 16px;
                background: linear-gradient(135deg, #fff4df 0%, #ffe8bf 100%);
                border: 1px solid #f1c97a;
                color: #7a4b00;
                font-size: 17px;
                font-weight: 700;
                line-height: 1.4;
            }
            .demo-subtle-list {
                display: grid;
                gap: 10px;
                margin-top: 14px;
            }
            .demo-subtle-row {
                display: grid;
                grid-template-columns: 14px 1fr;
                gap: 10px;
                align-items: start;
                color: var(--demo-muted);
                font-size: 13px;
                line-height: 1.45;
            }
            .demo-subtle-dot {
                width: 10px;
                height: 10px;
                margin-top: 4px;
                border-radius: 999px;
                background: linear-gradient(135deg, #2f6fa3 0%, #4d8fc4 100%);
            }
            .demo-stack {
                display: grid;
                gap: 18px;
                margin-top: 18px;
                width: min(100%, 860px);
            }
            .demo-section-title {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 6px;
            }
            .demo-section-copy {
                color: var(--demo-muted);
                font-size: 14px;
                line-height: 1.5;
                margin-bottom: 14px;
            }
            .demo-video {
                width: 100%;
                border-radius: 16px;
                border: 1px solid var(--demo-line);
                background: #000;
            }
            .demo-faq .widget-accordion {
                border: 1px solid var(--demo-line);
                border-radius: 16px;
                overflow: hidden;
            }
            .demo-faq .widget-accordion .p-Accordion-child {
                border-top: 1px solid var(--demo-line);
            }
            .demo-faq-button .widget-button {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: auto;
                min-width: 240px;
                border: 0;
                border-radius: 14px;
                padding: 12px 18px;
                background: linear-gradient(135deg, #2f6fa3 0%, #4d8fc4 100%);
                color: white;
                font-weight: 700;
                text-align: center !important;
                line-height: 1.2 !important;
                box-shadow: 0 12px 22px rgba(47, 111, 163, 0.24);
            }
            @media (max-width: 900px) {
                .demo-logo {
                    width: min(100%, 280px);
                }
                .demo-title {
                    max-width: none;
                }
            }
            </style>
            """

    display(HTML(style_template.replace("__BACKGROUND_LAYER__", background_layer)))


def _logo_header():
    if not LOGO_IMAGE_PATH.exists():
        return None

    logo_data = b64encode(LOGO_IMAGE_PATH.read_bytes()).decode("ascii")
    return widgets.HTML(
        value=f"""
        <div class="demo-logo-wrap">
          <img
            class="demo-logo"
            src="data:image/png;base64,{logo_data}"
            alt="AICOR"
          />
        </div>
        """
    )


def _selection_summary(selection):
    return f"""
    <div class="demo-summary">
      <div class="demo-badge-grid">
        <div class="demo-badge">
          <div class="demo-badge-label">Robot</div>
          <div class="demo-badge-value">{_style_label(selection['robot'])}</div>
        </div>
        <div class="demo-badge">
          <div class="demo-badge-label">Action</div>
          <div class="demo-badge-value">{_style_label(selection['action'])}</div>
        </div>
        <div class="demo-badge">
          <div class="demo-badge-label">Environment</div>
          <div class="demo-badge-value">{_style_label(selection['environment'])}</div>
        </div>
      </div>
      <div class="demo-note">
        This notebook is the single launch entrypoint. Change the stack here instead of
        relying on Binder URL params.
      </div>
    </div>
    """


def _available_videos():
    base_dir = Path(__file__).resolve().parent
    videos = []
    for title, relative_path in VIDEO_FILES:
        video_path = base_dir / relative_path
        if video_path.is_file():
            videos.append((title, video_path))
    return videos


def _video_card_html(title, video_path):
    video_data = b64encode(video_path.read_bytes()).decode("ascii")
    return f"""
    <div class="demo-card">
      <div class="demo-section-title">{title}</div>
      <div class="demo-section-copy">
        Recorded example run from the notebook assets directory.
      </div>
      <video class="demo-video" controls autoplay muted preload="metadata">
        <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        Your browser does not support the video tag.
      </video>
    </div>
    """


def _faq_section():
    video_entries = _available_videos()

    answers = []
    for _, answer in FAQ_ITEMS:
        answers.append(widgets.HTML(value=f"""
                <div class="demo-section-copy" style="margin: 0; padding: 2px 0 8px 0;">
                  {answer}
                </div>
                """))

    accordion = widgets.Accordion(children=answers, selected_index=None)
    for index, (question, _) in enumerate(FAQ_ITEMS):
        accordion.set_title(index, question)

    video_buttons = []

    if not video_entries:
        video_panel = widgets.HTML(value="""
            <div class="demo-card">
              <div class="demo-section-copy" style="margin-bottom: 0;">
                No recorded demo video was found in the notebook assets directory.
              </div>
            </div>
            """)
    else:
        video_panel = widgets.HTML(value="")

        for title, video_path in video_entries:
            button = widgets.Button(
                description=f"Video: {title}",
                icon="play",
            )
            button.add_class("demo-faq-video-button")

            def _show_video(_, current_title=title, current_video_path=video_path):
                video_panel.value = _video_card_html(current_title, current_video_path)

            button.on_click(_show_video)
            video_buttons.append(button)

    video_button_box = widgets.Box(video_buttons)
    video_button_box.add_class("demo-faq-button")

    wrapper = widgets.VBox(
        [
            widgets.HTML(value="""
                <div class="demo-card">
                  <div class="demo-section-title">FAQ</div>
                  <div class="demo-section-copy">
                    Short answers to common setup issues. Use the buttons below to launch the recorded demos inline.
                  </div>
                </div>
                """),
            video_button_box,
            accordion,
            video_panel,
        ]
    )
    wrapper.add_class("demo-faq")
    return wrapper


def run_info_ui():
    _inject_styles(include_background=False)
    children = [_faq_section()]
    container = widgets.VBox(children, layout=widgets.Layout(width="100%"))
    container.add_class("demo-shell")
    container.add_class("demo-stack")
    display(container)


def run_ui(on_start=None):
    global CURRENT_DEMO_SELECTION

    _inject_styles()

    selection = {
        "robot": ROBOTS[-1],
        "action": ACTIONS[0],
        "environment": ENVIRONMENTS[0],
        "object_kind": _default_object_kind_for_action(ACTIONS[0]),
    }
    CURRENT_DEMO_SELECTION = selection.copy()

    robot = widgets.ToggleButtons(
        options=[(_style_label(value), value) for value in ROBOTS],
        value=selection["robot"],
        description="Robot",
    )

    action = widgets.ToggleButtons(
        options=[(_style_label(value), value) for value in ACTIONS],
        value=selection["action"],
        description="Action",
    )

    environment = widgets.ToggleButtons(
        options=[(_style_label(value), value) for value in ENVIRONMENTS],
        value=selection["environment"],
        description="Env",
    )

    summary = widgets.HTML(value=_selection_summary(selection))
    start_button = widgets.Button(description="Start Demo", icon="play")
    stop_button = widgets.Button(
        description="Stop Demo",
        icon="stop",
        disabled=True,
        button_style="warning",
    )
    running_notice = widgets.HTML(value="")
    output = widgets.Output()
    active_process = {"proc": None}

    start_box = widgets.Box([start_button, stop_button])
    start_box.add_class("demo-start")

    controls = widgets.VBox(
        [
            robot,
            action,
            environment,
            start_box,
            running_notice,
            output,
        ]
    )
    controls.add_class("demo-card")
    controls.add_class("demo-ui")
    controls.add_class("demo-controls")

    CONTROL_KEYS = {
        "Robot": "robot",
        "Action": "action",
        "Env": "environment",
        "Environment": "environment",
    }

    def _update_selection(change):
        global CURRENT_DEMO_SELECTION
        key = CONTROL_KEYS[change["owner"].description]
        selection[key] = change["new"]
        if key == "action":
            selection["object_kind"] = _default_object_kind_for_action(
                selection["action"]
            )
        CURRENT_DEMO_SELECTION = selection.copy()
        summary.value = _selection_summary(selection)

    robot.observe(_update_selection, names="value")
    action.observe(_update_selection, names="value")
    environment.observe(_update_selection, names="value")

    def _default_start(current_selection):
        with output:
            output.clear_output(wait=True)

        _reload_rviz_for_environment(current_selection["environment"])
        env = os.environ.copy()
        env["PYTHONPATH"] = _demo_pythonpath()
        env["DEMO_UI_SELECTION"] = json_dumps(current_selection)
        env["PYTHONWARNINGS"] = "ignore"
        return subprocess.Popen(
            _build_demo_subprocess_command(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )

    def _set_running_state(is_running, message=""):
        start_button.disabled = is_running
        stop_button.disabled = not is_running
        robot.disabled = is_running
        action.disabled = is_running
        environment.disabled = is_running
        running_notice.value = message

    def _cleanup_process(proc, *, was_stopped=None):
        if active_process["proc"] is not proc:
            return
        return_code = proc.wait()
        active_process["proc"] = None
        if was_stopped is None:
            was_stopped = return_code in (-signal.SIGTERM, -signal.SIGKILL)
        if was_stopped:
            message = '<div class="demo-running-note">Demo stopped.</div>'
        elif return_code == 0:
            message = ""
        else:
            message = (
                '<div class="demo-running-note">'
                f"Demo exited with code {return_code}."
                "</div>"
            )
        _set_running_state(False, message)

    def _stream_demo_output(proc):
        try:
            if proc.stdout is not None:
                for line in proc.stdout:
                    output.append_stdout(line)
        finally:
            _cleanup_process(proc)

    def _handle_start(_):
        if active_process["proc"] is not None:
            return
        callback = on_start or _default_start
        _set_running_state(
            True,
            '<div class="demo-running-note">Please be patient. Demo is running. Use Stop Demo to interrupt it.</div>',
        )
        try:
            proc = callback(selection.copy())
        except Exception:
            _set_running_state(False, "")
            raise

        if isinstance(proc, subprocess.Popen):
            active_process["proc"] = proc
            threading.Thread(
                target=_stream_demo_output, args=(proc,), daemon=True
            ).start()
            return

        _set_running_state(False, "")

    def _handle_stop(_):
        proc = active_process["proc"]
        if proc is None or proc.poll() is not None:
            return
        running_notice.value = '<div class="demo-running-note">Stopping demo...</div>'
        os.killpg(proc.pid, signal.SIGTERM)

    start_button.on_click(_handle_start)
    stop_button.on_click(_handle_stop)

    children = []
    logo_header = _logo_header()
    if logo_header is not None:
        children.append(logo_header)
    children.append(controls)
    container = widgets.VBox(children, layout=widgets.Layout(width="100%"))
    container.add_class("demo-shell")
    display(container)


show_demo_ui = run_ui
show_demo_info_ui = run_info_ui
