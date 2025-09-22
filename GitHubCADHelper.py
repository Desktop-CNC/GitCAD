import subprocess
import sys
import os
from pathlib import Path as path
import readchar

# MENU LOGIC FOR THE PROGRAM
class GUIMenu:
    """
    Creates a text-based menu screen that prompts a user with a title message and options to select from.
    This menu appears in the command line. 
    """
    # text formatting 
    BOLD = '\033[1m'
    END = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RESET = '\033[0m' # Resets to default color and style
    
    def __init__(self, title_text: str):
        """
        Creates a GUIMenu instance. 
        param: title_text [str] The specified title
        """
        self.title_text = title_text
        self.arrow_index = 0 # where to start the option selector
        self.prompts = [] # list of options' prompts and handlers 
        GUIMenu.clear_screen() # clear the screen for the menu
        self.run_flag = True # runs the menu when true

    def add_option(self, option_text: str, handler: any, arg_supplier_handler: any=None):
        """
        Creates and adds an option to the menu. An option prompts with text. When selected, the option calls a
        handler function that can have arguments passed in from a supplier. 
        param: option_text [str] The text shown on the menu 
        param: handler [any] The function to call when the option is selected
        param: arg_supplier_handler [any] An optional arg that gets the arguments to pass into the handler
        """
        self.prompts.append((option_text, handler, arg_supplier_handler))

    def exit(self):
        """
        Ends running the menu and exits from it.
        """
        self.run_flag = False
        GUIMenu.clear_screen()

    def run(self):
        """
        A blocking function. This runs the menu. 
        """
        self.run_flag = True # set run state 
        # input from the keyboard
        user_input = None
        selected_option_history = []
        # loop to run the menu
        while self.run_flag:
            # only print the title if not done already, or an option was selected
            if user_input is None or user_input == readchar.key.ENTER: 
                print(f"\n{GUIMenu.BLUE}{GUIMenu.BOLD}{self.title_text}{GUIMenu.END}{GUIMenu.RESET}\n")
            # convert the prompt options names/texts into a list to print to the menu screen
            gui = [f"{GUIMenu.BOLD if i == self.arrow_index else ""}{"➤  " if i == self.arrow_index else " "} {self.prompts[i][0]}{GUIMenu.END}" for i in range(0, len(self.prompts))]
            for line in gui:
                print(line)    

            # loop while listening for user input from the keyboard
            while True:
                user_input = readchar.readkey()
                # clamp the selector arrow and move it based on input and the list of options from the menu
                if user_input == readchar.key.DOWN:
                    self.arrow_index = min(self.arrow_index+1, len(self.prompts)-1)
                    break # break to exit listening loop
                elif user_input == readchar.key.UP:
                    self.arrow_index = max(self.arrow_index-1, 0)
                    break
                # option selected; 
                elif user_input == readchar.key.ENTER:
                    # check for args
                    args = self.prompts[self.arrow_index][2]
                    if args is None: # call option handler function without args
                        self.prompts[self.arrow_index][1]()
                    else: # call option handler function with args
                        # call args to get content
                        self.prompts[self.arrow_index][1](args())
                    # append choice to history of options selected
                    selected_option_history.append(self.prompts[self.arrow_index][0])
                    # put select/cursor arrow to the top of the menu
                    self.arrow_index = 0
                    break
        
            # clear lines of the menu options printed if an option was not selected
            if user_input != readchar.key.ENTER:
                GUIMenu.clear_line()
                for line in gui:
                    GUIMenu.move_cursor_relatively(-1,0)
                    GUIMenu.clear_line()
        # returns the menu options selected at runtime
        return selected_option_history

    @staticmethod
    def clear_screen():
        """
        Clears the content in the terminal.
        """
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def clear_line():
        """
        Clears the content on the current line the cursor sits in the terminal.
        """
        sys.stdout.write("\033[2K")
        sys.stdout.write("\r")
        sys.stdout.flush()

    @staticmethod
    def move_cursor_relatively(delta_row: int, delta_col: int):
        """
        Moves the cursor to another position relative to its current position in the terminal.
        param: delta_row [int] The change in rows to move the cursor
        param: delta_col [int] The change in columns to move the cursor
        """
        if delta_row < 0: 
            sys.stdout.write(f"\033[{abs(delta_row)}A")
        else: 
            sys.stdout.write(f"\033[{abs(delta_row)}B")
        if delta_col < 0:
            sys.stdout.write(f"\033[{abs(delta_col)}D")
        else:
            sys.stdout.write(f"\033[{abs(delta_col)}C")
        sys.stdout.flush()            


# START OF THE PROGRAM

def run_bash_cmd(cmd: list, cwd:str=None):
    """
    Runs a bash command. 
    param: cmd [list] The command to run
    param: cwd [str] Optional current working directory
    """
    print(subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True))

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
                    run_bash_cmd(cmd, cwd=repo_dir) # run bash command
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
   
def handle_clone_repository(cwd: str):
    """
    Handles cloning an online GitHub repository for the main menu.
    param: cwd [str] The repository current working directory
    """
    # prompt the repo cloning
    print("\nWelcome to GitHub CAD Helper.")
    # get online GitHub repo URL
    repo_url = input("Please input the GitHub Repository URL: ")
    try: # attempt to clone
        run_bash_cmd(["git", "clone", repo_url], cwd=cwd)
        print("\nRepository successfuly cloned.\n")
    except: # handle failed cloning
        input(f"\n{GUIMenu.RED}Failed to clone the repository.{GUIMenu.RESET} Press enter to continue.")
        GUIMenu.clear_screen()


def handle_fetch_repository(cwd: str):
    """
    Handles fetching an online GitHub repository to update the locally cloned one. This handler is for the main menu. 
    param: cwd [str] The GitHub current working directory
    """
    r = handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos. Select the one you want to fetch GitHub for.", 
        bash_cmds=[
            ["git", "stash"],
            ["git", "fetch", "origin"],
            ["git", "reset", "--hard", "origin/main"]],
        success_msg="Successfully fetched the repository.",
        err_msg=f"{GUIMenu.RED}Failed to fetch the repository.{GUIMenu.RESET} Press enter to continue."
    )

    print(r)

def handle_push_repository(cwd: str):
    """
    Handles pushing a local repository back to GitHub. This is for the main menu.
    param: cwd [str] The GitHub current working directory
    """
    handle_repository_menu(
        cwd=cwd, 
        menu_title="Here are your local repos. Select the one you want to push changes back to GitHub for.",
        bash_cmds=[
            ["git", "add", "."],
            ["git", "commit", "-m", input("What changes were made? Press enter when done, but type here: ")],
            ["git", "push"]],
        success_msg="Successfuly pushed the repository",
        err_msg=f"{GUIMenu.RED}Did not push changes.{GUIMenu.RESET} It's possible there are no changes to push."
    )    

def handle_add_dependency(cwd: str):
    """
    Adds a dependency repository to a parent repository. 
    param: cwd [str] The GitHub current working directory
    """
    selected_options = [[], []] # lists of the selected options from the parent repo menu and the dep menu
    # the options selected from this menu; use menu to get a repo to add a dep too
    selected_options[0] = handle_repository_menu(
        cwd=cwd,
        menu_title="Here are your local repos. Select which to add a dependency too.",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        terminal_option_name="<NEXT>"
    )

    # if the menus did nothing (no options selected) or 
    # only the one option <GO BACK> option was selected, then do no more; exit this handler
    if len(selected_options[0]) < 2:
        return
    # get second to last selected option; this was the chosen repo from the menu
    selected_repo = selected_options[0][max(0, len(selected_options[0])-2)]

    # use menu to get a repo to be the dep to add
    selected_options[1] = handle_repository_menu(
        cwd=cwd,
        menu_title=f"Which reposity below should be imported into \"{selected_repo}\"? (Don't choose \"{selected_repo}\" here!)",
        bash_cmds=[],
        success_msg="",
        err_msg="",
        terminal_option_name="<DONE>"
    )

    # if the menus did nothing (no options selected) or 
    # only the one option <GO BACK> option was selected, then do no more; exit this handler
    if len(selected_options[0]) < 2 or len(selected_options[1]) < 2:
        return
    # get the second to last selected option from dep menu; this was chosed as the repo dependency to be added to the parent
    dep_repo = selected_options[1][max(0, len(selected_options[1])-2)]

    # list of commands for adding the dependency as a GitHub submodule
    bash_cmds = [
        ["git", "submodule", "add", dep_repo, f"deps/{dep_repo}"],
        ["git", "submodule", "update", "--init", "--recursive"],
        ["git", "add", ".gitmodules", f"deps/{dep_repo}"],
        ["git", "commit", "-m", f"Added {dep_repo} as a submodule"],
        ["git", "push"]
    ]

    # get local repo directory
    local_repo_dir = cwd + "/" + selected_repo
    # run commands
    for cmd in bash_cmds:
        run_bash_cmd(cmd, cwd=local_repo_dir)

def handle_remove_dependency(cwd: str):
    pass

def handle_fetch_dependencies(cwd: str):
    pass

def handle_exit():
    print("\n exiting program...")
    exit(0)

def main():
    # create the main menu
    main_menu = GUIMenu(title_text="Weclome to GitHub CAD Helper. What would you like to do? Use arrow keys to navigate.")
    main_menu.add_option("Clone a new repository from GitHub", handle_clone_repository, handle_github_current_working_directory)
    main_menu.add_option("Fetch repository changes from GitHub", handle_fetch_repository, handle_github_current_working_directory)
    main_menu.add_option("Push repository changes back to GitHub", handle_push_repository, handle_github_current_working_directory)
    main_menu.add_option("Add a dependency", handle_add_dependency, handle_github_current_working_directory)
    main_menu.add_option("Remove a dependency", handle_remove_dependency, handle_github_current_working_directory)
    main_menu.add_option("Refresh dependencies", handle_fetch_dependencies, handle_github_current_working_directory)
    main_menu.add_option("<EXIT>", handle_exit)
    # run the main menu
    main_menu.run()
# run the program
if __name__ == "__main__":
    main()

