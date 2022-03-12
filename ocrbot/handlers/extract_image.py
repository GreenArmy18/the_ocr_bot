from ocrbot.helpers.decorators import send_typing_action
from ocrbot.helpers.mock_database import insert_file_path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

@send_typing_action
def extract_image(update:Update,context:CallbackContext):
    '''
    This function is called when the user sends a photo.
    '''
    chat_id=update.effective_chat.id
    file_id = update.message.photo[-1].file_id
    newFile=context.bot.get_file(file_id)
    file_path= newFile.file_path

    keyboard = [[InlineKeyboardButton("נתח ", callback_data='eng')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    m = update.message.reply_text('מנתח תמונה, רק רגע...',quote=True)
    insert_file_path(chat_id,m.message_id,file_path)