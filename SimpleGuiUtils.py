import PySimpleGUI as sg


def checkbox(display: str, key: str):
    return sg.Checkbox(display, key=key, enable_events=True, default=True, size=18)
