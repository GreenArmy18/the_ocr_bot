from ocrbot.helpers.decorators import send_typing_action
from telegram import Update
from telegram.ext import CallbackContext
from ocrbot.config import API_KEY
from datetime import timedelta, date
import re
import requests
from PIL import Image
import numpy as np
from io import BytesIO

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

@send_typing_action
def extract_image(update:Update,context:CallbackContext):
    '''
    This function is called when the user sends a photo.
    '''
    chat_id=update.effective_chat.id
    file_id = update.message.photo[-1].file_id
    print(file_id,'file_id')
    newFile=context.bot.get_file(file_id)
    print(newFile,'newFile')
    file_path= newFile.file_path
    print(file_path,'file_path')
    m = update.message.reply_text('מנתח תמונה, רק רגע...',quote=True)
    
    print(update.message.photo[-1].height,update.message.photo[-1].width)

    d = date.today() + timedelta(days=1)
    today=date.today()
    next_thursday = next_weekday(d, 3) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    tommorw_date=next_thursday.strftime("%d/%m/%y")
    url = "https://api.mindee.net/v1/products/GreenArmy/screenshot/v1/predict"
    if file_path is not None:
        files = {"document": file_path}
        headers = {"Authorization": "Token e2f347943462442cc768bd8ab9607149"}
        response = requests.post(url, files=files, headers=headers)
        response=response.json()
        print(response)
        print(response["document"]['inference']['pages'][0]['prediction']["sunday_date"]["values"][0]["content"])        
        #total_hours_end, total_minutes_end, hours,minutes=calculate(message.splitlines())
           
        #m.edit_text(text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')
            
        #else:
        #    m.edit_text(text="⚠️Something went wrong, please try again later ⚠️")
    else:
        m.edit_text("Something went wrong, Send this image again")


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
