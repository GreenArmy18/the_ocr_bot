from ocrbot.helpers.decorators import send_typing_action
from telegram import Update
from telegram.ext import CallbackContext
from ocrbot.config import API_KEY
from datetime import timedelta, date
import re
import requests
from PIL import Image
#import cv2
#from matplotlib import cm
import numpy as np
#import urllib
from io import BytesIO
from collections import deque

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def colors_roughly_equal(color1, color2, threshold=5):
    return np.all(np.abs(color1 - color2) <= threshold)


def dfs_inplace(matrix, color, i, j):
    h, w = matrix.shape[0:2]
    queue = deque([(i, j)])
    while len(queue):
        i, j = queue.popleft()
        if matrix[i, j, -1] == 0 or not colors_roughly_equal(matrix[i, j], color):
            continue
        else:
            matrix[i, j, -1] = 0
        queue.append((min(i + 1, h - 1), j))
        queue.append((max(0, i - 1), j))
        queue.append((i, min(j + 1, w - 1)))
        queue.append((i, max(j - 1, 0)))


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
    
    d = date.today() + timedelta(days=1)
    today=date.today()
    next_thursday = next_weekday(d, 3) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    tommorw_date=next_thursday.strftime("%d/%m/%y")
    
    position=0

    if file_path is not None:
        data=requests.get(f"https://api.ocr.space/parse/imageurl?apikey={API_KEY}&url={file_path}&language=eng&detectOrientation=True&filetype=JPG&OCREngine=1&isTable=True&scale=True")
        data=data.json()
        print(data, "data")
        
        if data['IsErroredOnProcessing']==False:
            size=len(data['ParsedResults'][0]['TextOverlay']['Lines'])
            for x in range(size):
            #if data['ParsedResults'][0]['TextOverlay']['Lines'][x]['Words'][0]['WordText']==today:
            #if data['ParsedResults'][0]['TextOverlay']['Lines'][x]['Words'][0]['WordText']==30:
                l,t= data['ParsedResults'][0]['TextOverlay']['Lines'][x]['Words'][0]['Left'], data['ParsedResults'][0]['TextOverlay']['Lines'][x]['Words'][0]['Top']
            
            #l=391
            l+=45
            l-=300

            #t=1104
            t+=40
            t-=255

            left=l
            top=t
            height=300
            weight=245

            x=left
            y=top
            h=weight
            w=height
            
            #req = urllib.urlopen(file_path)
            #arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            #img = cv2.imdecode(arr, -1) # 'Load it as it is'

            #cv2.imshow('lalala', img)
            #if cv2.waitKey() & 0xff == 27: quit()
            response = requests.get(file_path)
            print(response.content, 'ccc')
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGBA')
            pixels = np.array(img)
            bg_value = np.copy(pixels[0, 0]).astype('int32')
            h, w = pixels.shape[0:2]
            print("starting dfs")
            dfs_inplace(pixels, bg_value, 0, 0)
            if pixels[-1, -1, -1] != 0:
                dfs_inplace(pixels, bg_value, h - 1, w - 1)

            img = Image.fromarray(pixels)
            while max(img.size) <= 512:
                img = img.resize([2 * x for x in img.size])
            img.thumbnail((512, 512), Image.ANTIALIAS)  # inplace

            image_file = BytesIO()
            img.save(image_file, format='PNG', quality=95)
            image_file.seek(0)  # important, set pointer to beginning after writing image
            print("ready to send")
            m.edit_media(media=img)

            #crop_img = img[y:y+h, x:x+w]

            #PIL_image = Image.fromarray(crop_img.astype('uint8'), 'RGB')

            #bio = BytesIO()
            #bio.name = 'image.jpeg'
            #PIL_image.save(bio, 'JPEG')
            #bio.seek(0)
            #m.edit_media(chat_id, photo=bio)

            #message=data['ParsedResults'][0]['ParsedText']
            #total_hours_end, total_minutes_end, hours,minutes=calculate(message.splitlines())
            #m.edit_text(text='שבוע טוב, אימא\n''השבוע עבדת '+total_hours_end+' שעות ו־'+total_minutes_end+' דקות.\n''ביום חמישי הקרוב – '+tommorw_date+', תצטרכי לעבוד ' +hours+ ' שעות ו־' +minutes+ ' דקות כדי להגיע למכסת 29 השעות השבועיות.\nשיהיה לך המשך שבוע נפלא :)')

        else:
            m.edit_text(text="⚠️Something went wrong, please try again later ⚠️")
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
