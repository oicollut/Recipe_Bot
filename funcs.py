
def string_to_pretty_list(mystring):
      mylist = []
      mystring = mystring.split(",")
      for a in mystring:
        mylist.append(a.strip())
      return mylist

def get_entry_by_dish_name(dish_name, data_dict):
    for entry in data_dict:
        if entry['DishName'].lower() == dish_name.lower(): 
            return entry
    return None

def find_need_to_buy_for_matched_dishes(entry, user_ingreds_list):#returns list of need_to_buys (shopping list) 
    ntb = []                                                      #executed in fins dish score (lenght used)
    ingredients = entry['Ingredients']                            #and assmeble_recipe_suggestion_messages (used as list)
    for ingred in string_to_pretty_list(ingredients):
      if ingred not in user_ingreds_list:
        ntb.append(ingred)

    return ntb
        

def find_dish_score(db, user_ingreds_list):

    #print(datadic)
    matches = {}
    for entry in db:
        for ingred in string_to_pretty_list(entry["Ingredients"]):
            if ingred in user_ingreds_list:
                if entry["DishName"] in matches:
                     matches[entry["DishName"]] += 1
                else: matches[entry["DishName"]] = 1
        if entry["DishName"] in matches:
          ntb = find_need_to_buy_for_matched_dishes(entry, user_ingreds_list) 
          matches[entry["DishName"]] = matches[entry["DishName"]] - len(ntb)
    
    matches = sorted(matches.items(), key=lambda x: x[1], reverse = True)
    matches = dict(matches)
    print(matches)

    return matches


def assmeble_recipe_suggestion_messages(matches, user_ingreds_list, db):
      
      suggestion_message_dict = {}
      suggested_recipes = []
      for match in matches.keys():
         suggestion_message_dict = {}
         entry = get_entry_by_dish_name(match, db)
         suggestion_message_dict["DishName"] = entry["DishName"]
         suggestion_message_dict["Shopping_list"] = find_need_to_buy_for_matched_dishes(entry, user_ingreds_list)
         suggestion_message_dict["Ingredients"] = entry["Ingredients"]
         suggestion_message_dict["Recipe"] = entry["Recipe"]
         suggested_recipes.append(suggestion_message_dict)
    
      return suggested_recipes
