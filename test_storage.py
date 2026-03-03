import flet as ft
import asyncio

async def main(page: ft.Page):
    with open("inspection.txt", "w") as f:
        f.write("--- PAGE INSPECTION ---\n")
        f.write(f"Version: {ft.__version__}\n")
        f.write(f"client_storage exists: {hasattr(page, 'client_storage')}\n")
        
        try:
            storage = ft.SharedPreferences()
            page.overlay.append(storage)
            page.update()
            f.write("SharedPreferences appended to overlay\n")
        except Exception as e:
            f.write(f"Error creating SharedPreferences: {e}\n")

        f.write("\n--- PAGE DIRECTORY ---\n")
        f.write("\n".join(dir(page)))
        
    await asyncio.sleep(1)
    await page.window.destroy()

ft.run(main)
