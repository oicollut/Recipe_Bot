import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove
import pandas as pd
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from funcs import string_to_pretty_list, assmeble_recipe_suggestion_messages, find_dish_score, get_entry_by_dish_name

user_ingreds_list = []

f = open("keys.json")
keys = json.load(f)

token = keys["bot_key"]
bot = telebot.TeleBot(token)

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("api_key.json", scope)
client = gspread.authorize(credentials)

SHEET_ID = '1gAHh4nmX4uBNIRENbbqVObd9brk1eLD1VlW5kEnRoUY'
SHEET_NAME = 'Sheet1'
spreadsheet = client.open_by_key(SHEET_ID)
worksheet = spreadsheet.worksheet(SHEET_NAME)
db = worksheet.get_all_records()


output_dict = {}
variant_dict = {
"курица": ["курица", "кура", "куриное филе"],
"подмидор": ["помидор", "помидоры", "томат", "томаты", "помидор черри", "черри", "помидоры черри"],
"кабачок": ["цукини"], "болгарский перец": ["сладкий перец", "красный перец", "желтый перец"],
"картошка": ["картофель"], "морковь" : ["морковка"], "горошек" : ["горох"]
}

@bot.message_handler(commands=['start'])
def start_handler(message):
    output_dict.clear()
    text = "Привет! Добро пожаловать в бот кулинарного вдохновения.\n\n*Команды*:\n /recipe - подобрать лучшие рецепты под имеющиеся продукты\n/random - рандомный рецепт"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    #bot.register_next_step_handler(sent_msg, provide_recipe)
@bot.message_handler(commands=['random'])
def random_recipe(message):
    key, value = random.choice(list(db.items()))
    randtext = f"*{value}*\n\nИнгредиенты: {key}"
    bot.send_message(message.chat.id, randtext, reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['recipe'])
def recipe(message):
    output_dict.clear()
    sent_msg = bot.send_message(message.chat.id, "Какие продукты есть дома? Перечисли через запятую.\n*Напрмер:* _макароны, зеленый лук, болгарский перец, брынза_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent_msg, handleIngridients)

def handleIngridients(message):
    user_ingreds_list = string_to_pretty_list(message.text)
    scored_dishes = find_dish_score(db, user_ingreds_list)
    suggested_recipes = assmeble_recipe_suggestion_messages(scored_dishes, user_ingreds_list, db)

    output = []
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for suggestion in suggested_recipes:
        already_have = []
        dish_name =suggestion["DishName"]
        for ingred in user_ingreds_list:
           if ingred in suggestion["Ingredients"]:
              already_have.append(ingred)
        already_have = ", ".join(already_have)
        to_buy = ", ".join(suggestion["Shopping_list"])
        recipe_text = f"*{dish_name}*\n_Уже есть:_ {already_have}\n_Осталось купить:_ {to_buy}\n\n"
        output.append(recipe_text)
        itembtn = types.KeyboardButton(f'{dish_name}')
        markup.add(itembtn)
    markup.add(types.KeyboardButton("Выйти"))
    text = "\n".join(output)
    if len(suggested_recipes) > 0:
      bot.send_message(message.chat.id, text, parse_mode="Markdown")
      sent_msg = bot.send_message(message.chat.id, "Нажми на кнопку, чтобы посмотреть полный рецепт:", reply_markup=markup)
    else:
      sent_msg = bot.send_message(message.chat.id, f"Не нашлось рецептов с ингредиентами: {message.text}", parse_mode="Markdown")

    bot.register_next_step_handler(sent_msg, expand_recipe, suggested_recipes)
      
def expand_recipe(message, suggested_recipes):
  buttons = []
  if message.text == "Выйти":
    text = "До свидания!\n\nНачать заново:\n /recipe - подобрать лучшие рецепты под имеющиеся продукты\n/random - рандомный рецепт"
    bot.send_message(message.chat.id, text, reply_markup=ReplyKeyboardRemove())
    return
  
  for recipe in suggested_recipes:
      if message.text in recipe["DishName"]:
          buttons.append(recipe["DishName"])

  if message.text not in buttons and message.text != "Выйти":
        bot.send_message(message.chat.id, "Not a valid response", parse_mode="Markdown")
  else:
    for recipe in suggested_recipes:
      if message.text in recipe["DishName"]:
        if len(recipe["Shopping_list"]) > 1:
          recipe_text = f"*{recipe['DishName']}*\nОсталось купить: {recipe['Shopping_list']}\nИнгредиенты: {recipe['Ingredients']}\n\nРецепт: {recipe['Recipe']}"
        else: recipe_text = f"*{recipe['DishName']}*\nИнгредиенты: {recipe['Ingredients']}\n\nРецепт: {recipe['Recipe']}"
        
        bot.send_message(message.chat.id, recipe_text, parse_mode="Markdown")

  bot.register_next_step_handler(message, expand_recipe, suggested_recipes)

print("Bot running!")
#print(datadic)
bot.infinity_polling()

#class Struct(object): pass

#testData = Struct()
#testData.text = "болгарский перец, помидоры, рис, макароны"

#handleIngridients(testData)