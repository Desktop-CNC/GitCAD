from GUIMenu import GUIMenu
from pathlib import Path as path
import Terminal
import Handler
import sys

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
        Terminal.run_bash_cmd(["git", "clone", repo_url], cwd=str(cwd))
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
        pause_prompt=False
    )   
    # check if the menu was exited
    if local_repo.__contains__('<') and local_repo.__contains__('>'):
        return
    # get commit message to push
    commit_message = input(f"\n{margin}{Terminal.Text.BOLD}{Terminal.Text.BLUE}What changes were made? {Terminal.Text.CYAN}Press enter when done, but type here: {Terminal.Text.RESET}")
    # try to push
    try:
        Terminal.run_bash_cmd(["git", "add", "."], cwd=cwd / path(local_repo))
        Terminal.run_bash_cmd(["git", "commit", "-m", commit_message], cwd=cwd / path(local_repo))
        Terminal.run_bash_cmd(["git", "push"], cwd=cwd / path(local_repo))
        input(f"\n{Terminal.Text.GREEN}Successfully pushed the repository to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except:
        input(f"\n{Terminal.Text.RED}Did not push changes. It's possible there are no changes to push.{Terminal.Text.RESET} Press enter to continue.\n")
    # clear the screen once done with menu
    Terminal.Screen.clear_line()

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
        pause_prompt=False
    )
    # check if the menu was exited
    if parent_repo.__contains__('<') and parent_repo.__contains__('>'):
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
        ignore_repos=ignore_repos
    )
    # check if the menu was exited
    if dep_repo.__contains__('<') and dep_repo.__contains__('>'):
        handle_create_dependency(cwd=cwd) # restart the whole process
        return # exit upon completion

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
        input(f"\n{Terminal.Text.GREEN}Successfully created dependency and pushed it to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except:
        input(f"\n{Terminal.Text.RED}Failed to create dependency. It may already exist, or a chosen repository does not.{Terminal.Text.RESET} Press enter to continue.\n")
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
        pause_prompt=False
    )
    # check if the menu was exited
    if parent_repo.__contains__('<') and parent_repo.__contains__('>'):
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
        allow_repos=allowed_repos
    )

    # check if the menu was exited
    if dep_repo.__contains__('<') and dep_repo.__contains__('>'):
        handle_delete_dependency(cwd=cwd) # restart the whole process
        return # exit upon completion

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
        input(f"\n{Terminal.Text.GREEN}Successfully deleted dependency and pushed change to GitHub.{Terminal.Text.RESET} Press enter to continue.\n")
    except Exception as e:
        input(f"\n{Terminal.Text.RED}Failed to delete dependency. It may not exist, or already deleted.{Terminal.Text.RESET} Press enter to continue.\n")
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

def handle_exit():
    print("\n exiting program...")
    exit(0)

def __main__():

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
