LOBBY_PLAY_BTN_PROP = "lobby_play_btn"
CANCEL_MAP_BTN = "cancel_map_btn"
START_MAP_BTN = "start_map_btn"
START_WAVE_BTN = "start_wave_btn"
WAVE_COMPLETED_LABEL = "wave_cmplt_label"
DISCONNECTED_DIALOG_BOX = "disconnected_dialog_box"
DEFEAT_LABEL = "defeat_label"
HP_BAR_ZERO = "hp_zero_bar"

DEFAULT_CONFIG = {
    "waves_per_run": 10,
    f"{LOBBY_PLAY_BTN_PROP}_pos": (160, 497),
    f"{LOBBY_PLAY_BTN_PROP}_color": (32, 242, 235),
    f"{CANCEL_MAP_BTN}_pos": (961, 878),
    f"{CANCEL_MAP_BTN}_color": (238, 0, 0),
    f"{START_MAP_BTN}_pos": (1053, 797),
    f"{START_MAP_BTN}_color": (48, 234, 0),
    f"{START_WAVE_BTN}_pos": (934, 178),
    f"{START_WAVE_BTN}_color": (37, 208, 0),
    f"{WAVE_COMPLETED_LABEL}_pos": (1205, 774),
    f"{WAVE_COMPLETED_LABEL}_color": (95, 255, 71),
    f"{DISCONNECTED_DIALOG_BOX}_pos": (987, 619),
    f"{DISCONNECTED_DIALOG_BOX}_color": (57, 59, 61),
    f"{DEFEAT_LABEL}_pos": (615, 284),
    f"{DEFEAT_LABEL}_color": (222, 0, 0),
    f"{HP_BAR_ZERO}_pos": (603, 67),
    f"{HP_BAR_ZERO}_color": (25, 22, 22),
}


def read_config() -> dict[str, any]:
    try:
        file = open("animeadventures.config", "r+")
        config = {}
        for line in file:
            (prop, value) = line.split("=")
            config[prop] = eval(value)

        return config
    except:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config: dict[str, str]):
    file = open("animeadventures.config", "w+")
    contents = []
    for key, value in config.items():
        contents.append(f"{key}={value}")
    file.write("\n".join(contents))


def is_approximate_color(
    color1: tuple[int, int, int], color2: tuple[int, int, int], difference: int
):
    return (
        abs(color1[0] - color2[0]) <= difference
        and abs(color1[1] - color2[1]) <= difference
        and abs(color1[2] - color2[2]) <= difference
    )