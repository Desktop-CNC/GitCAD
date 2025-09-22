from pathlib import Path as path
from GUIMenu import GUIMenu
import Terminal

def handle_github_current_working_directory():
    """
    Gets the current working directory of where local GitHub repositories are found.
    """
    cwd = path.home() / "Documents" / "GitHub"
    cwd.mkdir(parents=True, exist_ok=True)
    return str(cwd)

def handle_repository_menu(cwd: str, menu_title: str, bash_cmds: list, success_msg: str, err_msg: str, terminal_option_name: str=None):
    """
    Handles creating a menu listing local repositories as options.
    param: cwd [str] The GitHub current working directory
    param: menu_title [str] The title of the menu
    param: bash_cmds [list] The list of bash commands to run
    param: success_msg [str] The message to print if bash succeeds
    param: err_msg [str] The message to print if bash fails
    param: terminal_option_name [str] Optional override name to give to the option that exits the menu; by default this is <GO BACK>
    """
    root_dir = path(cwd) # the root of locally cloned repos from the cwd
    local_repo_menu = GUIMenu(title_text=menu_title) # create the menu

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
        def handle_bash_cmd():
            """
            Handles the bash command for for the local repo.
            """
            try: # attempt to run bash with the repo dir
                repo_dir = cwd + "/" + local_repo
                for cmd in bash_cmds:
                    # bash does not yet know which repo and where
                    Terminal.run_bash_cmd(cmd, cwd=repo_dir) # run bash command
                print(f"\n{success_msg}\n")
            except: # handle failed bash command
                input(f"\n{GUIMenu.RED}{err_msg}{GUIMenu.RESET} Press enter to continue.\n")
                GUIMenu.clear_screen()
        # add option to the menu for the cloned repo
        local_repo_menu.add_option(local_repo, handle_bash_cmd)
    
    # add final option to the menu to exit
    local_repo_menu.add_option("<GO BACK>" if terminal_option_name is None else terminal_option_name, handle_go_back)
    # run menu and return its options that were selected
    return local_repo_menu.run() 
   