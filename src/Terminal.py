#!/usr/bin/python3
from pathlib import Path as path
import Terminal
import subprocess
import sys

class Screen:
    """
    A Screen singleton that 
    """
    def __init__(self):
        pass
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

class Text:
    """
    """
    # text formatting 
    BOLD = '\033[1m'
    END = '\033[0m'
    GREY = '\033[37m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    YELLOW = '\033[93m'
    UNDERLINE = "\x1B[4m"
    RESET = '\033[0m' # Resets to default color and style
    def __init__(self):
        pass

def run_bash_cmd(cmd: list, cwd:path=None):
    """
    Runs a bash command. 
    param: cmd [list] The command to run
    param: cwd [str] Optional current working directory
    """
    result = subprocess.run(cmd, cwd=cwd, check=False, text=True, capture_output=True, shell=True)
    # print commands printed from the current working directory 
    margin = " "*4 # margin for offset
    # get name from cwd directory and pop off the end    
    repo_name = cwd.__str__().split(slash()).pop()
    cmd_str = " ".join(result.args) # get list of args 
    # format cwd and command line args to show the bash command
    print(f"{margin}{Terminal.Text.BOLD}{Terminal.Text.YELLOW}{cwd}{slash()}{Terminal.Text.BLUE}{repo_name}>{Terminal.Text.RESET} {cmd_str}")
    # return results
    return result

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