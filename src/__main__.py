from GUIMenu import GUIMenu
from pathlib import Path as path
import Terminal
import Handler
import subprocess
import threading
import time
import sys
import os

def handle_clone_repository(cwd: path):
    """
    Handles cloning an online GitHub repository for the main menu.
    param: cwd [str] The repository current working directory
    """
    # prompt the repo cloning
    margin = " " * GUIMenu.MENU_ORIGIN[0]
    print(f"\n{margin}Lets {Terminal.Text.YELLOW}clone{Terminal.Text.END} from GitHub.\n")
    # get online GitHub repo URL
    repo_url = input(f"{margin}{Terminal.Text.BOLD}{Terminal.Text.GREEN}Please input the GitHub Repository URL: {Terminal.Text.RESET}")
    
    try: # attempt to clone
        Terminal.run_bash_cmd(["git", "clone", "--recursive", repo_url], cwd=str(cwd))
        # import submodule/dependencies with cloned repo
        repo_name = repo_url.split(sep="/").pop().replace(".git", "")
        repo_dir = cwd / path(repo_name) # repo directory after cloning
        Terminal.run_bash_cmd(["git", "submodule", "update", "--init", "--recursive"], cwd=str(repo_dir))
        input(f"\n{Terminal.Text.BOLD}{Terminal.Text.GREEN}Repository successfully cloned.{Terminal.Text.RESET} Press enter to continue.")
    except: # handle failed cloning
        input(f"\n{Terminal.Text.BOLD}{Terminal.Text.RED}Failed to clone the repository.{Terminal.Text.RESET} Press enter to continue.")
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_pull_repository(cwd: path):
    """
    Handles pulling an online GitHub repository to update the locally cloned one. This handler is for the main menu. 
    param: cwd [str] The GitHub current working directory
    """
    Handler.handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos.",
        subtitle_text=f"Select the one you want to {Terminal.Text.YELLOW}pull changes{Terminal.Text.CYAN} from GitHub for.", 
        bash_cmds=[
            # stash (keep) local changes and pull from github
            ["git", "stash"],
            ["git", "fetch", "origin"],
            ["git", "reset", "--hard", "origin/main"],
            ["git", "submodule", "update", "--init", "--recursive"]],
        success_msg="Successfully pulled the repository.",
        err_msg="Failed to pull the repository."
    )
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_push_repository(cwd: path):
    """
    Handles pushing a local repository back to GitHub. This is for the main menu.
    param: cwd [str] The GitHub current working directory
    """
    margin = " " * GUIMenu.MENU_ORIGIN[0]
    # get the repo from the menu
    local_repo = Handler.handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos.",
        subtitle_text=f"Select the one you want to {Terminal.Text.YELLOW}push changes{Terminal.Text.CYAN} back to GitHub for.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        pause_prompt=False,
        auto_close=False
    )   
    # check if the menu was exited
    if local_repo.__contains__('<') and local_repo.__contains__('>'):
        # clear the screen once done with menu
        Terminal.Screen.clear_screen()
        return
    # get commit message to push
    commit_message = input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.BLUE}What changes were made? {Terminal.Text.CYAN}Press enter when done, but type here: {Terminal.Text.RESET}")
    margin = " " * GUIMenu.MENU_ORIGIN[0]
    # try to push
    try:
        Terminal.run_bash_cmd(["git", "add", "."], cwd=cwd / path(local_repo))
        Terminal.run_bash_cmd(["git", "commit", "-m", commit_message], cwd=cwd / path(local_repo))
        Terminal.run_bash_cmd(["git", "push"], cwd=cwd / path(local_repo))
        input(f"\n{margin}{Terminal.Text.GREEN}Successfully pushed the repository to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except:
        input(f"\n{margin}{Terminal.Text.RED}Did not push changes. It's possible there are no changes to push.{Terminal.Text.RESET} Press enter to continue.\n")
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_create_dependency(cwd: path):
    """
    Create a new dependency between a repository and a parent repository. 
    param: cwd [str] The GitHub current working directory
    """
    # get the parent repo from a menu
    parent_repo = Handler.handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repos.",
        subtitle_text=f"Select the one you want to {Terminal.Text.YELLOW}create{Terminal.Text.CYAN} a {Terminal.Text.YELLOW}dependency{Terminal.Text.CYAN} for.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        pause_prompt=False,
        auto_close=False
    )
    # check if the menu was exited
    if parent_repo.__contains__('<') and parent_repo.__contains__('>'):
        Terminal.Screen.clear_screen()
        return
    # repos that are already dependencies of the parent; ignore them below
    current_repo_deps = Handler.handle_repository_dependendencies(cwd=cwd / path(parent_repo))
    ignore_repos = current_repo_deps # repos to ignore
    ignore_repos.append(parent_repo)
    # get the dependency repo from another menu
    dep_repo = Handler.handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repos.",
        subtitle_text=f"Select the {Terminal.Text.YELLOW}dependency{Terminal.Text.CYAN} to add to {Terminal.Text.YELLOW}{parent_repo}{Terminal.Text.CYAN}.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        pause_prompt=False,
        auto_close=False,
        ignore_repos=ignore_repos
    )
    # check if the menu was exited
    if dep_repo.__contains__('<') and dep_repo.__contains__('>'):
        handle_create_dependency(cwd=cwd) # restart the whole process
        Terminal.Screen.clear_screen()
        return # exit upon completion

    margin = " " * GUIMenu.MENU_ORIGIN[0]
    try:
        # get repo directories 
        parent_repo_dir = cwd / path(parent_repo)
        dep_repo_dir = cwd / path(dep_repo)
        # get dependency repo url from bash
        dep_repo_ssh_url = Terminal.run_bash_cmd(["git", "remote", "get-url", "origin"], cwd=str(dep_repo_dir)).stdout.strip()

        # add dependency repo by its url and push parent repo to github
        Terminal.run_bash_cmd(["git", "submodule", "add", dep_repo_ssh_url, f"{path('dep') / path(dep_repo)}"], cwd=str(parent_repo_dir))
        Terminal.run_bash_cmd(["git", "commit", "-am", f"Created {dep_repo} as a submodule/dependency to {parent_repo}"], cwd=str(parent_repo_dir))
        Terminal.run_bash_cmd(["git", "push"], cwd=str(parent_repo_dir))
        input(f"\n{margin}{Terminal.Text.GREEN}Successfully created dependency and pushed it to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except:
        input(f"\n{margin}{Terminal.Text.RED}Failed to create dependency. It may already exist, or a chosen repository does not.{Terminal.Text.RESET} Press enter to continue.\n")
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_delete_dependency(cwd: path):
    """
    Removes a dependency from a repository.
    param: cwd [str] The GitHub current working directory
    """
    # get parent from repo menu
    parent_repo = Handler.handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repos.",
        subtitle_text=f"Select which to {Terminal.Text.YELLOW}delete{Terminal.Text.CYAN} a {Terminal.Text.YELLOW}dependency{Terminal.Text.CYAN} from.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        pause_prompt=False,
        auto_close=False
    )
    # check if the menu was exited
    if parent_repo.__contains__('<') and parent_repo.__contains__('>'):
        Terminal.Screen.clear_screen()
        return
    # get repos allowed to be deleted (deps of the parent)
    allowed_repos = Handler.handle_repository_dependendencies(cwd=cwd / path(parent_repo))
    # get dependency repo from another menu
    dep_repo = Handler.handle_repository_menu(
        cwd=cwd, 
        menu_title=f"Here are your local repos that are {Terminal.Text.YELLOW}dependencies{Terminal.Text.BLUE} for {Terminal.Text.YELLOW}{parent_repo}{Terminal.Text.BLUE}.", 
        subtitle_text="Select the dependency to delete.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        pause_prompt=False,
        auto_close=False,
        allow_repos=allowed_repos
    )

    # check if the menu was exited
    if dep_repo.__contains__('<') and dep_repo.__contains__('>'):
        handle_delete_dependency(cwd=cwd) # restart the whole process
        Terminal.Screen.clear_screen()
        return # exit upon completion

    margin = " " * GUIMenu.MENU_ORIGIN[0]
    try:
        # get parent repo directory 
        parent_repo_dir = cwd / path(parent_repo)
        # run dependency removal bash
        # remove submodule tracking
        Terminal.run_bash_cmd(["git", "submodule", "deinit", "-f", f"{path('dep') / path(dep_repo)}"], cwd=str(parent_repo_dir))
        Terminal.run_bash_cmd(["git", "rm", "-f", f"{path('dep') / path(dep_repo)}"], cwd=str(parent_repo_dir))
    
        # get args based on os
        args = (None, None, None)
        if sys.platform.startswith("win"):
            args = ("rmdir", "/s", "/q")
        elif sys.platform.startswith("linux"):
            args = ("rm", "-rf", " ")
        elif sys.platform.startswith("darwin"):
            args = ("rm", "-rf", " ")
        # clean up metadata left over
        Terminal.run_bash_cmd([args[0], args[1], args[2], f"{path('.git') / path('modules') / path('dep') / path(dep_repo)}"], cwd=str(parent_repo_dir))
        Terminal.run_bash_cmd([args[0], args[1], args[2], f"{path('dep') / path(dep_repo)}"], cwd=str(parent_repo_dir))
       
        # commit and push changes of removed dependency
        Terminal.run_bash_cmd(["git", "commit", "-m", f"Deleted submodule/dependency {dep_repo} from {parent_repo}"], cwd=str(parent_repo_dir))
        Terminal.run_bash_cmd(["git", "push"], cwd=str(parent_repo_dir))
        input(f"\n{margin}{Terminal.Text.GREEN}Successfully deleted dependency and pushed change to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except Exception as e:
        input(f"\n{margin}{Terminal.Text.RED}Failed to delete dependency. It may not exist, or already deleted.{Terminal.Text.RESET} Press enter to continue.\n")
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_restore_dependencies(cwd: str):
    """
    Resets dependencies to the current versions tagged and available for a repository.
    param: cwd [str] The GitHub current working directory
    """
    Handler.handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repos.",
        subtitle_text=f"Select which to {Terminal.Text.YELLOW}restore{Terminal.Text.CYAN} its {Terminal.Text.YELLOW}dependencies{Terminal.Text.CYAN} for.",
        bash_cmds=[
            # pull content of current versions of deps and do a hard-reset on local copies
            ["git", "fetch", "origin"],
            ["git", "submodule", "update", "--init", "--recursive"],
            ["git", "submodule", "foreach", "--recursive", "git reset --hard"]
        ],
        
        success_msg="Successfully synced dependencies with versions on GitHub.",
        err_msg="Failed to sync dependencies."
    )
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_update_to_latest_dependencies(cwd: str):
    """
    Refreshes the dependencies attached to a repository by pulling updated dependency content from GitHub. 
    """
    Handler.handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repositories.",
        subtitle_text=f"Select which to {Terminal.Text.YELLOW}update dependencies{Terminal.Text.CYAN} to {Terminal.Text.YELLOW}latest versions{Terminal.Text.CYAN} for.",
        bash_cmds=[
            # get latest versions of deps and push these changes to github 
            ["git", "submodule", "update", "--remote"],
            ["git", "add", f"{path('dep') / path('*')}"],
            ["git", "commit", "-m", "Updated submodules/dependencies"],
            ["git", "push"],
            # pull content of latests versions of deps and do a hard-reset on local copies
            ["git", "fetch", "origin"],
            ["git", "submodule", "update", "--init", "--recursive"],
            ["git", "submodule", "foreach", "--recursive", "git reset --hard"]
        ],
        success_msg="Dependencies successfully updated and then pushed to GitHub.",
        err_msg="Failed to update dependencies. It could be that they're already up to date." 
    )
    # clear the screen once done with menu
    Terminal.Screen.clear_screen()

def handle_exit():
    """
    Exits the entire program.
    """
    margin = " " * GUIMenu.MENU_ORIGIN[0]
    print(f"\n {margin}exiting program...")
    exit(0)

def handle_close_menu(menu: GUIMenu):
    """
    Exits a given menu and clears the screen.
    param: menu [GUIMenu] The menu to exit
    """
    Terminal.Screen.clear_screen()
    menu.exit()

def handle_ssh_auth(menu: GUIMenu):
    """
    Authorize SSH Key with GitCAD program. This function is initiated by a menu. 
    param: menu [GUIMenu] The menu
    """
    ssh_key = find_ssh_key() # find the name of existing key
    if ssh_key[0].name == "id_ed25519": # only use id_ed25519 key 
        ssh_key = ssh_key[0]
    else: # ignore all other keys; notify user
        input(f"{Terminal.Text.BOLD}{Terminal.Text.RED} warning: expected ssh key id_ed25519 but could not find it!{Terminal.Text.YELLOW} Press ENTER to continue to GitCAD.{Terminal.Text.RESET}")
        menu.exit()
        return
   
    # evaluate github ssh access; this checks for authorizations but does not grant it. 
    # only linux OS will allow granting authorization at this stage (other OS will not)
    github_ssh_status = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-T", "git@github.com"],
        stdin=sys.stdin, stdout=sys.stdout,
        env=os.environ,
        check=False
    )

    authorize_github_ssh = None # authorize ssh key if not already and the check above said authorization is not yet given
    # if this is a linux OS, then the chance to allow authentication was the stage above; in this case, skip this stage below
    if sys.platform.startswith("win") and github_ssh_status.returncode == 255: # ssh access is not yet granted (run on non-linux only)
        print(f"\n{Terminal.Text.BOLD}{Terminal.Text.YELLOW}A passphrase is needed to authenticate. {Terminal.Text.BLUE}You CANNOT see it as you type!{Terminal.Text.RESET}") 
        print(f"\n{Terminal.Text.CYAN}When giving a passphrase, you get TWO attempts before authentication fails.{Terminal.Text.RESET}")
        
        # attempt to authorize the key
        authorize_github_ssh = subprocess.run(
            ["ssh-add", f"{ssh_key}"],
            stdin=sys.stdin, stdout=sys.stdout,
            env=os.environ,
            check=False
        )

    # check for signs of failed authentication 
    failed_win_auth = authorize_github_ssh is not None and authorize_github_ssh.returncode != 0 # failed to auth on authorizing github ssh with returncode not 0
    failed_linux_auth = github_ssh_status.returncode == 255 # failed to auth on checking stats with returncode 255
    # check for signs of successful authentication (this may be mutually exclusive and succeeding true implies failed is false, but outlining criteria for failure and success separately is still important)
    succeeded_win_auth = (authorize_github_ssh is None or authorize_github_ssh.returncode == 0) # succeeded auth on status or authorizing github ssh succeeded with returncode 0
    succeeded_linux_auth = (authorize_github_ssh is None and github_ssh_status.returncode != 255) # authorize github ssh should not be used, but the status check cannot fail with returncode 255

    # authorize var should be none if it wasn't needed (ssh access already granted)
    if (sys.platform.startswith("win") and failed_win_auth) or (sys.platform.startswith("linux") and failed_linux_auth): # failed to authenticate 
        print(f"{Terminal.Text.RED}\nLooks like authentication failed.{Terminal.Text.BOLD} (or you didn't give an SSH Key){Terminal.Text.END} \nUnderstand secure access to GitHub is limited without a key.{Terminal.Text.RESET}")
        input(f"{Terminal.Text.BOLD}{Terminal.Text.YELLOW}Press ENTER to continue to GitCAD.{Terminal.Text.RESET}")  
        Terminal.Screen.clear_screen() 
        menu.exit()
        return
    elif (sys.platform.startswith("win") and succeeded_win_auth) or (sys.platform.startswith("linux") and succeeded_linux_auth): # auth succeeded
        input(f"{Terminal.Text.BOLD}{Terminal.Text.GREEN}Authentication Complete! {Terminal.Text.YELLOW}Press ENTER to continue to GitCAD.{Terminal.Text.RESET}")
        Terminal.Screen.clear_screen()
        menu.exit()
        return
    # report a warning if OS is not recognized or failed unexpectedly when authorizing
    input(f"{Terminal.Text.BOLD}{Terminal.Text.RED} warning: Authentication proceeded with unknown status!{Terminal.Text.YELLOW} Press ENTER to continue to GitCAD.{Terminal.Text.RESET}")
    menu.exit()
    return

def find_ssh_key():
    """
    Searches the `~/.ssh` directory for usable ssh keys. If the default "id_ed25519" key if found, only it is returned.  
    """
    ssh_dir = path.home() / ".ssh" # dir of keys 
    def_key_dir = ssh_dir / "id_ed25519" # dir of default key
    if def_key_dir.exists(): # return default key if found 
        return [def_key_dir]
    # find alternative to the default keys starting with "id_"
    alt_key_dirs = list(ssh_dir.glob("id_*"))
    alt_key_dirs = [key for key in alt_key_dirs if not key.name.endswith(".pub")] # ignore .pub
    return alt_key_dirs
 
def handle_keygen(menu: GUIMenu):
    """
    Runs the keygen commands to create an SSH Key. This function is initiated from a menu. 
    param: menu [GUIMenu] The menu
    """
    # prompt key generation input from user
    print(f"{Terminal.Text.BLUE}Now you will be asked for: (1) an email, (2) the name of the file to save the key to, \nand (3) a key passphrase/password{Terminal.Text.RESET}")
    print(f"{Terminal.Text.ORANGE}When you see: 'Enter file in which to save the key...', ignore and SKIP this. Just press {Terminal.Text.BOLD}{Terminal.Text.YELLOW}ENTER{Terminal.Text.END}{Terminal.Text.ORANGE} to skip.{Terminal.Text.RESET}")

    # make/find .ssh folder/root
    home = os.path.expanduser("~")
    ssh_key_root = os.path.join(home, ".ssh")
    os.makedirs(ssh_key_root, exist_ok=True)
    ssh_key_name = input("Please enter your GitHub email: ")
    # initiate keygen with provided GitHub email
    result = subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", ssh_key_name], 
                    cwd=ssh_key_root, stdin=sys.stdin, env=os.environ, check=False)
    
    ssh_key = find_ssh_key() # find the actual name of existing key
    if ssh_key[0].name == "id_ed25519": # only use id_ed25519 key 
        ssh_key = ssh_key[0]
    else: # ignore all other keys; notify user
        input(f"{Terminal.Text.BOLD}{Terminal.Text.RED} warning: expected ssh key id_ed25519 but could not find it!{Terminal.Text.YELLOW} Press ENTER to continue to GitCAD.{Terminal.Text.RESET}")
        menu.exit()
        return

    # prompt with results of keygen
    Terminal.Screen.clear_screen()
    if result.returncode == 0:
        # prompt successful key generation; prompt for user to put key on GitHub account
        print(f"{Terminal.Text.GREEN}Successfuly created SSH Key.{Terminal.Text.END}")
        print(f"{Terminal.Text.BOLD}{Terminal.Text.BLUE}You need to upload this key to your GitHub account.{Terminal.Text.END} To do this, {Terminal.Text.YELLOW}go to GitHub and click:{Terminal.Text.RESET} \n(1) Account Settings \n(2) SSH and GPG Keys \n(3) New SSH key{Terminal.Text.END}")
        print(f"\n{Terminal.Text.BOLD}{Terminal.Text.BLUE}Now at {Terminal.Text.YELLOW}Add new SSH Key{Terminal.Text.BLUE} GitHub webpage:{Terminal.Text.RESET}")
        print(f"(1) Let the name be whatever you want. \n(2) Let key type be \'Authentication Key\'. \n(3){Terminal.Text.BOLD}{Terminal.Text.ORANGE} In key text box, paste the following:{Terminal.Text.RESET}")

        if sys.platform.startswith("win"): # read .pub file content for windows
            subprocess.run(["powershell", "Get-Content", f"{ssh_key}.pub"],
                            cwd=ssh_key_root, stdin=sys.stdin, stdout=sys.stdout, env=os.environ, check=False)
        else: # read .pub file content for linux / other OS
            subprocess.run(["cat", f"{ssh_key}.pub"], 
                           cwd=ssh_key_root, stdin=sys.stdin, stdout=sys.stdout, env=os.environ, check=False)
        
        print(f"\nOnce {Terminal.Text.BOLD}{Terminal.Text.UNDERLINE}COPIED and PASTED{Terminal.Text.RESET} the key code above into GitHub, you can continue.")
        time.sleep(3) # brief delay to stop user for not reading the key .pub file content
    else: # failed to make key
        print(f"{Terminal.Text.RED}Failed to create SSH Key.{Terminal.Text.END}")
    # exit keygen menu
    input(f"Press {Terminal.Text.BOLD}{Terminal.Text.YELLOW}ENTER{Terminal.Text.END} to continue.")
    Terminal.Screen.clear_line()
    menu.exit()

def handle_create_ssh_key():
    """
    Runs the menu to create an SSH Key. Generating a key will give neccessary prompts and output needed info for GitHub setup. 
    """
    # run key generation menu
    keygen_menu = GUIMenu(title_text=f"Would you like to {Terminal.Text.YELLOW}create an SSH Key?",
                          subtitle_text="SSH keys allow secure GitHub Account access. Use arrow/ENTER keys.")
    keygen_menu.add_option("Yes. Generate a key.", handle_keygen, lambda: keygen_menu)
    keygen_menu.add_option("No. Skip this.", handle_close_menu, lambda: keygen_menu)
    keygen_menu.run()

# Building an EXE notes:
# This can be done with pyinstaller on the cmd line:
# EX: pyinstaller --onefile __main__.py --copy-metadata readchar
# 
# Add readchar; is is needed. 
#

def __main__():

    # init program
    Terminal.Screen.clear_screen()
    ssh_url = "https://docs.github.com/en/authentication/connecting-to-github-with-ssh/about-ssh"
    ssh_link = f"\033]8;;{ssh_url}\033\\SSH Key\033]8;;\033\\"
    
    # create ssh auth menu
    auth_menu = GUIMenu(title_text=f"Welcome to GitCAD. {Terminal.Text.YELLOW}Would you like to use a GitHub SSH key?", 
                        subtitle_text="SSH keys allow secure GitHub Account access. Use arrow/ENTER keys.")
    auth_menu.add_option(f"Yes. Let's authorize my {Terminal.Text.CYAN}{ssh_link}{Terminal.Text.END}.", handle_close_menu, lambda: auth_menu)
    auth_menu.add_option("No. (This may limit GitCAD's access to GitHub)", handle_close_menu, lambda: auth_menu)
    auth_menu.add_option(f"{Terminal.Text.ORANGE}Select here to make an SSH Key{Terminal.Text.END}", handle_create_ssh_key, None)
    auth_menu.add_option(f"{Terminal.Text.YELLOW}<EXIT>{Terminal.Text.END}", handle_exit)
    # run the auth menu
    auth_menu.run() 

    # create the main menu
    main_menu = GUIMenu(title_text="Welcome to GitCAD.", subtitle_text="What would you like to do? Use arrow keys to navigate.")
    main_menu.add_option("Clone a new repository from GitHub", handle_clone_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Pull latest repository changes from GitHub", handle_pull_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Push repository changes back to GitHub", handle_push_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Create a new dependency", handle_create_dependency, Handler.handle_github_current_working_directory)
    main_menu.add_option("Delete a dependency", handle_delete_dependency, Handler.handle_github_current_working_directory)
    main_menu.add_option("Retore dependencies to the current versions", handle_restore_dependencies, Handler.handle_github_current_working_directory)
    main_menu.add_option("Set dependencies latest versions available", handle_update_to_latest_dependencies, Handler.handle_github_current_working_directory)
    main_menu.add_option(f"{Terminal.Text.YELLOW}<EXIT>{Terminal.Text.END}", handle_exit)
    # run the main menu
    main_menu.run()

# run the program
if __name__ == "__main__":
    __main__()
