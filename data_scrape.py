import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',  # HTML as final response is HTML
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://zoutrition.missouri.edu',
    'Referer': 'https://zoutrition.missouri.edu/NetNutrition/zoutrition/Unit/SelectUnitFromSideBar',  # Referer URL (adjust based on each step)
}

session = requests.Session()
def send_post_request(url, data):
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print(f"fRequest for {url} successful.")
        return response
    else:
        return None

def Select_Unit_From_Side_Bar():
    data = {
        'unitOid': '1',
    }
    url ='https://zoutrition.missouri.edu/NetNutrition/zoutrition/Unit/SelectUnitFromSideBar'
    return send_post_request(url, data)

def Select_Unit_From_Child_Units_List():
    data = {
        'unitOid': '2',
    }
    url ='https://zoutrition.missouri.edu/NetNutrition/zoutrition/Unit/SelectUnitFromChildUnitsList'
    return send_post_request(url, data)

def Select_Menu():
    data = {
        'menuOid': '1654172',
    }
    url = 'https://zoutrition.missouri.edu/NetNutrition/zoutrition/Menu/SelectMenu'
    return send_post_request(url, data)

def Select_Item():
    data = {
        'detailOid': '158641007',
    }
    url = 'https://zoutrition.missouri.edu/NetNutrition/zoutrition/Menu/SelectItem'
    return send_post_request(url, data)

def Show_Item_Nutrition_Label():
    data = {
        'detailOid': '158641007',
    }
    url = 'https://zoutrition.missouri.edu/NetNutrition/zoutrition/NutritionDetail/ShowItemNutritionLabel'
    return send_post_request(url, data)
    
def main():
    side_bar_response = Select_Unit_From_Side_Bar()
    child_units_response = Select_Unit_From_Child_Units_List()
    menu_response = Select_Menu()
    item_response = Select_Item()
    html_page = Show_Item_Nutrition_Label()
    print(html_page.text)

main()