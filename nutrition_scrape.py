from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def handle_data(page):
    pass

def click_left_menu(page, side_bar_buttons, i): # clicks on left menu to choose resturant 
    side_bar_button = side_bar_buttons.nth(i)
    side_bar_button.wait_for(state="visible")
    side_bar_button.click()
    page.wait_for_timeout(2000)

def click_child_menu(page, child_buttons, j):
    cur_child_button = child_buttons.nth(j)
    cur_child_button.wait_for(state="visible")
    cur_child_button.click()
    page.wait_for_timeout(2000)

def select_day(page, daily_links, l): # loads the menu
    cur_menu_button = daily_links.nth(l)
    cur_menu_button.wait_for(state="visible")
    cur_menu_button.click()
    page.wait_for_timeout(2000)

def main_back(page):
    back_button = page.locator('#btn_Back1') # go back so we can continue
    back_button.click()
    page.wait_for_timeout(2000)
    
def extra_back(page):
    back_button = page.locator('#btn_BackmenuList1') # need to go back twice
    back_button.click()
    page.wait_for_timeout(2000)

def load_nutrition_info(page, dining_options, k):
    cur_menu_item = dining_options.nth(k)
    cur_menu_item.wait_for(state="visible")
    cur_menu_item.click() # loads nutriiton info
    page.wait_for_timeout(2000)
    handle_data(page)

def normal_logic(page, side_bar_buttons, i):
    click_left_menu(page, side_bar_buttons, i)
    child_buttons = page.locator("a[onclick^='javascript:childUnitsSelectUnit']") # locate all child buttons
    child_button_count = child_buttons.count()

    for j in range(child_button_count): # each menu 'ex: pepsi beverage fountain'
        if (i == 13) and (j < 2 or j == 4): # skip 1,2 and 5 on the mark
            continue
        click_child_menu(page, child_buttons, j)

        if (j == 0 and i != 8) or ((i != 13) and (j < 5)) or ((i == 13) and (j == 2 or j == 3)): # only the first menus have dates, pizza & MO has no days listed
            daily_links = page.locator("a[onclick^='javascript:menuListSelectMenu']")
            daily_links_count = daily_links.count()
            for l in range(daily_links_count):
                select_day(page, daily_links, l)

                dining_options = page.locator("td.cbo_nn_itemHover") # get all menu items
                dining_option_count = dining_options.count()
                for k in range(dining_option_count): # getting nutrition information for every menu item
                    load_nutrition_info(page, dining_options, k)
                main_back(page)
            extra_back(page)
        else:
            dining_options = page.locator("td.cbo_nn_itemHover") # get all menu items
            dining_option_count = dining_options.count()
            for k in range(dining_option_count): # getting nutrition information for every menu item
                load_nutrition_info(page, dining_options, k)
            main_back(page)

# def dining_hall_logic(page, side_bar_buttons, i):
    click_left_menu(page, side_bar_buttons, i)
    child_buttons = page.locator("a[onclick^='javascript:childUnitsSelectUnit']") # locate all child buttons
    child_button_count = child_buttons.count()

    for j in range(child_button_count): # each menu 'ex: pepsi beverage fountain'
        if (i == 13) and (j < 2 or j == 4): # skip 1,2 and 5 on the mark
            continue
        click_child_menu(page, child_buttons, j)

        if ((i != 13) and (j < 5)) or ((i == 13) and (j == 2 or j == 3)): # logic for which spots have an extra step (menu select)
            daily_links = page.locator("a[onclick^='javascript:menuListSelectMenu']")
            daily_links_count = daily_links.count()
            for l in range(daily_links_count):
                select_day(page, daily_links, l)

                dining_options = page.locator("td.cbo_nn_itemHover") # get all menu items
                dining_option_count = dining_options.count()
                for k in range(dining_option_count): # getting nutrition information for every menu item
                    load_nutrition_info(page, dining_options, k)
                main_back(page)
            extra_back(page)
        else:
            dining_options = page.locator("td.cbo_nn_itemHover") # get all menu items
            dining_option_count = dining_options.count()
            for k in range(dining_option_count): # getting nutrition information for every menu item
                load_nutrition_info(page, dining_options, k)
            main_back(page)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('https://zoutrition.missouri.edu/NetNutrition/zoutrition')
        side_bar_buttons = page.locator("a[onclick^='javascript:sideBarSelectUnit']")
        side_bar_button_count = side_bar_buttons.count()

        skipped_buttons = []
        # dining_halls = [9,11,13]

        for i in range(side_bar_button_count): # each left button
            if i == 12 or i == 2: # savor kitchen is ahead 1 step and catalyst cafe doesn't exist anymore
                skipped_buttons.append(side_bar_buttons.nth(i))
                continue
            # if i in dining_halls: # dining halls have different structure
            #     dining_hall_logic(page, side_bar_buttons, i)
            # else:
            normal_logic(page, side_bar_buttons, i)
    browser.close()

main()
