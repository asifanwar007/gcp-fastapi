from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import starlette.status as status
import datetime
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './assignment-0001-419218-11f2874ba986.json'

app = FastAPI()

firestore_db = firestore.Client()


firebase_request_adapter = requests.Request()


templates = Jinja2Templates(directory="templates")

async def getAllRoomsIds():
    room_ref = firestore_db.collection('rooms') # .document(time_id).get()
    room_docs = room_ref.list_documents()
    
    room_ids = []
    for doc in room_docs:
        room_ids.append(doc.id)
    return room_ids

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Function that handles rendering the main page of the app"""
    user_token = "test"
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, "date":today_date})

@app.get("/allrooms", response_class=HTMLResponse)
async def root(request: Request):
    """Function that handles rendering the main page of the app"""
    user_token = "test"
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    allrooms= await getAllRoomsIds()
    return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, "date":today_date, 'all_rooms':allrooms})

@app.post("/add-room", response_class=HTMLResponse)
async def addRoom(request:Request):
    try:
        user_token = 'test'
        form = await request.form()
        room_id = form['room_id'].strip()
        if room_id == "":
            print("Room name is empty")
            return RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        room_name_ref = firestore_db.collection('rooms').where(filter=FieldFilter("room_id", "==", room_id)).get()
        if len(room_name_ref) != 0:
            for doc in room_name_ref:
                data = doc.to_dict()
                room_name = data.get('room_id')
            room_info = f'''<p id="error-red">Rooma already added: {room_id}</p>'''
            return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, 'room_info': room_info})
        data = {
            'room_id' : room_id,
            'createdAt' : datetime.datetime.now(),
        }
        rooms_ref = firestore_db.collection('rooms').document(room_id)
        rooms_ref.set(data)
        room_info = f'''<p id="success-green">Room added, !!Hurray <br> Room Name: {data['room_id']}</p>'''
        # return RedirectResponse('/', status_code=status.HTTP_302_FOUND)
        
        return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, 'room_info': room_info})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

@app.post("/delete-room", response_class=HTMLResponse)
async def deleteRoom(request:Request):
    try:
        user_token = 'test'
        form = await request.form()
        room_id = form['room_id'].strip()
        if room_id == "":
            print("Room name is empty")
            return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

        room_name_exist = firestore_db.collection('rooms').where(filter=FieldFilter("room_id", "==", room_id)).get()
        room_ref_to = firestore_db.collection('rooms').document(room_id).get()
        if not room_ref_to.exists:
            delete_info = f'''<p id="error-red">Room doesn't exit</p>'''
            return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, 'delete_info': delete_info})
            
        firestore_db.collection('rooms').document(room_id).delete()
        delete_info =  f'''<p id="success-green">{room_id} has been deleted'''
        return templates.TemplateResponse("main.html", context={'request': request, 'user_token': user_token, 'delete_info': delete_info})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

if __name__ == "__main__":
    import uvicorn
    try:
       uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(e)