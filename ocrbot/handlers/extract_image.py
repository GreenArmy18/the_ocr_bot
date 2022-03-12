from ocrbot.helpers.decorators import send_typing_action
from ocrbot.helpers.mock_database import insert_file_path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from datetime import timedelta, date
import re
from ocrbot.helpers.mock_database import get_file_path
import requests
from ocrbot.config import API_KEY

#@send_typing_action
def extract_image(update:Update,context:CallbackContext):
    '''
    This function is called when the user sends a photo.
    '''
    chat_id=update.effective_chat.id
    file_id = update.message.photo[-1].file_id
    newFile=context.bot.get_file(file_id)
    file_path= newFile.file_path

    #keyboard = [[InlineKeyboardButton("English ", callback_data='eng'), InlineKeyboardButton("Russian", callback_data='rus'),InlineKeyboardButton("Czech", callback_data='cze')],
    #            [InlineKeyboardButton("Chinese simplified", callback_data='chs'), InlineKeyboardButton("Chinese Traditional", callback_data='cht')],[InlineKeyboardButton("Japanese", callback_data='jpn')] ,
    #            [InlineKeyboardButton("Arabic", callback_data='ara'),InlineKeyboardButton("Afrikans", callback_data='AFR'), InlineKeyboardButton("German", callback_data='gre')],
    #            [InlineKeyboardButton("Italian", callback_data='ita'),InlineKeyboardButton("Indonesian", callback_data='eng'),InlineKeyboardButton("French", callback_data='fre')],
    #            [InlineKeyboardButton ("Spanish", callback_data='spa'),InlineKeyboardButton("Portuguese", callback_data='por'),InlineKeyboardButton("Korean", callback_data='kor')]]
    #reply_markup = InlineKeyboardMarkup(keyboard)

    #m = update.message.reply_text('Select Language : ', reply_markup=reply_markup,quote=True)
    insert_file_path(chat_id,file_path)

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

d = date.today() + timedelta(days=1)
next_thursday = next_weekday(d, 3) # 0 = Monday, 1=Tuesday, 2=Wednesday...
tommorw_date=next_thursday.strftime("%d/%m/%y")

#@send_typing_action
def button_click(update:Update,context:CallbackContext):
    '''
    This function is called when the user clicks on the buttons.
    '''
    query = update.callback_query
    query.answer()
    filepath=get_file_path(query.message.chat_id)
    if filepath is not None:
        #query.edit_message_text("Extracting text please wait ...")
        query.edit_message_text("מנתח תמונה, רק רגע...")
        data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={filepath}&language=eng&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
        data=data.json()
        
        if data['IsErroredOnProcessing']==False:
            message=data['ParsedResults'][0]['ParsedText']
            total_hours_end, total_minutes_end, hours,minutes=calculate(message.splitlines())
            query.edit_message_text(text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')

        else:
            query.edit_message_text(text="⚠️Something went wrong, please try again later ⚠️")
    else:
        query.edit_message_text("Something went wrong, Send this image again")


def calculate(data_list):
    t1=timedelta(hours=1, milliseconds=0)
    t2=timedelta(hours=1, milliseconds=0)
    total_time=t1-t2

    hours=[]

    for x in range(1,5):
        str1 = ''.join(str(e) for e in data_list[x-1])

        pos_flags=[i for i, letter in enumerate(str1) if letter == ':']

        for i in range (2):
            hours.append((str1[pos_flags[i]-2:pos_flags[i]+3]).split(" "))

    from datetime import datetime

    for x in range(1,5):
        first_time=re.sub('[^0-9]', '', str(hours[x*2-2]))
        second_time=re.sub('[^0-9]', '', str(hours[x+x-1]))

        time1 = datetime.strptime(first_time,"%H%M") # convert string to time

        time2 = datetime.strptime(second_time,"%H%M")
        diff = time1 - time2
        total_time+=(diff)

    test=total_time
    test = '%02d:%02d:%02d.%06d' % (test.days*24 + test.seconds // 3600, (test.seconds % 3600) // 60, test.seconds % 60, test.microseconds)

    total_hours_end=(str(test)[:-3].split(":"))[0]
    total_minutes_end=(str(test)[:-3].split(":"))[1]
    if total_minutes_end[0]=='0': total_minutes_end=total_minutes_end[1]
    total=timedelta(hours=29, microseconds=0)-total_time

    total_hours=(str(total)[:-3].split(":"))[0]
    total_minutes=(str(total)[:-3].split(":"))[1]
    
    if total_minutes[:-1]=='0':
        total_minutes=total_minutes[1:]

    return total_hours_end, total_minutes_end, total_hours, total_minutes
