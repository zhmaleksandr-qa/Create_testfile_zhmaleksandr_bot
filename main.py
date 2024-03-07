import os
import time
import telebot
from telebot import types

bot = telebot.TeleBot(token='', parse_mode='html')
formats = ['.jpg', '.png', '.svg', '.gif', '.ico', '.mp4', '.avi', '.webm', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.pdf', '.css', '.html', '.js', '.json', '.zip', '.rar']

bot.set_my_commands([types.BotCommand('/start', 'перезапуск бота')])

@bot.message_handler(commands=['start'])
def welcome(message):
	
	username = message.from_user.first_name
	
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add(*formats, row_width=4)

	reply = bot.send_message(message.chat.id, f"Привет, <b>{username}</b>! 👋🏻\nЯ персональный бот-генератор тестовых файлов. Помогу тебе проверить граничные значения при загрузке файлов разного веса в приложениях и на веб-сайтах. Задача моя генерировать файлы различных расширений размерами от 1 байта до 45 мегабайт включительно.\n\nЧтобы начать, выбери одно из доступных расширений в меню ниже ⬇️", reply_markup=markup)

	bot.register_next_step_handler(reply, check_format)

def check_format(message):
	if (message.text == 'Вернуться в начало' or message.text == '/start'):
	
		welcome(message)

	elif (message.text in formats):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add("B (байты)", "KB (килобайты)", "MB (мегабайты)", "Вернуться в начало")

		reply = bot.send_message(message.chat.id, f"🔹 Выбранное расширение — <b>{message.text}</b>\n\nТеперь выбери единицу измерения.\n<u>Небольшая памятка по размерам:</u>\n1 килобайт = 1 024 байта\n1 мегабайт = 1 024 килобайта = 1 048 576 байт", reply_markup=markup)

		
		bot.register_next_step_handler(reply, check_unit, message)

	else:
		
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add(*formats, row_width=5)
		markup.add("Вернуться в начало")

		reply = bot.send_message(message.chat.id, f"Выбрано неверное расширение файла, пожалуйста выбери одно из меню ниже 🙂⬇️", reply_markup=markup)

		bot.register_next_step_handler(reply, check_format)

def check_unit(message, format):
	if (message.text == 'Назад'):
		
		check_format(format)
	
	elif (message.text == 'Вернуться в начало' or message.text == '/start'):
		welcome(message)

	
	elif (message.text in ['B (байты)', 'KB (килобайты)', 'MB (мегабайты)']):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add('Назад', 'Вернуться в начало')
		
		reply = bot.send_message(message.chat.id, f"🔹 Выбранное расширение — <b>{format.text}</b>\n🔹 Единица измерения — <b>{message.text}</b>\n\nОстался последний шаг, напиши размер файла. Я принимаю только целые числа, без пробелов и прочих символов.\n⛔️ <u>Ограничения по размеру:</u>\n<b>Минимум</b> — 1 байт\n<b>Максимум</b> — 45 MB (это 46 080 KB или 47 185 920 байт)", reply_markup=markup)

		
		bot.register_next_step_handler(reply, check_size, format, message)
	
	else:
		
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add('B (байты)', 'KB (килобайты)', 'MB (мегабайты)', 'Вернуться в начало')

		reply = bot.send_message(message.chat.id, f"Неверная единица измерения. Пожалуйста, выбери одну из меню ниже 🙂", reply_markup=markup)
		
		bot.register_next_step_handler(reply, check_unit, format)

def check_size(message, format, unit):
	if (message.text == 'Назад'):
		
		check_format(format)

	elif (message.text == 'Вернуться в начало' or message.text == '/start'):
		welcome(message)

	elif (isinstance(message.text, type(None)) or not message.text.isdigit()):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.add('Назад', 'Вернуться в начало')
		
		reply = bot.send_message(message.chat.id, f"Неверный размер файла. Пожалуйста введи правильный, я принимаю только целые положительные числа, без пробелов и прочих символов 🙂", reply_markup=markup)

		bot.register_next_step_handler(reply, check_size, format, unit)

	else:
		size = int(message.text)

		if (unit.text == 'MB (мегабайты)'):
			size_bytes = size * 1024 * 1024
			unit_result_text = 'MB'
		elif (unit.text == 'KB (килобайты)'):
			size_bytes = size * 1024
			unit_result_text = 'KB'
		else:
			size_bytes = size
			unit_result_text = 'B'

		if (size_bytes < 1 or size_bytes > 47185920):
			reply = bot.send_message(message.chat.id, f"Размер файла выходит за границы моих возможностей.\n<u>Мои ограничения:</u>\n<b>Минимум</b> — 1 байт\n<b>Максимум</b> — 45 MB (это 46 080 KB или 47 185 920 байт)\n\nПожалуйста, введи подходящий размер 🙂")
			bot.register_next_step_handler(reply, check_size, format, unit)
		else:
			
			timestamp = int(time.time())
			filename = f'{timestamp}-{size_bytes}-bytes{format.text}'

			f = open(filename,"wb")
			random_bytes = os.urandom(size_bytes)
			f.write(random_bytes)
			f.close()
			
			
			if (unit_result_text == 'MB' or unit_result_text == 'KB'):
				size_format = '{0:,}'.format(size).replace(',', ' ')
				size_bytes_format = '{0:,}'.format(size_bytes).replace(',', ' ')
				caption = f'🙌🏻 Ура, твой тестовый файлик с расширением <b>{format.text}</b> успешно сгенерирован!\n\nЕго размер — <b>{size_format} {unit_result_text}</b>\nВ байтах — <b>{size_bytes_format} B</b>'
			else:
				size_bytes_format = '{0:,}'.format(size_bytes).replace(',', ' ')
				caption = f'🙌🏻 Ура, твой тестовый файлик с расширением <b>{format.text}</b> успешно сгенерирован!\n\nЕго размер — <b>{size_bytes_format} {unit_result_text}</b>'

			
			f = open(filename,"rb")
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
			markup.add('Вернуться в начало')
			reply = bot.send_document(message.chat.id, f, caption=caption, reply_markup=markup)

			f.close()
			os.unlink(filename)
			bot.register_next_step_handler(reply, welcome)

def main():
	bot.infinity_polling()

if __name__ == '__main__':
	main()
