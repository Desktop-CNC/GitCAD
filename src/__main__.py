from GUIMenu import GUIMenu
import Terminal
import Handler

def handle_clone_repository(cwd: str):
    """
    Handles cloning an online GitHub repository for the main menu.
    param: cwd [str] The repository current working directory
    """
    # prompt the repo cloning
    print("\nWelcome to GitHub CAD Helper\n.")
    # get online GitHub repo URL
    repo_url = input("Please input the GitHub Repository URL: ")
    try: # attempt to clone
        Terminal.run_bash_cmd(["git", "clone", repo_url], cwd=cwd)
        print("\nRepository successfully cloned.\n")
    except: # handle failed cloning
        input(f"\n{Terminal.Text.RED}Failed to clone the repository.{Terminal.Text.RESET} Press enter to continue.")
        Terminal.Screen.clear_screen()

def handle_pull_repository(cwd: str):
    """
    Handles pulling an online GitHub repository to update the locally cloned one. This handler is for the main menu. 
    param: cwd [str] The GitHub current working directory
    """
    Handler.handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos. \nSelect the one you want to pull changes from GitHub for.", 
        bash_cmds=[
            ["git", "stash"],
            ["git", "fetch", "origin"],
            ["git", "reset", "--hard", "origin/main"]],
        success_msg="Successfully pulled the repository.",
        err_msg="Failed to pull the repository."
    )


def handle_push_repository(cwd: str):
    """
    Handles pushing a local repository back to GitHub. This is for the main menu.
    param: cwd [str] The GitHub current working directory
    """
    Handler.handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos. \nSelect the one you want to push changes back to GitHub for.",
        bash_cmds=[
            ["git", "add", "."],
            ["git", "commit", "-m", input("What changes were made? Press enter when done, but type here: ")],
            ["git", "push"]],
        success_msg="Successfully pushed the repository",
        err_msg="Did not push changes. It's possible there are no changes to push."
    )    

def handle_add_dependency(cwd: str):
    """
    Adds a dependency repository to a parent repository. 
    param: cwd [str] The GitHub current working directory
    """
    pass

def handle_remove_dependency(cwd: str):
    pass

def handle_refresh_dependencies(cwd: str):
    pass

def handle_exit():
    print("\n exiting program...")
    exit(0)

def main():
    # create the main menu
    main_menu = GUIMenu(title_text="Welcome to GitCAD. \nWhat would you like to do? Use arrow keys to navigate.")
    main_menu.add_option("Clone a new repository from GitHub", handle_clone_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Pull repository changes from GitHub", handle_pull_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Push repository changes back to GitHub", handle_push_repository, Handler.handle_github_current_working_directory)
    main_menu.add_option("Add a dependency", handle_add_dependency, Handler.handle_github_current_working_directory)
    main_menu.add_option("Remove a dependency", handle_remove_dependency, Handler.handle_github_current_working_directory)
    main_menu.add_option("Refresh dependencies", handle_refresh_dependencies, Handler.handle_github_current_working_directory)
    main_menu.add_option("<EXIT>", handle_exit)
    # run the main menu
    main_menu.run()

# run the program
if __name__ == "__main__":
    main()
