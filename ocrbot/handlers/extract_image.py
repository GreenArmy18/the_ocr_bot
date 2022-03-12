from ocrbot.helpers.decorators import send_typing_action
from ocrbot.helpers.mock_database import insert_file_path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import requests
from ocrbot.config import API_KEY

@send_typing_action
def extract_image(update:Update,context:CallbackContext):
    '''
    This function is called when the user sends a photo.
    '''
    chat_id=update.effective_chat.id
    file_id = update.message.photo[-1].file_id
    newFile=context.bot.get_file(file_id)
    file_path= newFile.file_path
    data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={file_path}&language=eng&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
    print(data, "data")
    data=data.json()
    print(data, "json")
    print (file_path,'extract')
    keyboard = [[InlineKeyboardButton("English ", callback_data='eng'), InlineKeyboardButton("Russian", callback_data='rus'),InlineKeyboardButton("Czech", callback_data='cze')],
                [InlineKeyboardButton("Chinese simplified", callback_data='chs'), InlineKeyboardButton("Chinese Traditional", callback_data='cht')],[InlineKeyboardButton("Japanese", callback_data='jpn')] ,
                [InlineKeyboardButton("Arabic", callback_data='ara'),InlineKeyboardButton("Afrikans", callback_data='AFR'), InlineKeyboardButton("German", callback_data='gre')],
                [InlineKeyboardButton("Italian", callback_data='ita'),InlineKeyboardButton("Indonesian", callback_data='eng'),InlineKeyboardButton("French", callback_data='fre')],
                [InlineKeyboardButton ("Spanish", callback_data='spa'),InlineKeyboardButton("Portuguese", callback_data='por'),InlineKeyboardButton("Korean", callback_data='kor')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    m = update.message.reply_text('Select Language : ', reply_markup=reply_markup,quote=True)
    insert_file_path(chat_id,m.message_id,file_path)
