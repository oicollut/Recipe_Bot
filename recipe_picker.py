import pandas as pd
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
import json
import random
import gspread

variant_dict = {
"курица": ["курица", "кура", "куриное филе"],
"подмидор": ["помидор", "помидоры", "томат", "томаты", "помидор черри", "черри", "помидоры черри"],
"кабачок": ["цукини"], "болгарский перец": ["сладкий перец", "красный перец", "желтый перец"],
"картошка": ["картофель"], "морковь" : ["морковка"]
}

def string_to_pretty_list(mystring):
  mylist = []
  mystring = mystring.split(",")
  for a in mystring:
    mylist.append(a.strip())
  return mylist

database = pd.read_excel("Recipe_Database.xlsx")
datadic = pd.Series(database.Ingredients.values,index=database.DishName).to_dict()

for i in datadic.keys():
  datadic[i] = string_to_pretty_list(datadic[i])

#user_ingreds = input("What do you have? Enter ingredients:")
user_ingreds = "макароны, томаты, морковка, цукини"
user_ingreds_list = string_to_pretty_list(user_ingreds)



"""matches = []
for i in datadic.items():
  for n in i[1]:
    if n in normalized_user_ingreds_list:
      matches.append(i[0])
    
matchdict = Counter(matches) #turns matches into a dict of the shape: INGRED LIST: TIMES MATCHED
best_dish_names = [key for key, value in matchdict.items() if value == max(matchdict.values())]
#print(best_dish_names)

output_dict = {}
for dish in best_dish_names:
  ingredients = datadic[dish]
  ntb = []
  for ingred in ingredients:
    if ingred not in normalized_user_ingreds_list:
      ntb.append(ingred)
  output_dict[dish] = {"ingreds":ingredients, "to_buy":ntb, "recipe": "Рецепт: Здесь скоро будет рецепт"}

#print(output_dict.items())
output = []
for item in output_dict.items():
  dish_name = item[0]
  ingreds = ",".join(item[1]["ingreds"])
  to_buy = ",".join(item[1]["to_buy"])
  recipe = item[1]["recipe"]
  recipe_text = f"*{dish_name}*\n{ingreds}\n{to_buy}\n_{recipe}_\n"
  output.append(recipe_text)
text = "\n".join(output)
print(text)

"""







