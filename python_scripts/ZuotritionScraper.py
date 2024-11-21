from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
import sys

class ZoutritionScraper():

    def __init__(self, index_array):
        self.index_array = index_array
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
            "menu": self.menu_manager,
        }
        manager_to_call = status_function_map.get(self.page_status)
        try:
            manager_to_call()
        except Exception as e:
            print(f"Could not call manager from page status: {self.page_status}")

    #######################
    ##### PLAYWRIGHT  #####
    #######################

    def start_page(self): # starts the page and gets the left buttons 
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False, slow_mo=350)
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
        self.status_update()

    def child_restaurant_manager(self):
        self.get_child_resturant_options()
        for i in range(self.child_resturant_buttons_count): # looping to click every child button
            self.navigate_to_child_resturant(i)
            self.status_update()
            if i < self.child_resturant_buttons_count - 1:
                self.get_back_button()
                self.click_back_button()
                self.check_page_status()
    
    def menu_tables_manager(self):
        self.get_menu_tables_options()
        for i in range(self.menu_table_buttons_count): # clicking every menu table button
            self.navigate_to_menu_lable(i)
            self.status_update()
            self.get_back_button()
            self.click_back_button()
            self.check_page_status()

    def menu_manager(self):
        # add some kind of organizing, maybe a dictionary to add the "daily" or "breakfast" or whatever the "title" is and only compare with that set 
        # go item by item and if its not seen in the set then scrape it
        # do NOT go item by item by clicking on them, just scrape the page
        pass

    ####################
    ##### NAVIGATE #####
    ####################

    def navigate_to_child_resturant(self, idx):
        self.page.wait_for_load_state('networkidle')
        child_resturant = self.child_resturant_buttons.nth(idx)
        child_resturant.wait_for(state="visible")
        child_resturant.click()

    def navigate_to_dining_location(self, idx):
        self.page.wait_for_load_state('networkidle')
        dining_location = self.dining_location_buttons.nth(idx)
        dining_location.wait_for(state="visible")
        dining_location.click()

    def navigate_to_menu_lable(self, idx):
        self.page.wait_for_load_state('networkidle')
        menu_location = self.menu_table_buttons.nth(idx)
        menu_location.wait_for(state="visible")
        menu_location.click()

    def navigate_to_menu_tables(self):
        self.page.wait_for_load_state('networkidle')
        menu_table = self.menu_table_buttons.nth(self.menu_table_index)
        menu_table.wait_for(state="visible")
        menu_table.click()

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
            elif self.page_status == "menu_tables":
                self.page.locator("#btn_BackmenuList1").wait_for(state="attached")
                self.back_button = self.page.locator('#btn_BackmenuList1')
        except Exception as e:
            print(f"Error: {e}")
