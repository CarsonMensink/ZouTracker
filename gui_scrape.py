from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
import sys

class ZuotritionScraper:
    def __init__(self):
        self.restaurants = {
            "Baja Grill": 0,
            "Bookmark Cafe": 1,
            "Catalyst Cafe (depreciated)": 2,
            "Do Mundo's": 3,
            "Emporium": 4,
            "Infusion": 5,
            "Legacy Grill": 6,
            "Mort's": 7,
            "Pizza & MO": 8,
            "Plaza 900": 9,
            "Potential Energy Cafe": 10,
            "Restaurants at Southwest": 11,
            "Savor": 12,
            "The MARK on 5th Street": 13,
            "Wheatstone Bistro": 14,
            "Wings & MO": 15,
        }
        self.loop = True
        self.function_manager()

    ####################
    ##### MANAGERS #####
    ####################
    def function_manager(self):
        self.start_page()

        while self.loop:
            self.check_page_status()
            self.call_manager_based_on_status()

        self.close_playright()

    def call_manager_based_on_status(self):
        if self.page_status == "none":
            self.none_manager()
        elif self.page_status == "child_restaurants":
            self.child_resturant_manager()
        elif self.page_status == "menu_tables":
            self.menu_tables_manager()
        elif self.page_status == "menu":
            self.menu_manager()

    def none_manager(self):
        self.get_restaurant_input()
        self.navigate_to_dining_location()

    def child_resturant_manager(self):
        # get back button
        self.get_child_resturant_options()
        self.get_child_resturant_input()
        self.navigate_to_child_resturant()

    def menu_tables_manager(self):
        # get back button
        self.get_menu_tables_options()
        self.get_menu_tables_input()
        self.navigate_to_menu_tables()
    
    def menu_manager(self):
        # get back button
        # prompt for back or done
        print("menu final")

    #######################
    ##### PLAYWRIGHT  #####
    #######################
    def start_page(self): # starts the page and gets the left buttons 
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False, slow_mo=350)
        self.page = self.browser.new_page()
        self.page.goto('https://zoutrition.missouri.edu/NetNutrition/zoutrition')
        self.dining_location_buttons = self.page.locator("a[onclick^='javascript:sideBarSelectUnit']")

    def close_playright(self): # ends playwright safely
        self.browser.close()
        self.p.stop()
        sys.exit(0)
    
    def navigate_to_dining_location(self):
        dining_location = self.dining_location_buttons.nth(self.dining_location_choice)
        dining_location.wait_for(state="visible")
        dining_location.click()

    def get_child_resturant_options(self):
        self.child_menu_options = {}
        self.child_resturant_buttons = self.page.locator("a[onclick^='javascript:childUnitsSelectUnit']")
        child_resturant_buttons_count = self.child_resturant_buttons.count()
        for i in range(child_resturant_buttons_count):
            child_button = self.child_resturant_buttons.nth(i)
            child_button.wait_for(state="visible")
            child_button_text = child_button.inner_text()
            self.child_menu_options[child_button_text] = i
            
    def navigate_to_child_resturant(self):
        child_resturant = self.child_resturant_buttons.nth(self.child_menu_choice)
        child_resturant.wait_for(state="visible")
        child_resturant.click()

    def get_menu_tables_options(self):
        self.menu_table_options = {}
        index_counter = 0
        self.menu_table_buttons = self.page.locator("a[onclick^='javascript:menuListSelectMenu']")
        parent_container = self.page.locator(".cbo_nn_menuPrimaryRow, .cbo_nn_menuAlternateRow")
        for row in parent_container.all():
            date_element = row.locator('td').nth(0)
            date_text = date_element.inner_text().strip().split("\n")[0]

            link_elements = row.locator('.cbo_nn_menuLink')
            links = [link.inner_text().strip().lower() for link in link_elements.all()]
            index_list = list(range(index_counter, index_counter + len(links)))
            index_counter += len(links)
            self.menu_table_options[date_text] = [links, index_list]

    def check_page_status(self):
        # locate child restaurants
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

    def navigate_to_menu_tables(self):
        menu_table = self.menu_table_buttons.nth(self.menu_table_index)
        menu_table.wait_for(state="visible")
        menu_table.click()       

    #################
    ###### GUI ######
    #################
    def get_restaurant_input(self): # returns a value used for the page to navigate
        self.print_restaurant_options()
        while True:
            user_input = input("Pick a restaurant: ")
            if user_input in self.restaurants:
                self.dining_location_choice = self.restaurants[user_input]
                return
            elif user_input == '-1':
                self.close_playright()
                return
            else:
                print("Invalid input. Please try again.")

    def print_restaurant_options(self): # helper function for getting values
        print("\n\nAvailable restaurants:")
        for name, value in self.restaurants.items():
            print(f"{value}: {name}")
        print("To exit the application type '-1'")

    def get_child_resturant_input(self): # returns a value used for the page to navigate
        self.print_child_menu_options()
        while True:
            user_input = input("Pick a child menu: ")
            if user_input in self.child_menu_options:
                self.child_menu_choice = self.child_menu_options[user_input]
                return
            elif user_input == '-1':
                self.close_playright()
                return
            else:
                print("Invalid input. Please try again.")

    def print_child_menu_options(self): # helper function for getting value
        print("\n\nAvailable child menus:")
        for name, value in self.child_menu_options.items():
            print(f"{value}: {name}")
        print("To exit the application type '-1'")

    def get_menu_tables_input(self):
        self.print_menu_table_dates()
        self.get_menu_tables_date()
        self.print_menu_table_links()
        self.get_menu_table_link()

    def get_menu_tables_date(self):
        while True:
            user_input = input("Pick a date: ")
            if user_input in self.menu_table_options:
                self.date_picked = user_input
                return
            elif user_input == '-1':
                self.close_playright()
                return
            else:
                print("Invalid input. Please try again.")

    def print_menu_table_dates(self):
        print("\n\nAvailable dates:")
        for name, value in self.menu_table_options.items():
            print(f"Date: {name}")
            print("-" * 20)
        print("To exit the application type '-1'")
    
    def get_menu_table_link(self):
        while True:
            user_input = input("Pick a date: ")
            links_list = self.menu_table_options[self.date_picked][0]
            if user_input.lower() in links_list:
                link_index = links_list.index(user_input.lower())
                self.menu_table_index = self.menu_table_options[self.date_picked][1][link_index]
                return
            elif user_input == '-1':
                self.close_playright()
                return
            else:
                print("Invalid input. Please try again.")       

    def print_menu_table_links(self):
        print("\n\nAvailable links:")
        link_list, index_list = self.menu_table_options[self.date_picked]
        for i in range(len(link_list)):
            print(f"{index_list[i]}: {link_list[i].title()}")
        print("To exit the application type '-1'")

ZuotritionScraper()

# add lower case compability for everything here
# add back buttons
# add menu manager