#!/usr/bin/python3
from pathlib import Path as path
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
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RESET = '\033[0m' # Resets to default color and style
    def __init__(self):
        pass

def run_bash_cmd(cmd: list, cwd:str=None):
    """
    Runs a bash command. 
    param: cmd [list] The command to run
    param: cwd [str] Optional current working directory
    """
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return result