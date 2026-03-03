import flet as ft

def main(page: ft.Page):
    print("--- PAGE DIR ---")
    print(dir(page))
    if hasattr(page, 'client_storage'):
        print("Has client_storage")
    elif hasattr(page, 'session'):
        print("Has session")
        print(dir(page.session))
    elif hasattr(page, 'shared_preferences'):
        print("Has shared_preferences")
        print(dir(page.shared_preferences))
    page.window_destroy()

ft.run(main)
