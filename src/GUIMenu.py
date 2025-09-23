#!/usr/bin/python3
import readchar
import Terminal

class GUIMenu:
    """
    Creates a text-based menu screen that prompts a user with a title message and options to select from.
    This menu appears in the command line. 
    """
    MENU_ORIGIN = (4,2)
    MENU_WIDTH = 80
    MENU_PADDING = 2
    MENU_ARROW = "➤"

    def __init__(self, title_text: str, subtitle_text: str=None):
        """
        Creates a GUIMenu instance. 
        param: title_text [str] The specified title
        param: subtitle_text [str] Optional subtitle text
        """
        self.title_text = title_text
        self.subtitle_text = subtitle_text if subtitle_text is not None else ""
        self.arrow_index = 0 # where to start the option selector
        self.prompts = [] # list of options' prompts and handlers 
        Terminal.Screen.clear_screen() # clear the screen for the menu
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

    def print_line(self, line: str, padding: int, margin: int, left_offset: int=None, right_offset: int=None):
        """
        Prints a formatted line of the GUI menu.
        param: line [str] The text to format
        param: padding [int] The amount of whitespace padding before borders
        param: margin [int] The amount of whitespace after borders 
        param: left_offset [int] Optional extra whitespace offset to the left of the content
        param: right_offset [int] Optional extra whitespace offset to the right of the content
        """
        # convert to concatenated whitespace 
        padding = " " * padding
        margin = " " * margin
        left_offset = "" if left_offset is None else " " * max(0, left_offset)
        right_offset = "" if right_offset is None else " " * max(0, right_offset)

        # insert text into fixed length line
        line = line.ljust(GUIMenu.MENU_WIDTH) 
        if line.__contains__(GUIMenu.MENU_ARROW):
            line = line + (" " * 4)
        # add borders and print
        line = margin + "||" + left_offset + padding + line + padding + right_offset + "||" + margin
        print(line)

    def exit(self):
        """
        Ends running the menu and exits from it.
        """
        self.run_flag = False

    def run(self):
        """
        A blocking function. This runs the menu. 
        """
        self.run_flag = True # set run state 
        # input from the keyboard
        user_input = None
        # the last option selected from the menu
        option_selected = None
        
        # separator bar
        separator = "=" * GUIMenu.MENU_WIDTH
        
        # loop to run the menu
        while self.run_flag:
            # only print the title if not done already, or an option was selected
            if user_input is None or user_input == readchar.key.ENTER: 
                # print offset to menu origin 
                print("\n"*GUIMenu.MENU_ORIGIN[1])
                self.print_line(line=separator, padding=0, margin=GUIMenu.MENU_ORIGIN[0])
                self.print_line(line=f"{Terminal.Text.BLUE}{Terminal.Text.BOLD}{self.title_text}{Terminal.Text.END}{Terminal.Text.RESET}", padding=GUIMenu.MENU_PADDING, margin=GUIMenu.MENU_ORIGIN[0], right_offset=13)
                self.print_line(line=f"{Terminal.Text.CYAN}{self.subtitle_text}{Terminal.Text.RESET}", padding=GUIMenu.MENU_PADDING, margin=GUIMenu.MENU_ORIGIN[0], right_offset=0)
                self.print_line(line=separator, padding=0, margin=GUIMenu.MENU_ORIGIN[0])
                
            # convert the prompt options names/texts into a list to print to the menu screen
            gui = [f"{Terminal.Text.BOLD if i == self.arrow_index else ''}{GUIMenu.MENU_ARROW + (' ' * 4) if i == self.arrow_index else (' ' * 2)} {self.prompts[i][0]}{Terminal.Text.END}" for i in range(0, len(self.prompts))]
            for line in gui:
                self.print_line(line=line, padding=GUIMenu.MENU_PADDING, margin=GUIMenu.MENU_ORIGIN[0])
            self.print_line(line=separator, padding=0, margin=GUIMenu.MENU_ORIGIN[0])

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
                    option_selected = self.prompts[self.arrow_index][0]
                    # put select/cursor arrow to the top of the menu
                    self.arrow_index = 0
                    break
        
            # clear lines of the menu options printed if an option was not selected
            if user_input != readchar.key.ENTER:
                Terminal.Screen.clear_line()
                for i in range(0, len(gui)+1):
                    Terminal.Screen.move_cursor_relatively(-1,0)
                    Terminal.Screen.clear_line()
                
        Terminal.Screen.clear_screen()
        # returns the menu options selected at runtime
        return option_selected