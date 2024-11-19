from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

data_buffer = []
titles_set = set()
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
nutrients_looking_for = ["Total Fat", "Saturated Fat", "TransFat", "Cholesterol", "Sodium", "Total Carbohydrate",
                         "Dietary Fiber", "Total Sugars", "Protein", "Vit. D", "Calcium", "Iron"]

def put_data_into_json(i):
    with open(f'data/{restaurants[i]}.json', 'w') as json_file:
        json.dump(data_buffer, json_file, indent=4)

def replace_unicode(string):
    string = re.sub(r'\u00a0', ' ', string)
    string = re.sub(r'\n', ' ', string)
    string = re.sub(r'\"', ' ', string)
    return string

def find_matching_index(nutrient):
    for index, substring in enumerate(nutrients_looking_for):
        if substring in nutrient:
            return index
    return -1

def handle_data(page):
    url = page.content()
    soup = BeautifulSoup(url, 'html.parser')
    title = soup.select_one('.cbo_nn_LabelHeader').get_text(strip=True)
    if title in titles_set:
        print(f"Already added {title} ***SKIPPING***")
        return
    titles_set.add(title)
    serving_info = soup.select_one('.cbo_nn_LabelBottomBorderLabel').get_text(strip=True) # decode
    serving_info = replace_unicode(serving_info)
    calories = soup.select_one('.cbo_nn_LabelSubHeader .inline-div-right')
    if calories:
        calories = calories.get_text(strip=True)
        nutrients = []
        nutrient_rows = soup.select('.cbo_nn_LabelBorderedSubHeader')
        for row in nutrient_rows:
            nutrient_name = row.select_one('.inline-div-left').get_text(strip=True)
            nutrient_value = row.select_one('.inline-div-right').get_text(strip=True)

            if "Include" in nutrient_name and "Added Sugars" in nutrient_name:
                nutrient_value = nutrient_name.split(' ')[1]
                if nutrient_value != "NA":
                    nutrient_value += 'g'
                nutrient_name = "Added Sugars"
            else:
                index = find_matching_index(nutrient_name)
                str_len = len(nutrients_looking_for[index])
                temp = nutrient_name[:str_len] 
                nutrient_value = nutrient_name[str_len:]
                if nutrient_value != "NA":
                    for i, char in enumerate(nutrient_value):
                        if char.isdigit():
                            nutrient_value = nutrient_value[i:]
                            break
                nutrient_name = temp

            nutrients.append({nutrient_name: nutrient_value})
        ingredients = soup.select_one('.cbo_nn_LabelIngredients')
        if ingredients:
            ingredients = ingredients.get_text(strip=True)
            ingredients = replace_unicode(ingredients)
            nutrition_data = {
                "Title": title,
                "Serving Info": serving_info,
                "Calories": calories,
                "Nutrients": nutrients,
                "Ingredients": ingredients,
            }
            data_buffer.append(nutrition_data)
            print(f"Added {title}")

def click_left_menu(page, side_bar_buttons, i): # clicks on left menu to choose resturant 
    side_bar_button = side_bar_buttons.nth(i)
    side_bar_button.wait_for(state="visible")
    side_bar_button.click()
    page.wait_for_timeout(1000)

def click_child_menu(page, child_buttons, j):
    cur_child_button = child_buttons.nth(j)
    cur_child_button.wait_for(state="visible")
    cur_child_button.click()
    page.wait_for_timeout(1000)

def select_day(page, daily_links, l): # loads the menu
    cur_menu_button = daily_links.nth(l)
    cur_menu_button.wait_for(state="visible")
    cur_menu_button.click()
    page.wait_for_timeout(1000)

def main_back(page):
    back_button = page.locator('#btn_Back1') # go back so we can continue
    back_button.click()
    page.wait_for_timeout(1000)
    
def extra_back(page):
    back_button = page.locator('#btn_BackmenuList1') # need to go back twice
    back_button.click()
    page.wait_for_timeout(1000)

def load_nutrition_info(page, dining_options, k):
    cur_menu_item = dining_options.nth(k)
    cur_menu_item.wait_for(state="visible")
    cur_menu_item.click() # loads nutriiton info
    page.wait_for_timeout(1500)
    handle_data(page)

def normal_logic(page, side_bar_buttons, i):
    click_left_menu(page, side_bar_buttons, i)
    child_buttons = page.locator("a[onclick^='javascript:childUnitsSelectUnit']") # locate all child buttons
    child_button_count = child_buttons.count()
    if child_button_count == 0:
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
        for j in range(child_button_count): # each menu 'ex: pepsi beverage fountain'
            if (i == 13) and (j < 2 or j == 4): # skip 1,2 and 5 on the mark
                continue
            click_child_menu(page, child_buttons, j)
            if (j == 0 and i != 8) or (((i == 9) or (i == 11)) and (j < 5)) or ((i == 13) and (j == 2 or j == 3)): # only the first menus have dates, pizza & MO has no days listed
                daily_links = page.locator("a[onclick^='javascript:menuListSelectMenu']")
                daily_links_count = daily_links.count()
                for l in range(2,3):
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

def main(range1, range2):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('https://zoutrition.missouri.edu/NetNutrition/zoutrition')
        side_bar_buttons = page.locator("a[onclick^='javascript:sideBarSelectUnit']")

        for i in range(range1, range2): # each left button
            data_buffer.clear()
            titles_set.clear()
            if i == 2: # catalyst cafe doesn't exist anymore
                continue
            # if i in dining_halls: # dining halls have different structure
            #     dining_hall_logic(page, side_bar_buttons, i)
            # else:
            # test_logic(page, side_bar_buttons, 0)
            normal_logic(page, side_bar_buttons, i)
            put_data_into_json(i)
        browser.close()

main(15,16) # pass in the range

# CLEAN UP THIS CODE (functions, class)
# make feature for keyboard interrupt to automatically send current info to file 
