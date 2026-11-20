import sys


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("Astro is built for Windows (it uses the Windows taskbar and window APIs).")

    from astro.app import Astro

    Astro().root.mainloop()
