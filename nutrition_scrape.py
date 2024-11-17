from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://zoutrition.missouri.edu/NetNutrition/zoutrition')
    side_bar_buttons = page.locator("a[onclick^='javascript:sideBarSelectUnit']")

    side_bar_button_count = side_bar_buttons.count()
    skipped_buttons = []
    dining_halls = [9, 11, 13] # needs unique logic for dining halls

    for i in range(side_bar_button_count): # each left button
        if i == 12 or i == 2: # savor kitchen is ahead 1 step
            skipped_buttons.append(side_bar_button.nth(i))
            continue
        side_bar_button = side_bar_buttons.nth(i)
        side_bar_button.wait_for(state="visible")
        side_bar_button.click() # clicks on left menu to choose resturant 
        page.wait_for_timeout(2000)

        child_buttons = page.locator("a[onclick^='javascript:childUnitsSelectUnit']") # locate all child buttons
        child_button_count = child_buttons.count()
        for j in range(child_button_count): # each menu 'ex: pepsi beverage fountain'
            cur_child_button = child_buttons.nth(j)
            cur_child_button.wait_for(state="visible")
            cur_child_button.click() # clicking on first menu 'ex: baja grill' -> leads to all days
            page.wait_for_timeout(2000)

            if j == 0 and i != 8: # only the first menus have dates, pizza & MO has no days listed
                first_menu_button = page.locator("a[onclick^='javascript:menuListSelectMenu']").nth(0) # currently only caring about the first menu
                first_menu_button.wait_for(state="visible")
                first_menu_button.click() # loads the menu
                page.wait_for_timeout(2000)

            menu_items_buttons = page.locator("td.cbo_nn_itemHover") # get all menu items
            menu_item_count = menu_items_buttons.count()
            for k in range(menu_item_count): # getting nutrition information for every menu item
                cur_menu_item = menu_items_buttons.nth(k)
                cur_menu_item.wait_for(state="visible")
                cur_menu_item.click() # loads nutriiton info
                page.wait_for_timeout(2000)
                # HANDLE DATA

            back_button = page.locator('#btn_Back1') # go back so we can continue
            back_button.click()
            page.wait_for_timeout(2000)
            if j == 0 and i != 8: # go back extra time, don't need to ever for pizza & MO
                back_button = page.locator('#btn_BackmenuList1') # need to go back twice
                back_button.click()
        

            
    browser.close()

# PLAZA, SOUTHWEST, MARK [9, 11, 13]