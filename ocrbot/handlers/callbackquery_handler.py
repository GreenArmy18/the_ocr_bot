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
            print(calculate(message.splitlines()))
            query.edit_message_text(f"{message}")
        else:
            query.edit_message_text(text="⚠️Something went wrong, please try again later ⚠️")
    else:
        query.edit_message_text("Something went wrong, Send this image again")


def calculate(data_list):
    hours=[]

    for x in range(1,5):
        str1 = ''.join(str(e) for e in data_list[x-1])

        pos_flags=[i for i, letter in enumerate(str1) if letter == ':']

        for i in range (2):
            hours.append((str1[pos_flags[i]-2:pos_flags[i]+3]).split(" "))
    print(hours)
    from datetime import datetime

    for x in range(1,5):
        first_time=re.sub('[^0-9]', '', str(hours[x*2-2]))
        second_time=re.sub('[^0-9]', '', str(hours[x+x-1]))

        time1 = datetime.strptime(first_time,"%H%M") # convert string to time
        #print(time1)

        time2 = datetime.strptime(second_time,"%H%M")
        #print(time2)
        diff = time1 - time2
        total_time+=(diff)

    test=total_time
    test = '%02d:%02d:%02d.%06d' % (test.days*24 + test.seconds // 3600, (test.seconds % 3600) // 60, test.seconds % 60, test.microseconds)
    print(test)

    #print(total_time-timedelta(hours=0, microseconds=0), "total time")
    total_hours_end=(str(test)[:-3].split(":"))[0]
    #print(total_hours_end)
    #print(((total_time)[:-3].split(":")).hour)
    total_minutes_end=(str(test)[:-3].split(":"))[1]
    if total_minutes_end[0]=='0': total_minutes_end=total_minutes_end[1]
    total=timedelta(hours=29, microseconds=0)-total_time
    #print(total, "total")

    total_hours=(str(total)[:-3].split(":"))[0]
    total_minutes=(str(total)[:-3].split(":"))[1]
    
    #print(total_hours, "hours")
    #print(total_minutes, "minutes")
    if total_minutes[:-1]=='0':
        total_minutes=total_minutes[1:]

    main_title="שבוע טוב, אימא\nמחר, יום חמישי, תצטרכי לעבוד"
    hours_title="שעות"
    link_mark="ו־"
    minutes_title="דקות."
    end_title="\nשיהיה לך המשך שבוע נפלא :)"
    #print(main_title, total_hours, hours_title, link_mark, total_minutes, minutes_title, end_title)
    print(total_hours_end, total_minutes_end, total_hours, total_minutes)
    return total_hours_end, total_minutes_end, total_hours, total_minutes
