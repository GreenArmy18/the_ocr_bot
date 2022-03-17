from ocrbot.helpers.decorators import send_typing_action
from telegram import Update
from telegram.ext import CallbackContext
from ocrbot.config import API_KEY
from datetime import timedelta, date, datetime
import re
import requests
from PIL import Image
import numpy as np
from io import BytesIO
#from datetime import timedelta, datetime

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def calculate(data_list):
    print(data_list)
    start_hour,end_hour=[],[]
    for i in range(len(data_list)):
        if i%2:
            end_hour.append(data_list[i])
        else: start_hour.append(data_list[i])
    print(start_hour)
    print(end_hour)

    t1=timedelta(hours=1, milliseconds=0)
    t2=timedelta(hours=1, milliseconds=0)
    total_time=t1-t2

    for x in range(len(start_hour)):
        first_time=re.sub('[^0-9]', '', str(start_hour[x]))
        second_time=re.sub('[^0-9]', '', str(end_hour[x]))
        
        print(first_time,second_time)

        time1 = datetime.strptime(first_time,"%H%M") # convert string to time

        time2 = datetime.strptime(second_time,"%H%M")
        diff = time2 - time1
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

    print(total_hours_end, total_minutes_end, total_hours, total_minutes)
    return total_hours_end, total_minutes_end, total_hours, total_minutes

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
    hours=[]
    flag=False

    if file_path is not None:
        while flag==False:
                    response = requests.get(file_path)
        img = Image.open(BytesIO(response.content))
        image_file = BytesIO()
        img.save(image_file, format='JPEG')
        image_file.seek(0)  # important, set pointer to beginning after writing image
        files = {"document": image_file}
        headers = {"Authorization": "Token e2f347943462442cc768bd8ab9607149"}
        response = requests.post(url, files=files, headers=headers)
        response=response.json()
        size=len(response["document"]['inference']['pages'][0]['prediction']["wednesday_date"]["values"])
        print(size,'size')
        hours=[]

        hours_titles=['sunday_start_time','sunday_end_time','monday_start_time','monday_end_time','tuesday_start_time','tuesday_end_time','wednesday_start_time','wednesday_end_time']
        start_hour_titles=['sunday_start_time','monday_start_time','tuesday_start_time','wednesday_start_time']
        end_hour_titles=['sunday_end_time','monday_end_time','tuesday_end_time','wednesday_end_time']
        start_hour,end_hour=[],[]
        wed_size=len(response["document"]['inference']['prediction']['wednesday_date']["values"])
        print(wed_size,'wed_size')
        for hour in hours_titles:
            values_size=len(response["document"]['inference']['prediction'][hour]["values"])
            print(values_size,'values_size')
            
            if len(response["document"]['inference']['prediction']['wednesday_date']["values"])>1:
                    for value in range(values_size):
                        if response["document"]['inference']['prediction']["wednesday_date"]["values"][value]["content"]=='02':
                            #if response["document"]['inference']['prediction']["wednesday_date"]["values"][value]["content"]==today_date/yom_reviei:
                            if response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==1 or response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==1.0 or response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==0.99:
                                    hours.append(response["document"]['inference']['prediction'][hour]["values"][value]["content"])
                                    print(response["document"]['inference']['prediction'][hour]["values"][value]["content"])
            else:
                for value in range(values_size):
                    #if response["document"]['inference']['prediction']["wednesday_date"]["values"][value]["content"]==today_date/yom_reviei:
                    if response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==1 or response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==1.0 or response["document"]['inference']['prediction'][hour]["values"][value]["confidence"]==0.99:
                            hours.append(response["document"]['inference']['prediction'][hour]["values"][value]["content"])
                            

        print(hours,'hours')
        if len(hours)==8:
            flag=True
            total_hours_end, total_minutes_end, hours,minutes=calculate(hours)
                
            m.edit_text(text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')
            
    else:
        m.edit_text(text="⚠️Something went wrong, please try again later ⚠️")
    #else:
        #m.edit_text("Something went wrong, Send this image again")


