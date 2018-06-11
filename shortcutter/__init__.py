from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# get operating system
import sys
platform = sys.platform
if sys.platform.startswith("linux"):
    platform = "linux"

# operating system specific imports
if platform == "win32":
    from .windows import ShortCutterWindows as ShortCutter
elif platform == "linux":
    from .linux import ShortCutterLinux as ShortCutter
elif platform == "darwin":
    from .macos import ShortCutterMacOS as ShortCutter
else:
    raise Exception("Error: '{}' platform is not supported.")


def main():
    import traceback
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Automatic shortcut creator." +
                                        " Shortcuts auto-activate their environments by default.")
    parser.add_argument("target", nargs='?', default=None,
                        help="The target executable to create Desktop and Menu shortcuts.")
    parser.add_argument("-d", "--desktop", action="store_true", help="Only create a desktop shortcut.")
    parser.add_argument("-m", "--menu", action="store_true", help="Only create a menu shortcut.")
    parser.add_argument("-n", "--name", nargs='?', default=None, help="Name of the shortcut without extension (autoname otherwise).")
    parser.add_argument("-s", "--simple", action="store_true", help="Create simple shortcut without activate wrapper.")
    parser.add_argument("-t", "--terminal", action="store_true",
                        help="Create shortcut to environment with shortcutter " +
                             "(plus shortcut to root environment in case of conda).")
    args = parser.parse_args()

    create_desktop = args.desktop
    create_menu = args.menu
    activate = not args.simple
    name = args.name if args.name else None

    if not args.target and not args.terminal:
        print('Shortcutter needs target or --terminal arguments to work.')
        return

    # if desktop or menu hasnt been specified create both (i.e. the default)
    if not create_desktop and not create_menu:
        create_desktop = True
        create_menu = True

    shortcutter = ShortCutter(raise_errors=True, activate=activate)

    try:
        target_path = shortcutter.find_target(args.target)
        if target_path or args.terminal:

            desktop_created = False
            if create_desktop:
                try:
                    if args.terminal:
                        shortcutter.create_shortcut_to_env_terminal(name, menu=False)
                    else:
                        shortcutter.create_desktop_shortcut(target_path, name)
                    desktop_created = True
                except Exception:
                    print(''.join(traceback.format_exc()))
                    print("Failed to create desktop shortcut.")

            menu_created = False
            if create_menu:    
                try:
                    if args.terminal:
                        shortcutter.create_shortcut_to_env_terminal(name, desktop=False)
                    else:
                        shortcutter.create_menu_shortcut(target_path, name)
                    menu_created = True
                except Exception:
                    print(''.join(traceback.format_exc()))
                    print("Failed to create menu shortcut.")

            if desktop_created or menu_created:
                print("Shortcut created for '{}'".format(args.target))

        else:
            print("Shortcut creation failed: unable to find '{}'".format(args.target))

    except Exception:
        print(''.join(traceback.format_exc()))
        print("Shortcut creation failed.")
