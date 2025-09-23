from pathlib import Path as path
from GUIMenu import GUIMenu
import Terminal
import copy

def handle_github_current_working_directory():
    """
    Gets the current working directory of where local GitHub repositories are found.
    """
    cwd = path.home() / "Documents" / "GitHub"
    cwd.mkdir(parents=True, exist_ok=True)
    return str(cwd)

def handle_repository_menu(cwd: str, menu_title: str, bash_cmds: list, success_msg: str, err_msg: str, subtitle_text: str=None):
    """
    Handles creating a menu listing local repositories as options.
    param: cwd [str] The GitHub current working directory
    param: menu_title [str] The title of the menu
    param: bash_cmds [list] The list of bash commands to run
    param: success_msg [str] The message to print if bash succeeds
    param: err_msg [str] The message to print if bash fails
    param: subtitle_text [str] Optional subtitle text
    """
    root_dir = path(cwd) # the root of locally cloned repos from the cwd
    local_repo_menu = GUIMenu(title_text=menu_title, subtitle_text=subtitle_text) # create the menu

    def handle_go_back():
        """
        Handles exiting the fetching menu.
        """
        local_repo_menu.exit()

    # step through the list of locally cloned repos
    for item in root_dir.iterdir():
        if not item.is_dir():
            continue # ignore what's in the root dir that isn't a dir
        # get the name of a cloned repo
        local_repo = item.name
        repo_dir = cwd / path(local_repo)

        def handle_bash_cmd(repo_dir=repo_dir):
            """
            Handles the bash command for for the local repo.
            """
            try: # attempt to run bash with the repo dir
                for cmd in bash_cmds:
                    # bash does not yet know which repo and where
                    Terminal.run_bash_cmd(cmd, cwd=repo_dir) # run bash command
                input(f"\n{Terminal.Text.GREEN}{success_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            except: # handle failed bash command
                input(f"\n{Terminal.Text.RED}{err_msg}{Terminal.Text.RESET} Press enter to continue.\n")
            # exit menu after done with bash
            local_repo_menu.exit()

        # add option to the menu for the cloned repo
        local_repo_menu.add_option(local_repo, handle_bash_cmd)
    
    # add final option to the menu to exit
    local_repo_menu.add_option("<GO BACK>", handle_go_back)
    # run menu and return its options that were selected
    return local_repo_menu.run() 
   