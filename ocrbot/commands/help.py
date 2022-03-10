from telegram import Update
from telegram.ext import CallbackContext
from ocrbot.helpers.decorators import send_typing_action

@send_typing_action
def help(update:Update,context:CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "List of commands available:\
        \n/start - To start the bot\
        \n/help - To show this message",quote=True
    )

@send_typing_action
def helping(update:Update,context:CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
            'כדאי שתתקשרי לאופק, הוא כבר ידע לעזור לך.\n או שפשוט תשלחי לו הודעה: https://t.me/The_Horizon18',quote=True
    )