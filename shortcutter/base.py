import sys
import os
from .exception import ShortcutError, ShortcutNoDesktopError, ShortcutNoMenuError
import traceback


class ShortCutter(object):
    """
    Creates applicaton shortcuts for Windows, MacOS and Linux operating systems.

    To create desktop and menu shortcuts to `python`::

        from shortcut import ShortCutter
        s = ShortCutter()
        s.create_desktop_shortcut("python")
        s.create_menu_shortcut("python")

    Attributes:
    -----------
    raise_errors : bool, default False
        Whether to raise exceptions or skip errors and continue
    error_log : object, default None
        File object where to write errors when raise_errors=False.
        Default is `None` - do not write errors.
        Can also be `sys.stderr` or `io.StringIO()`.
    desktop_folder : str
        Directory used when creating desktop shortcuts
    menu_folder : str
        Directory used when creating menu shortcuts
    bin_folder : str
        `Scripts` or `bin` dir path
        (the one to where setup.py installs if use `ShortCutter()` from setup.py)
        Works (tested) only on Miniconda.
    site_packages : str
        Site packages dir path
        (the one to where setup.py installs if use `ShortCutter()` from setup.py)
        Works (tested) only on Miniconda.
    """

    def __init__(self, raise_errors=False, error_log=None):
        """
        Creates ShortCutter.

        :param bool raise_errors:
            Whether to raise exceptions or skip errors and continue.
        :param error_log:
            File object where to write errors when raise_errors=False.
            Default is `None` - do not write errors.
            Can also be `sys.stderr` or `io.StringIO()`.
        """
        self.raise_errors = raise_errors
        self.error_log = error_log
        self.desktop_folder = self._get_desktop_folder()
        self.menu_folder = self._get_menu_folder()
        self.bin_folder = self._get_bin_folder()
        self.site_packages = self._get_site_packages()
        self._custom_init()

    # might be overridden if needed
    def _custom_init(self):
        pass

    # should be overridden
    @staticmethod
    def _get_desktop_folder():
        raise ShortcutError("_get_desktop_folder needs overriding")

    # should be overridden
    @staticmethod
    def _get_menu_folder():
        raise ShortcutError("_get_menu_folder needs overriding")

    # should be overridden
    @staticmethod
    def _get_bin_folder():
        raise ShortcutError("_get_bin_folder needs overriding")

    # should be overridden
    @staticmethod
    def _get_site_packages():
        raise ShortcutError("_get_site_packages needs overriding")

    # should be overridden
    @staticmethod
    def _executable(app_name):
        raise ShortcutError("_executable needs overriding")

    @classmethod
    def executable(cls, app_name):
        """
        Returns platform independent executable name:

          * app -> app (on Unix)
          * app -> app.exe (on Windows)
        """
        cls._executable(app_name)

    def create_desktop_shortcut(self, target, shortcut_name=None):
        """
        Creates a desktop shortcut to a target.

        :param str target:
            The target to create a shortcut for, it can be a fully qualified
            file path `/path/to/my_program` or a simple application name 
            `my_program`.
        :param str shortcut_name:
            Name of the shortcut without extension (.lnk would be appended if needed).
            If `None` uses the target filename. Defaults to `None`.

        Returns a tuple of (shortcut_name, target_path, shortcut_file_path)
        """
        if not os.path.isdir(self.desktop_folder):
            msg = "Desktop folder '{}' not found.".format(self.desktop_folder)
            if self.raise_errors:
                raise ShortcutNoDesktopError(msg)
            else:
                self.error_log.write(msg + '\n')
        else:
            return self.create_shortcut(target, self.desktop_folder, shortcut_name)

    def create_menu_shortcut(self, target, shortcut_name=None):
        """
        Creates a menu shortcut to a target.

        :param str target:
            The target to create a shortcut for, it can be a fully qualified
            file path `/path/to/my_program` or a simple application name 
            `my_program`.
        :param str shortcut_name:
            Name of the shortcut without extension (.lnk would be appended if needed).
            If `None` uses the target filename. Defaults to `None`.

        Returns a tuple of (shortcut_name, target_path, shortcut_file_path)
        """
        if not os.path.isdir(self.menu_folder):
            msg = "Menu folder '{}' not found.".format(self.menu_folder)
            if self.raise_errors:
                raise ShortcutNoMenuError(msg)
            else:
                self.error_log.write(msg + '\n')
        else:
            return self.create_shortcut(target, self.menu_folder, shortcut_name)

    def create_shortcut(self, target, shortcut_directory, shortcut_name=None):
        """
        Creates a shortcut to a target.

        :param str target:
            The target to create a shortcut for, it can be a fully qualified
            file path `/path/to/my_program` or a simple application name 
            `my_program`.
        :param str shortcut_directory:
            The directory path where the shortcut should be created.
        :param str shortcut_name:
            Name of the shortcut without extension (.lnk would be appended if needed).
            If `None` uses the target filename. Defaults to `None`.

        Returns a tuple of (shortcut_name, target_path, shortcut_file_path)
        """
        # Set the target path:
        target_path = self.find_target(target)

        # Check if target is dir or file:
        isdir = False
        if target_path is not None:
            if os.path.isdir(target_path):
                isdir = True

        # Set shortcut name:
        if shortcut_name is None:
            if isdir:
                shortcut_name = os.path.basename(target)
            else:
                # getting the file name and removing the extension:
                shortcut_name = os.path.splitext(os.path.basename(target))[0]

        # Create shortcut:
        def create():
            if isdir:
                return self._create_shortcut_to_dir(shortcut_name, target_path, shortcut_directory)
            else:
                return self._create_shortcut_file(shortcut_name, target_path, shortcut_directory)

        if self.raise_errors:
            shortcut_file_path = create()
        else:
            # noinspection PyBroadException
            try:
                shortcut_file_path = create()
            except:
                shortcut_file_path = None
                self.error_log.write(''.join(traceback.format_exc()))

        return shortcut_name, target_path, shortcut_file_path

    # should be overridden
    @staticmethod
    def _create_shortcut_to_dir(shortcut_name, target_path, shortcut_directory):
        raise ShortcutError("_create_shortcut_to_dir needs overriding")

    # should be overridden
    @staticmethod
    def _create_shortcut_file(shortcut_name, target_path, shortcut_directory):
        raise ShortcutError("_create_shortcut_file needs overriding")

    def makedirs(self, *args):
        """
        Recursively creates dirs if they don't exist.
        Utilizes self.raise_errors and self.error_log

        :param args:
            Multiple paths (str) for folders to create.

        Returns True on success False of failure
        """
        ret = True
        for path in args:
            if not os.path.isdir(path):
                if self.raise_errors:
                    os.makedirs(path)
                else:
                    try:
                        os.makedirs(path)
                    except OSError:
                        if self.error_log is not None:
                            self.error_log.write(''.join(traceback.format_exc()))
                        ret = False
        return ret

    def find_target(self, target):
        """
        Finds a file path for a target application.

        :param str target:
            The target to find, it can be a fully qualified
            file path `/path/to/my_program` or a simple application name 
            `my_program`.

        Returns a single target file path or `None` if a path can't be found.

        Single-worded targets like `'app'` are always searched in the PATH
        You should append `./app` to tell that the file is in the CWD.
        """
        if os.path.basename(target) == target:
            targets = self.search_for_target(target)
            if len(targets) > 0:
                return targets[0]
            else:
                return None
        elif os.path.isfile(target):
            return os.path.abspath(target)
        else:
            return None

    def search_for_target(self, target):
        """
        Searches for a target application.

        :param str target:
            The target to find.

        Returns a list of potential target file paths, it no paths are found an empty list is returned.
        """
        # potential list of app paths
        target_paths = []

        # create list of potential directories
        paths = self._get_paths()

        # loop through each folder
        for path in paths:
            if os.path.exists(path):
                # is it a directory?
                if os.path.isdir(path):
                    # get files in directory
                    for file_name in os.listdir(path):
                        file_path = os.path.join(path, file_name)
                        if os.path.isfile(file_path):
                            if self._is_file_the_target(target, file_name, file_path):
                                target_paths.append(file_path)
                else:
                    # its not a directory, is it the app we are looking for?
                    pass

        return target_paths

    # needs overriding
    def _is_file_the_target(self, target, file_name, file_path):
        raise ShortcutError("_is_file_the_target needs overriding")

    def _get_paths(self):
        """
        Gets paths from the PATH environment variables.

        Returns a list of paths.
        """
        # get folders from PATH
        paths = os.environ['PATH'].split(os.pathsep)

        return paths
