from cgitb import text
import requests
from ocrbot.helpers.decorators import send_typing_action
from telegram import Update
from telegram.ext import CallbackContext
from ocrbot.helpers.mock_database import get_file_path
from ocrbot.config import API_KEY
from datetime import timedelta, date
import re



@send_typing_action
def button_click(update:Update,context:CallbackContext):
    '''
    This function is called when the user clicks on the buttons.
    '''
    query = update.callback_query
    query.answer()
    filepath=get_file_path(query.message.chat_id,query.message.message_id)
    if filepath is not None:
        query.edit_message_text("Extracting text please wait ...")
        data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={filepath}&language={query.data}&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
        data=data.json()
        
        if data['IsErroredOnProcessing']==False:
            message=data['ParsedResults'][0]['ParsedText']
            print(calculate(message.splitlines()),"final result")
            total_hours_end, total_minutes_end, hours,minutes=calculate(message.splitlines())
            #query.edit_message_text(f"{message}")
            #query.edit_message_text(f"{message}")
            tommorw_date=next_thursday.strftime("%d/%m/%y")
            context.bot.send_message(chat_id=update.message.chat_id, text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')

        else:
            query.edit_message_text(text="⚠️Something went wrong, please try again later ⚠️")
    else:
        query.edit_message_text("Something went wrong, Send this image again")

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

d = date.today() + timedelta(days=1)
next_thursday = next_weekday(d, 3) # 0 = Monday, 1=Tuesday, 2=Wednesday...

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
    print(hours,"hours")
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
    print(test,"test")

    total_hours_end=(str(test)[:-3].split(":"))[0]
    total_minutes_end=(str(test)[:-3].split(":"))[1]
    if total_minutes_end[0]=='0': total_minutes_end=total_minutes_end[1]
    total=timedelta(hours=29, microseconds=0)-total_time

    total_hours=(str(total)[:-3].split(":"))[0]
    total_minutes=(str(total)[:-3].split(":"))[1]
    
    if total_minutes[:-1]=='0':
        total_minutes=total_minutes[1:]

    #total_hours_end, total_minutes_end, hours,minutes = somefunction(f.read())
    #total_hours_end = '%02d:%02d:%02d.%06d' % (total_hours_end.days*24 + total_hours_end.seconds // 3600, (total_hours_end.seconds % 3600) // 60, total_hours_end.seconds % 60, total_hours_end.microseconds)

    print(total_hours_end, total_minutes_end)
    #tommorw_date=(date.today() + timedelta(days=1)).strftime("%d/%m/%y")
    tommorw_date=next_thursday.strftime("%d/%m/%y")
    #context.bot.send_message(chat_id=update.message.chat_id, text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')
    print('שבוע טוב, אימא\n''השבוע עבדת ',total_hours_end,' שעות ו־',total_minutes_end,' דקות.\n''ביום חמישי הקרוב – ',tommorw_date,', תצטרכי לעבוד ' ,total_hours, ' שעות ו',total_minutes,'־דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')
    text='שבוע טוב, אימא\n''השבוע עבדת ',total_hours_end,' שעות ו־',total_minutes_end,' דקות.\n''ביום חמישי הקרוב – ',tommorw_date,', תצטרכי לעבוד ' ,total_hours, ' שעות ו',total_minutes,'־דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)'
    #'שבוע טוב, אימא\n''השבוע עבדת ',total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +total_hours+ ' שעות ו־' +total_minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)'
    print(total_hours_end, total_minutes_end, total_hours, total_minutes,"my numbers")
    return total_hours_end, total_minutes_end, total_hours, total_minutes
    #return text
