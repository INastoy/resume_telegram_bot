from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

resume_button = InlineKeyboardButton(text='Резюме', callback_data='get_resume')
parser_button = InlineKeyboardButton(text='Трекер цен Ситилинк', callback_data='get_tracker')
project_button = InlineKeyboardButton(text='Проект на джанго', callback_data='get_project')

main_menu = InlineKeyboardMarkup(row_width=2).add(resume_button, parser_button, project_button)
