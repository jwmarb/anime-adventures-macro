import threading
import utils
import pyautogui
import keyboard
import pynput
import time
import os
import win32gui
import win32con
from typing import Callable
from configurator import is_focused


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


runs: list[float] = []
losses = 0
disconnections = 0
UPDATE_RATE = 1 / 3


def run_macro(path: str, autofocus: bool = True):
    if autofocus:
        roblox = win32gui.FindWindow(None, "Roblox")
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(roblox)

    os.system(path)


def get_min_max_run() -> tuple[float, int, float, int]:
    if len(runs) == 0:
        return (0.0, -1, 0.0, -1)
    l_run, h_run, l_idx, h_idx = runs[0], runs[0], 0, 0
    for i in range(1, len(runs)):
        if h_run < runs[i]:
            h_run = runs[i]
            h_idx = i
        if l_run > runs[i]:
            l_run = runs[i]
            l_idx = i

    return (h_run, h_idx, l_run, l_idx)


def timer(
    should_stop: Callable[[], bool],
    start_time: Callable[[], float],
    avg_run_time: Callable[[], float],
    run_till_start_of_wave: Callable[[], int],
    logs: Callable[[], list[str]],
):
    while not should_stop():
        now = time.perf_counter()
        log = [
            *catalog(now, start_time(), avg_run_time(), run_till_start_of_wave()),
            "",
            "To stop farming for gems, press BACKSPACE on your keyboard",
            "",
            *logs(),
        ]
        print("\n".join(log))
        time.sleep(UPDATE_RATE)
        os.system("cls")


def catalog(
    now: float, start_time: float, avg_run_time: float, run_till_start_of_wave: int
):
    highest_run_time, h_idx, lowest_run_time, l_idx = get_min_max_run()
    return (
        "\t\t[RUNS INFO]",
        f"\tTotal # of runs completed: {len(runs)}",
        f"\tTime elapsed: {utils.to_human_time(now - start_time)}",
        f"\tAverage run time: {utils.to_human_time(avg_run_time//len(runs)) if len(runs) > 0 else 'N/A'}",
        f"\tSlowest run time: {f'{utils.to_human_time(highest_run_time)} (Achieved at run #{h_idx + 1})' if highest_run_time != 0 else 'N/A'}",
        f"\tFastest run time: {f'{utils.to_human_time(lowest_run_time)} (Achieved at run #{l_idx + 1})' if lowest_run_time != 0 else 'N/A'}",
        "",
        "\t\t[GAME STATS]",
        f"\tWaves per run: {run_till_start_of_wave - 1}",
        f"\tGames lost: {losses}",
        f"\tGames won: {len(runs) - losses}",
        f"\tWin rate: {f'{((len(runs)-losses)/len(runs))*100}%' if len(runs) > 0 else 'N/A'}",
        f"\t# of disconnections: {disconnections}",
    )


def main():
    global runs
    global losses
    global disconnections
    runs.clear()
    losses = 0
    disconnections = 0
    # Tracking variables
    start_time = time.perf_counter()

    # Controller
    kb_controller = pynput.keyboard.Controller()

    run_till_start_of_wave = 10
    config = utils.read_config()
    run_till_start_of_wave = config["waves_per_run"] + 1
    avg_run_time: int = 0
    should_stop_timer = False
    logs: list[str] = []

    t1 = threading.Thread(
        target=timer,
        args=(
            lambda: should_stop_timer,
            lambda: start_time,
            lambda: avg_run_time,
            lambda: run_till_start_of_wave,
            lambda: logs,
        ),
    )
    t1.start()

    def execute_run(skip_joining_private_server: bool):
        global runs
        nonlocal avg_run_time
        nonlocal logs
        config = utils.read_config()

        while True:
            now = time.perf_counter()
            logs.clear()
            # print("\tLaunching roblox...")
            # Auto-start anime adventures private server
            if not skip_joining_private_server:
                run_macro("%CD%/bin/joinprivateserver.exe", autofocus=False)

            is_opened = False
            while not is_opened:
                detect_stop()
                top_windows = []
                win32gui.EnumWindows(windowEnumerationHandler, top_windows)
                for process in top_windows:
                    HWND = process[0]
                    if process[1] == "Roblox":
                        is_opened = True
                        logs.append("\tDetected Roblox application")
                        win32gui.ShowWindow(HWND, win32con.SW_RESTORE)
                        win32gui.SetWindowPos(
                            HWND,
                            win32con.HWND_NOTOPMOST,
                            0,
                            0,
                            0,
                            0,
                            win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                        )
                        win32gui.SetWindowPos(
                            HWND,
                            win32con.HWND_TOPMOST,
                            0,
                            0,
                            0,
                            0,
                            win32con.SWP_NOMOVE + win32con.SWP_NOSIZE,
                        )
                        win32gui.SetWindowPos(
                            HWND,
                            win32con.HWND_NOTOPMOST,
                            0,
                            0,
                            0,
                            0,
                            win32con.SWP_SHOWWINDOW
                            + win32con.SWP_NOMOVE
                            + win32con.SWP_NOSIZE,
                        )
                        break
            while True:
                detect_stop()
                color = pyautogui.pixel(
                    config[f"{utils.LOBBY_PLAY_BTN_PROP}_pos"][0],
                    config[f"{utils.LOBBY_PLAY_BTN_PROP}_pos"][1],
                )
                if color == config[f"{utils.LOBBY_PLAY_BTN_PROP}_color"]:
                    logs.append("\tSuccessfully loaded in-game")
                    run_macro("%CD%/bin/lobbyclickplay.exe")
                    # pyautogui.moveTo(x=153, y=479, duration=DELAY)
                    # pyautogui.click(clicks=2, interval=DELAY)
                    break

            start = time.perf_counter()
            kb_controller.press("d")
            kb_controller.press("w")
            kb_controller.press(pynput.keyboard.Key.shift_l)
            while True:
                listeners()
                if time.perf_counter() - start > 1.75:
                    kb_controller.release("d")
                    kb_controller.release(pynput.keyboard.Key.shift_l)
                    break

            start = time.perf_counter()
            while True:
                kb_controller.release("d")
                kb_controller.press("a")
                time.sleep(0.01)
                kb_controller.release("a")
                kb_controller.press("d")
                time.sleep(0.01)
                if time.perf_counter() - start > 0.5:
                    kb_controller.release("w")
                    kb_controller.release("a")
                    kb_controller.release("d")
                    break

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.CANCEL_MAP_BTN}_pos"][0],
                    config[f"{utils.CANCEL_MAP_BTN}_pos"][1],
                )
                if color == config[f"{utils.CANCEL_MAP_BTN}_color"]:
                    run_macro("%CD%/bin/selectmarineford.exe")
                    break

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.START_MAP_BTN}_pos"][0],
                    config[f"{utils.START_MAP_BTN}_pos"][1],
                )
                if color == config[f"{utils.START_MAP_BTN}_color"]:
                    run_macro("%CD%/bin/startmarineford.exe")
                    break

            is_normal_camera_angle = False
            macro_parent_folder = ""

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.START_WAVE_BTN}_pos"][0],
                    config[f"{utils.START_WAVE_BTN}_pos"][1],
                )
                if color == config[f"{utils.START_WAVE_BTN}_color"]:
                    color2 = pyautogui.pixel(
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_pos"][0],
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_pos"][1],
                    )
                    is_normal_camera_angle = utils.is_approximate_color(
                        config[f"{utils.NORMAL_CAMERA_ANGLE_INDICATOR}_color"],
                        color2,
                        20,
                    )
                    if is_normal_camera_angle:
                        logs.append("\tUsing NORMAL camera angle macros!")
                        macro_parent_folder = "normal"
                    else:
                        logs.append("\tUsing BIRD-EYE camera angle macros!")
                        macro_parent_folder = "birdeye"
                    run_macro("%CD%/bin/clickwavestart.exe")
                    break

            # Listen for wave completions
            wave = 1
            files = os.listdir(f"./wave_events/{macro_parent_folder}")

            while True:
                listeners()
                color = pyautogui.pixel(
                    config[f"{utils.WAVE_COMPLETED_LABEL}_pos"][0],
                    config[f"{utils.WAVE_COMPLETED_LABEL}_pos"][1],
                )
                if color == config[f"{utils.WAVE_COMPLETED_LABEL}_color"]:
                    logs.append(f"\tWave {wave} completed")
                    if "every_wave_completed.exe" in files:
                        run_macro(
                            f"%CD%/wave_events/{macro_parent_folder}/every_wave_completed.exe"
                        )
                    wave += 1

                    if wave == run_till_start_of_wave:
                        end_time = time.perf_counter() - now
                        runs.append(end_time)
                        avg_run_time += end_time
                        run_macro("%CD%/bin/closegame.exe", autofocus=False)
                        skip_joining_private_server = False
                        break

                    if str(wave) in files:
                        wave_actions = os.listdir(
                            f"wave_events/{macro_parent_folder}/{wave}"
                        )
                        for action in wave_actions:
                            run_macro(
                                f"%CD%/wave_events/{macro_parent_folder}/{wave}/{action}"
                            )
                    else:
                        logs.append(
                            f"\t- No action found for wave {wave}. Waiting till the end of wave {wave}..."
                        )

                    s = time.perf_counter()
                    while time.perf_counter() - s <= 5:
                        detect_stop()

    def detect_stop():
        nonlocal should_stop_timer
        if keyboard.is_pressed("backspace"):
            should_stop_timer = True
            time.sleep(UPDATE_RATE)
            now = time.perf_counter()
            os.system("cls")
            results = [
                *catalog(now, start_time, avg_run_time, run_till_start_of_wave),
                "",
                "Press ESCAPE to exit",
                "Press SHIFT to restart the program",
            ]
            print("\n".join(results))
            while True:
                if is_focused():
                    if keyboard.is_pressed("escape"):
                        os._exit(0)
                    if keyboard.is_pressed("shift"):
                        main()

    def detect_disconnection():
        global disconnections
        nonlocal logs
        color = pyautogui.pixel(
            config[f"{utils.DISCONNECTED_DIALOG_BOX}_pos"][0],
            config[f"{utils.DISCONNECTED_DIALOG_BOX}_pos"][1],
        )
        roblox = win32gui.FindWindow(None, "Roblox")
        if roblox:
            tup = win32gui.GetWindowPlacement(roblox)
            if (
                color == config[f"{utils.DISCONNECTED_DIALOG_BOX}_color"]
                and tup[1] == win32con.SW_SHOWMAXIMIZED
            ):
                disconnections += 1
                logs.append(
                    "\tDetected user has been disconnected. Attempting to reconnect..."
                )
                os.system("%CD%/bin/closegame.exe")
                while True:
                    if keyboard.is_pressed("backspace"):
                        raise Exception()
                    os.system("%CD%/bin/joinprivateserver.exe")
                    start = time.perf_counter()
                    while time.perf_counter() - start <= 1:
                        if keyboard.is_pressed("backspace"):
                            raise Exception()
                    if pyautogui.pixel(x=953, y=482) == (255, 255, 255):
                        break
                    start = time.perf_counter()
                    while time.perf_counter() - start <= 0.1:
                        if keyboard.is_pressed("backspace"):
                            raise Exception()

                    pyautogui.click(x=943, y=602)  # OK button
                execute_run(True)

    def detect_loss():
        global runs
        global losses
        nonlocal avg_run_time
        nonlocal logs
        color1 = pyautogui.pixel(
            config[f"{utils.DEFEAT_LABEL}_pos"][0],
            config[f"{utils.DEFEAT_LABEL}_pos"][1],
        )
        color2 = pyautogui.pixel(
            config[f"{utils.HP_BAR_ZERO}_pos"][0], config[f"{utils.HP_BAR_ZERO}_pos"][1]
        )
        if (
            color1 == config[f"{utils.DEFEAT_LABEL}_color"]
            and color2 == config[f"{utils.HP_BAR_ZERO}_color"]
        ):
            end_time = time.perf_counter()
            logs.append("\tLoss detected. Redoing run...")
            runs.append(end_time)
            avg_run_time += end_time
            losses += 1
            os.system('"%CD%/bin/closegame.exe"')
            execute_run(False)

    def listeners():
        detect_stop()
        detect_disconnection()
        detect_loss()

    execute_run(False)


if __name__ == "__main__":
    main()
