import os
import sys
import traceback
import time

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

class ZoutritionScraper():

    def __init__(self, index_array):
        self.DEBUG = False
        self.index_array = index_array
        self.current_file_name = ""
        self.current_file_building = ""
        self.page_status = None
        self.dining_location_choice = 0
        self.child_menu_choice = 0
        self.menu_choice = 0
        self.start()

    def start(self):
        self.start_page()
        for self.index in self.index_array:
            self.starter_manager()

        self.close_playright()

    def status_update(self):
        self.check_page_status()
        self.call_manager_from_page_status()

    def call_manager_from_page_status(self):
        self.page.wait_for_load_state('networkidle')
        status_function_map = {
            "child_restaurants": self.child_restaurant_manager,
            "menu_tables": self.menu_tables_manager,
            "none": self.menu_tables_manager,
            "menu": self.menu_manager,
        }
        manager_to_call = status_function_map.get(self.page_status)
        try:
            manager_to_call()
        except Exception as e:
            print(f"Could not call manager from page status: {self.page_status}")
            print(e)
            print("Traceback:")
            traceback.print_exc()

    #######################
    ##### PLAYWRIGHT  #####
    #######################

    def start_page(self): # starts the page and gets the left buttons 
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=True, slow_mo=500)
        self.page = self.browser.new_page()
        self.page.goto('https://zoutrition.missouri.edu/NetNutrition/zoutrition')
        self.dining_location_buttons = self.page.locator("a[onclick^='javascript:sideBarSelectUnit']")
        self.page.wait_for_load_state('networkidle')

    def close_playright(self): # ends playwright safely
        self.browser.close()
        self.p.stop()
        sys.exit(0)
    
    ####################
    ##### MANAGERS #####
    ####################

    def starter_manager(self):
        self.navigate_to_dining_location(self.index)
        self.make_sub_dir()
        self.status_update()
        self.add_nutrition_info_to_json() # gets executed after everything rewinds

    def child_restaurant_manager(self):
        if self.DEBUG:
            print("***GOT TO CHILD MANAGER***")
    
        self.get_child_resturant_options()
        for i in range(self.child_resturant_buttons_count): # looping to click every child button
            self.navigate_to_child_resturant(i)
            self.status_update()
            if i < self.child_resturant_buttons_count - 1:
                self.get_back_button()
                if self.DEBUG:
                    print("***GOT BACK BUTTON***") 
                self.click_back_button()
                if self.DEBUG:
                    print("***CLICKED BACK BUTTON***")                 
                self.check_page_status()
    
    def menu_tables_manager(self):
        if self.DEBUG:
            print("***GOT TO MENU TABLES MANAGER***") 

        self.get_menu_tables_options()  
        if self.menu_table_buttons_count == 0:
            return
        else:
            self.seen_set_dictionary = {}
            for i in range(self.menu_table_buttons_count): # clicking every menu table button
                self.navigate_to_menu_label(i)
                self.status_update()
                self.get_back_button()
                self.click_back_button()
                self.check_page_status()

    def menu_manager(self):
        self.add_file_to_data_dict() # file path is fully built

        page_header = self.page.locator('.cbo_nn_itemHeaderDiv')
        page_header_text = page_header.inner_text()
        if page_header_text not in self.seen_set_dictionary:
            self.seen_set_dictionary[page_header_text] = set()

        self.get_all_items_on_menu()

        for i in range(self.menu_page_buttons_count): # prevents duplicates without having to scrape data and compare titles
            item = self.menu_items_array[i]
            if item not in self.seen_set_dictionary[page_header_text]:
                self.seen_set_dictionary[page_header_text].add(item)
                self.scrape_menu_item(i)
                self.filter_nutrition_info()

    ####################
    ##### NAVIGATE #####
    ####################

    def navigate_to_child_resturant(self, idx):
        self.page.wait_for_load_state('networkidle')
        child_resturant = self.child_resturant_buttons.nth(idx)
        child_resturant.wait_for(state="visible")

        self.current_file_building = child_resturant.inner_text().replace(" ", "_").lower()
        self.current_file_name = self.current_file_building 

        child_resturant.click()

    def navigate_to_dining_location(self, idx):
        self.page.wait_for_load_state('networkidle')
        dining_location = self.dining_location_buttons.nth(idx)
        dining_location.wait_for(state="visible")
        dining_location.click()

    def navigate_to_menu_label(self, idx):
        self.page.wait_for_load_state('networkidle')
        menu_location = self.menu_table_buttons.nth(idx)
        menu_location.wait_for(state="visible")

        self.current_file_building = '_' + menu_location.inner_text().replace(" ", "_").lower()
        self.current_file_name += self.current_file_building 

        menu_location.click()

    def click_back_button(self):
        self.page.wait_for_load_state('networkidle')
        back_button = self.back_button
        back_button.wait_for(state="attached")
        back_button.click()

    ##################
    ##### SCRAPE #####
    ##################

    def check_page_status(self):
        self.page.wait_for_load_state('networkidle')
        # locate child restaurants
        self.page.wait_for_load_state('networkidle')
        element = self.page.locator(".cbo_nn_childUnitsTable")
        if element.count() > 0:
            self.page_status = "child_restaurants"
            return
        # locate menu table
        element = self.page.locator(".cbo_nn_menuTable")
        if element.count() > 0:
            self.page_status = "menu_tables"
            return
        # locate menu
        element = self.page.locator(".cbo_nn_itemGridDiv")
        if element.count() > 0:
            self.page_status = "menu"
            return
        # nothing was found
        self.page_status = "none"
        if self.DEBUG:
            print(f"***{self.page_status}***")

    def get_menu_tables_options(self):
        self.page.wait_for_load_state('networkidle')
        self.menu_table_buttons = self.page.locator("a[onclick^='javascript:menuListSelectMenu']")
        self.menu_table_buttons_count = self.menu_table_buttons.count()

    def get_child_resturant_options(self):
        self.page.wait_for_load_state('networkidle')
        self.child_resturant_buttons = self.page.locator("a[onclick^='javascript:childUnitsSelectUnit']")
        self.child_resturant_buttons_count = self.child_resturant_buttons.count()

    def get_back_button(self):
        self.page.wait_for_load_state('networkidle')
        try:
            if self.page_status == "menu":
                self.page.locator("#btn_Back1").wait_for(state="attached")
                self.back_button = self.page.locator('#btn_Back1')
                self.current_file_name = self.current_file_name.replace(self.current_file_building, "")
            elif self.page_status == "menu_tables" or self.page_status == "none":
                self.page.locator("#btn_BackmenuList1").wait_for(state="attached")
                self.back_button = self.page.locator('#btn_BackmenuList1')
                self.current_file_name = self.current_file_name.replace(self.current_file_building, "")
        except Exception as e:
            print(f"Error: {e}")

    ################
    ##### DATA #####
    ################

    def get_all_items_on_menu(self):
        self.menu_items_array = []
        self.menu_page_buttons = self.page.locator('td.cbo_nn_itemHover')
        self.menu_page_buttons_count = self.menu_page_buttons.count()
        for i in range(self.menu_page_buttons_count):
            current_element = self.menu_page_buttons.nth(i)
            self.menu_items_array.append(current_element.inner_text())

    def scrape_menu_item(self, index):
        self.page.wait_for_load_state('networkidle')
        item_to_click = self.menu_page_buttons.nth(index)
        item_to_click.click()

        time.sleep(0.1)
        self.page.locator('.cbo_nn_NutritionLabelTable').wait_for(state="visible")
        url = self.page.content()
        soup = BeautifulSoup(url, 'html.parser')
        nutrition_label_div = soup.select_one('.cbo_nn_NutritionLabelTable')
        
        time.sleep(0.1)
        self.title = nutrition_label_div.select_one('.cbo_nn_LabelHeader')

        time.sleep(0.1)
        self.serving_size_information = nutrition_label_div.select_one('.bold-text.inline-div-right')

        time.sleep(0.1)
        self.calories_per_serving = nutrition_label_div.select_one('.inline-div-right.bold-text.font-22')

        self.values_spans = []
        time.sleep(0.1)
        values_div = nutrition_label_div.select('.cbo_nn_LabelBorderedSubHeader, .cbo_nn_LabelNoBorderSubHeader')
        for value in values_div:
            spans = value.find_all('span')
            if len(spans) > 1:
                value_span = spans[1]
            else:
                value_span = spans[0]
            self.values_spans.append(value_span)

        time.sleep(0.1)
        self.ingredients_information = nutrition_label_div.select_one('.cbo_nn_LabelIngredients')

        time.sleep(0.1)
        self.allergens_information = nutrition_label_div.select_one('.cbo_nn_LabelAllergens')

        close_button = self.page.locator('[onclick="javascript:closeNutritionDetailPanel();"]')
        close_button.wait_for(state="visible")
        close_button.click()

    def replace_unicode(self, string):
        string = re.sub(r'\u00a0', ' ', string)
        string = re.sub(r'\n', ' ', string)
        string = re.sub(r'\"', ' ', string)
        return string

    def clean_added_sugars(self, string):
        if "NA" in string or not string.strip():
            return "N/A"
        
        match = re.search(r'(\d+\.?\d*)\s*g', string)
        return f"{match.group(1)}g" if match else "N/A"
    
    def filter_nutrition_info(self):
        title = self.title.get_text().title() if self.title else "N/A"
        serving_info = self.serving_size_information.get_text() if self.serving_size_information else "N/A"
        if self.serving_size_information:
            serving_info = self.replace_unicode(serving_info)
        calories = self.calories_per_serving.get_text() if self.calories_per_serving else "N/A"

        # Use "N/A" as the default for each nutrient if the corresponding value is missing
        nutrient_names = [
        "Total Fat", "Saturated Fat", "Trans Fat", "Cholesterol", "Sodium",
        "Total Carbohydrates", "Dietary Fiber", "Total Sugars", "Added Sugars",
        "Protein", "Vit. D", "Calcium", "Iron", "Potas."
        ]
        nutrients = {name: "N/A" for name in nutrient_names}
        for i, name in enumerate(nutrient_names):
            if i < len(self.values_spans):
                value = self.values_spans[i].get_text(strip=True)
                if name == "Added Sugars":
                    nutrients[name] = self.clean_added_sugars(value)
                else:
                    nutrients[name] = value

        ingredients = self.ingredients_information.get_text(strip=True) if self.ingredients_information else "N/A"
        if self.ingredients_information:
            ingredients = self.replace_unicode(ingredients)
        allergens = self.allergens_information.get_text(strip=True) if self.allergens_information else "N/A"
        if self.allergens_information:
            allergens = self.replace_unicode(allergens)

        nutrition_data = {
                "Title": title,
                "Serving Info": serving_info,
                "Calories": calories,
                "Nutrients": nutrients,
                "Ingredients": ingredients,
                "Allergens": allergens,
            }

        print(f"Added {title}")
        self.data_dict[self.current_file_name].append(nutrition_data)

    def make_sub_dir(self):
        # makes base subfolder
        restaurants = [
            "Baja Grill",
            "Bookmark Cafe",
            "Catalyst Cafe",
            "Do Mundo's",
            "Emporium",
            "Infusion",
            "Legacy Grill",
            "Mort's",
            "Pizza & MO",
            "Plaza 900",
            "Potential Energy Cafe",
            "Restaurants at Southwest",
            "Savor",
            "The MARK on 5th Street",
            "Wheatstone Bistro",
            "Wings & MO"
        ]
        parent_folder = "../data"
        self.folder_name = restaurants[self.index]
        self.full_folder_path = os.path.join(parent_folder, self.folder_name)
        if not os.path.exists(self.full_folder_path):
            os.makedirs(self.full_folder_path)
            print(f"***Folder '{self.full_folder_path}' created.***")
        else:
            print(f"***Folder '{self.full_folder_path}' aleady exists.***") 

        self.data_dict = {}
    
    def add_file_to_data_dict(self):
        if self.current_file_name not in self.data_dict:
            self.data_dict[self.current_file_name] = []
            print(f"***Moving to {self.current_file_name}...***")

    def add_nutrition_info_to_json(self):
        for key, value in self.data_dict.items():
            file_name = os.path.join(self.full_folder_path, f"{key}.json")

            with open(file_name, 'w') as json_file:
                json.dump(value, json_file, indent=4)
                print(f"***Dumping to {file_name}***")

# FUTURE FEATURES

# FIND MISSING ITEMS
# PROGRESS BAR