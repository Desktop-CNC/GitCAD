#!/usr/bin/python3
import readchar
import Terminal

class GUIMenu:
    """
    Creates a text-based menu screen that prompts a user with a title message and options to select from.
    This menu appears in the command line. 
    """
    
    def __init__(self, title_text: str):
        """
        Creates a GUIMenu instance. 
        param: title_text [str] The specified title
        """
        self.title_text = title_text
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

    def exit(self):
        """
        Ends running the menu and exits from it.
        """
        self.run_flag = False
        Terminal.Screen.clear_screen()

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
                print(f"\n{Terminal.Text.BLUE}{Terminal.Text.BOLD}{self.title_text}{Terminal.Text.END}{Terminal.Text.RESET}\n")
            # convert the prompt options names/texts into a list to print to the menu screen
            gui = [f"{Terminal.Text.BOLD if i == self.arrow_index else ''}{'➤  ' if i == self.arrow_index else '' ''} {self.prompts[i][0]}{Terminal.Text.END}" for i in range(0, len(self.prompts))]
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
                Terminal.Screen.clear_line()
                for line in gui:
                    Terminal.Screen.move_cursor_relatively(-1,0)
                    Terminal.Screen.clear_line()
        # returns the menu options selected at runtime
        return selected_option_history   