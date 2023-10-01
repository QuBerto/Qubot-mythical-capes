import time
import utilities.color as clr
from model.osrs.osrs_bot import OSRSBot
from pathlib import Path
import utilities.ocr as ocr
import pyautogui

__HOMES_PATH = Path(__file__).parent
QUBERTO_IMAGES = __HOMES_PATH.joinpath("images")
class OSRSConstruction(OSRSBot):
    def __init__(self):
        bot_title = "Quberto Mythical cape"
        description = "Build and removes mythical capes. Set build spot yellow, a build cape green, Tag your servant cyan and don't forget to unnote 21 teak planks"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 100

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):

        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.main()
            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def main(self):
        
        if self.is_furniture():
            self.handle_menu()
        if self.get_nearest_tag(clr.GREEN):
            self.remove()
            if self.count_planks() < 7:
                if not self.get_noted_planks():
                    self.out_of_planks()
                self.butler()
        elif self.get_nearest_tag(clr.YELLOW) and self.count_planks() > 2:
            self.build()

        
    def out_of_planks(self):
        self.log_msg("Out of noted planks")
        self.stop()
       
    def butler(self):
        current_planks = self.count_planks()
        if butler := self.get_nearest_tag(color=clr.CYAN):
            while not self.mouseover_text("Talk"):
                self.mouse.move_to(butler.random_point(), mouseSpeed="fastest")
            self.mouse.click()
            self.log_msg(f"Talking to Sevant")
            while not self.is_chat("Un-note"):
                if self.count_planks() > current_planks:
                    if butler := self.get_nearest_tag(color=clr.CYAN):
                        while not self.mouseover_text("Talk"):
                            self.mouse.move_to(butler.random_point(), mouseSpeed="fastest")
                        self.mouse.click()
                        while not self.is_chat("Un-note"):
                            time.sleep(1/10)
                        self.mouse.click()
                        return True
                time.sleep(1/10)
            pyautogui.press("1")
            self.log_msg(f"Requested planks")
      
    def remove(self):
        self.rigth_click(clr.GREEN, "Teleport")
        tries = 0
        while not self.find_menu_text("Remove", font=ocr.BOLD_12, rect=self.win.game_view, color=clr.WHITE):
            if tries > 10:
                return False
            time.sleep(1/10)
            tries +=1
        self.move_to_menu_text("Remove")
        tries = 0
        while not self.is_chat("Yes") :
            if tries > 10:
                return False
            time.sleep(1/10)
            tries +=1
        if self.is_chat("Yes"):
            pyautogui.press("1")
        tries = 0
        while self.get_nearest_tag(clr.GREEN):
            if tries > 20:
                return False
            time.sleep(1/10)
            tries +=1
        self.log_msg("Remvoed item")
        return True

    def build(self):
        self.rigth_click(clr.YELLOW)
        tries = 0
        while not self.find_menu_text("Build", font=ocr.BOLD_12, rect=self.win.game_view, color=clr.WHITE):
            if tries > 10:
                return False
            time.sleep(1/10)
            tries +=1
        tries = 0
        while not self.move_to_menu_text("Build"):
            if tries > 3:
                self.log_msg(f"Failed to do richt click menu")
                return False
            tries +=1
            pass
        tries = 0
        while not self.is_furniture():
            if tries > 10:
                self.log_msg(f"Failed to open build menu")
                return False
            time.sleep(1/10)
            tries +=1
        self.handle_menu()
        
    def handle_menu(self):
        pyautogui.press("4")
        self.log_msg(f"Pressed 4 to build")
        tries = 0
        while self.is_furniture():
            if tries > 10:
                self.log_msg(f"Failed to select build")
                return False
            time.sleep(1/10)
            tries +=1
        tries = 0
        self.log_msg(f"Menu is closed")
        while self.get_nearest_tag(clr.YELLOW):
            if tries > 10:
                self.log_msg(f"Failed to build")
                return False
            time.sleep(1/10)
            tries +=1
        self.log_msg(f"Item has been build")

    def is_furniture(self):
        furn = ocr.find_text("Furniture",rect=self.win.game_view,font=ocr.BOLD_12,color=clr.Color([255,152,31]))
        if furn:
            return True
        return False
    
    def rigth_click(self, color, mouseover="Walk"):
        cape = self.get_nearest_tag(color=color)
        if cape:
            self.mouse.move_to(cape.random_point(), mouseSpeed="fastest")
            while not self.mouseover_text(mouseover):
                self.mouse.move_to(cape.random_point(), mouseSpeed="fastest")
            self.mouse.right_click()
            return True
        return False
    
    def move_to_menu_text(self, text: str):
        if menu_text := self.find_menu_text(text, font=ocr.BOLD_12, rect=self.win.game_view, color=clr.WHITE):
            self.log_msg(f"Moving mouse to {text}")
            self.mouse.move_to(menu_text.random_point(), mouseSpeed="fastest")
            if self.mouseover_text(["Walk", "Talk", "Use"]):
                return False
            self.mouse.click()
            self.log_msg(f"Clicked {text}")
            return True
        return False
    
    def is_chat(self, text: str, colr=clr.BLACK):
        """Check if text is in chat window
        :param str text: A string to search inside the chat window
        :param clr color: A clr object representing the font color
        """
        if ocr.find_text(text,rect=self.win.chat,font=ocr.QUILL_8,color=colr):
            self.log_msg(f"{text} is found in chat" )
            return True
        return False
    

    def find_menu_text(self, text: str, font, rect, color):
        if objects := ocr.find_text(text, color=color, font=font, rect=rect):
            return objects[0]
        return False
    
    def count_planks(self):
        planks = self.get_all_tagged_in_rect(rect=self.win.control_panel,color=clr.GREEN)
        if planks:
            return len(planks)
        return 0
    
    def get_noted_planks(self):
        if items := self.get_all_tagged_in_rect(self.win.control_panel,color=clr.BLUE):
            return True
        return False
        
