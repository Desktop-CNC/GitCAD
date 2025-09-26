from pathlib import Path as path
import sys
from GUIMenu import GUIMenu
import Terminal

def handle_repository_dependendencies(cwd: path):
    """
    Gets a list of the immediate dependencies associated with a given repository. Reads from .gitmodules file.
    param: cwd [path] Directory of the parent repository
    """
    try: 
        deps = [] # list of dependencies to collect
        file_dir = str(cwd / path(".gitmodules"))
        with open(file_dir, "r") as file:
            # found the file; read it
            for line in file:
                # find dep / submodule url line
                if line.startswith("	url"):
                    # look at just the dep repo url, look at the repo name and drop .git file type
                    dep = line.split().pop().split("/").pop().replace(".git", "")
                    deps.append(dep) # add dep
        # found all deps; return list 
        return deps
    except FileExistsError as e:
        # file doesn't exist; return empty list
        return []
    except Exception as e:
        # handle all other errors
        return []


def handle_github_current_working_directory():
    """
    Gets the current working directory of where local GitHub repositories are found.
    """
    cwd = path.home() / "Documents" / "GitHub"
    cwd.mkdir(parents=True, exist_ok=True)
    return cwd

def handle_repository_menu(cwd: path, menu_title: str, bash_cmds: list, success_msg: str, err_msg: str, pause_prompt: bool=True, subtitle_text: str=None, ignore_repos: list=None, allow_repos: list=None, auto_close: bool=True):
    """
    Handles creating a menu listing local repositories as options.
    param: cwd [str] The GitHub current working directory
    param: menu_title [str] The title of the menu
    param: bash_cmds [list] The list of bash commands to run
    param: success_msg [str] The message to print if bash succeeds
    param: err_msg [str] The message to print if bash fails
    param: pause_prompt [bool] Optional to indicate if user should be paused and prompted with a status after running the bash commands
    param: subtitle_text [str] Optional subtitle text
    param: ignore_repos [list] Optional list of repos to not show on the menu
    param: allow_repos [list] Optional list of repos allowed in the menu; found repos not in this list are ignored if the list is not None
    """
    root_dir = cwd # the root of locally cloned repos from the cwd
    local_repo_menu = GUIMenu(title_text=menu_title, subtitle_text=subtitle_text, auto_close=auto_close) # create the menu

    def handle_go_back():
        """
        Handles exiting the fetching menu.
        """
        local_repo_menu.exit()

    import time
    # step through the list of locally cloned repos
    for item in root_dir.iterdir():
        # check if repo is in the set of ignored repos; if this set exist and contains the repo it should be ignored
        in_ignored = ignore_repos is not None and ignore_repos.__contains__(item.name)
        # check if repo is in the set of allowed; if the allowed set exists, make sure it is in it
        in_allowed = allow_repos is None or allow_repos.__contains__(item.name)
        # ignore non-dirs, repos to ignore (if any), and ensure they are in the set of allowed if it exsists
        if not (item.is_dir() and not in_ignored and in_allowed):
            continue # skip
        # get the name of a cloned repo
        local_repo = item.name
        repo_dir = cwd / path(local_repo)
        # list of dependencies of the repo option
        repo_deps = handle_repository_dependendencies(cwd=repo_dir)
        row_deps = f"> {Terminal.Text.CYAN}deps: {Terminal.Text.CYAN}{repo_deps}{Terminal.Text.END}" if len(repo_deps) > 0 else ""
        row = f"{local_repo} {row_deps}" 
        def handle_bash_cmd(repo_name=local_repo, repo_dir=repo_dir):
            """
            Handles the bash command for for the local repo.
            """
            margin = " " * GUIMenu.MENU_ORIGIN[0]
            print(f"{margin}{Terminal.Text.BOLD}{Terminal.Text.UNDERLINE}Running commands:{Terminal.Text.RESET}")
            try: # attempt to run bash with the repo dir
                for cmd in bash_cmds:
                    # bash does not yet know which repo and where
                    Terminal.run_bash_cmd(cmd, cwd=repo_dir) # run bash command
                if pause_prompt:
                    input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.GREEN}{success_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            except: # handle failed bash command
                if pause_prompt:
                    input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.RED}{err_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            # exit menu after done with bash
            local_repo_menu.exit()

        # add option to the menu for the cloned repo
        local_repo_menu.add_option(row, handle_bash_cmd)
    
    # add final option to the menu to exit
    local_repo_menu.add_option(f"{Terminal.Text.YELLOW}<GO BACK>{Terminal.Text.END}", handle_go_back)
    # run menu and return last option selected
    return local_repo_menu.run() 
   