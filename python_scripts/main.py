from ZuotritionScraper import ZoutritionScraper

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
print("Select restaurants by index (separate multiple selections with a space):")
for idx, restaurant in enumerate(restaurants):
    print(f"{idx}: {restaurant}")

input = list(map(int, input("Enter the indexes of the restaurants you want to select: ").split()))
ZoutritionScraper(input)