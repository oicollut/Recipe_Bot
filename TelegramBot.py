import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove
import pandas as pd
from collections import Counter
import random


bot = telebot.TeleBot(BOT_TOKEN)
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
    database = pd.read_excel("Recipe_Database.xlsx")
    datadic = pd.Series(database.DishName.values,index=database.Ingredients).to_dict()
    key, value = random.choice(list(datadic.items()))
    randtext = f"*{value}*\n\nИнгредиенты: {key}"
    bot.send_message(message.chat.id, randtext, reply_markup=ReplyKeyboardRemove())
  
@bot.message_handler(commands=['recipe'])
def recipe(message):
    output_dict.clear()
    sent_msg = bot.send_message(message.chat.id, "Какие продукты есть дома? Перечисли через запятую.\n*Напрмер:* _макароны, зеленый лук, болгарский перец, брынза_", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(sent_msg, provide_recipe)
def provide_recipe(message):
    import pandas as pd
    from collections import Counter
    output_dict.clear()
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

    user_ingreds_list = string_to_pretty_list(message.text)

    #print(datadic)
    matches = []
    for i in datadic.items():
      for n in i[1]:
        if n in user_ingreds_list:
          matches.append(i[0])
    
    if len(matches) > 0:
      matchdict = Counter(matches) #turns matches into a dict of the shape: DISH: TIMES MATCHED
      best_dish_names = [key for key, value in matchdict.items() if value == max(matchdict.values())]
      #print(best_dish_names)
    
      for dish in best_dish_names:
        ingredients = datadic[dish]
        ntb = []
        for ingred in ingredients:
          if ingred not in user_ingreds_list:
            ntb.append(ingred)
        output_dict[dish] = {"ingreds":ingredients, "to_buy":ntb, "recipe": "Рецепт: Здесь скоро будет рецепт"}

      #print(output_dict.items())
      output = []
      markup = types.ReplyKeyboardMarkup(row_width=2)
      for item in output_dict.items():
        dish_name = item[0]
        to_buy = ", ".join(item[1]["to_buy"])
        recipe_text = f"*{dish_name}*\n\nОсталось купить: {to_buy}\n\n"
        output.append(recipe_text)
        itembtn = types.KeyboardButton(f'{dish_name}')
        markup.add(itembtn)
      markup.add(types.KeyboardButton("Выйти"))
      text = "\n".join(output)
      bot.send_message(message.chat.id, text, parse_mode="Markdown")
      bot.send_message(message.chat.id, "Нажми на кнопку, чтобы посмотреть полный рецепт:", reply_markup=markup)
    else:
      bot.send_message(message.chat.id, f"Не нашлось рецептов с ингредиентами: {message.text}", parse_mode="Markdown")

@bot.message_handler()
def expand_recipe(message):
  output = []
  if message.text == "Выйти":
    text = "До свидания!\n\nНачать заново:\n /recipe - подобрать лучшие рецепты под имеющиеся продукты\n/random - рандомный рецепт"
    bot.send_message(message.chat.id, text, reply_markup=ReplyKeyboardRemove())
  if message.text in output_dict.keys():
    dish_name = message.text
    ingreds = ", ".join(output_dict[message.text]["ingreds"])
    to_buy = ", ".join(output_dict[message.text]["to_buy"])
    recipe = output_dict[message.text]["recipe"]
    recipe_text = f"*{dish_name}*\nОсталось купить: {to_buy}\nИнгредиенты: {ingreds}\n\nРецепт: {recipe}"
    output.append(recipe_text)
    text = "".join(output)
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
  elif message.text not in output_dict.keys() and message.text != "Выйти":
    bot.send_message(message.chat.id, "Not a valid response", parse_mode="Markdown")

  #bot.register_next_step_handler(sent_msg, expand_recipe)
print("Bot running!")
bot.infinity_polling()

