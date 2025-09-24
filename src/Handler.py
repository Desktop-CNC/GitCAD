from pathlib import Path as path
import sys
from GUIMenu import GUIMenu
import Terminal

def slash():
    """
    Returns the slash notation of the operating system.
    """
    if sys.platform.startswith("win"):
        return "\\"
    elif sys.platform.startswith("linux"):
        return "/"
    elif sys.platform.startswith("darwin"):
        return "/"
    return None


def handle_github_current_working_directory():
    """
    Gets the current working directory of where local GitHub repositories are found.
    """
    cwd = path.home() / "Documents" / "GitHub"
    cwd.mkdir(parents=True, exist_ok=True)
    return cwd

def handle_repository_menu(cwd: path, menu_title: str, bash_cmds: list, success_msg: str, err_msg: str, pause_prompt: bool=True, subtitle_text: str=None, ignore_repos: list=None):
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
    """
    root_dir = cwd # the root of locally cloned repos from the cwd
    local_repo_menu = GUIMenu(title_text=menu_title, subtitle_text=subtitle_text) # create the menu

    def handle_go_back():
        """
        Handles exiting the fetching menu.
        """
        local_repo_menu.exit()

    # step through the list of locally cloned repos
    for item in root_dir.iterdir():
        if not item.is_dir() or (ignore_repos is not None and ignore_repos.__contains__(item.name)):
            continue # ignore non-dirs or repos we don't want
        # get the name of a cloned repo
        local_repo = item.name
        repo_dir = cwd / path(local_repo)

        def handle_bash_cmd(repo_name=local_repo, repo_dir=repo_dir):
            """
            Handles the bash command for for the local repo.
            """
            margin = " " * GUIMenu.MENU_ORIGIN[0]
            print(f"{margin}{Terminal.Text.BOLD}{Terminal.Text.UNDERLINE}Running commands:{Terminal.Text.RESET}")
            try: # attempt to run bash with the repo dir
                for cmd in bash_cmds:
                    # bash does not yet know which repo and where
                    cmd_output = Terminal.run_bash_cmd(cmd, cwd=repo_dir) # run bash command
                    # get inline command as a string
                    cmd_str = " ".join(cmd_output.args)
                    # print commands printed from the current working directory 
                    print(f"{margin}{Terminal.Text.BOLD}{Terminal.Text.YELLOW}{cwd}{slash()}{Terminal.Text.BLUE}{repo_name}>{Terminal.Text.RESET} {cmd_str}")
                if pause_prompt:
                    input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.GREEN}{success_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            except: # handle failed bash command
                if pause_prompt:
                    input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.RED}{err_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            # exit menu after done with bash
            local_repo_menu.exit()

        # add option to the menu for the cloned repo
        local_repo_menu.add_option(local_repo, handle_bash_cmd)
    
    # add final option to the menu to exit
    local_repo_menu.add_option("<GO BACK>", handle_go_back)
    # run menu and return last option selected
    return local_repo_menu.run() 
   