from fastapi import FastAPI
from fastapi_socketio import SocketManager
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

class Data:
    data = {
        'calisan': ['Ahmet Yilmaz', 'Can Erturk', 'Hasan Korkmaz', 'Cenk Saymaz', 'Ali Turan', 'Riza Erturk', 'Mustafa Can'],
        'Departman': ['Insan Kaynaklari', 'Bilgi Islem', 'Muhasebe', 'Insan Kaynaklari', 'Bilgi Islem', 'Muhasebe', 'Bilgi Islem'],
        'Yas': [30, 25, 45, 50, 23, 34, 42],
        'Semt': ['Kadikoy', 'Tuzla', 'maltepede', 'Tuzla', 'Kadikoy', 'Tuzla', 'maltepede'],
        'Maas': [5000, 3000, 4000, 3500, 2750, 6500, 4500]
    }

app = FastAPI()
sio = SocketManager(app=app)

@app.get("/")
async def main():
    return {"message": "Hello World"}

@sio.on('join')
async def handle_join(sid, *args, **kwargs):
    print("Baglanti gerceklesti...")
    await sio.emit('lobby', 'User joined')

def process_data(result):
    result = result.to_json(orient='records')
    result = result.replace('[','').replace(']','').replace('"','').replace(',','\n')
    result = result.split('\n')
    return result

@sio.on('isim')
async def test(sid,*args, **kwargs):
    data = Data.data['calisan']
    await sio.emit('isim', [data])

@sio.on('maltepede')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df[df['Semt'] == 'maltepede']['calisan']
    result = process_data(result)
    await sio.emit('maltepede', result)

@sio.on('bilgi')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df[df['Departman'] == 'Bilgi Islem']['calisan']
    result = process_data(result)
    await sio.emit('bilgi', result)

@sio.on('genelMaaslar')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman')['Maas'].sum()
    result = process_data(result)
    await sio.emit('genelMaaslar', result)

@sio.on('ortalam_yaslar')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Departman')['Yas'].mean()
    result = process_data(result)
    await sio.emit('ortalam_yaslar', result)

@sio.on('minimum_yas')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    resultm = df.groupby('Departman').min()['Maas']
    resulty = df.groupby('Departman').min()['Yas']
    resultm = process_data(resultm)
    resulty = process_data(resulty)
    await sio.emit('minimum_yas', resulty)

@sio.on('calisan_sayi')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df.groupby('Semt')['calisan'].count()
    result = process_data(result)
    await sio.emit('calisan_sayi', result)

@sio.on('maltepe_calisan')
async def test(sid,*args, **kwargs):
    df = pd.DataFrame(Data.data)
    result = df[df['Semt'] == 'Kadikoy']['calisan'].count()
    result = str(result)
    await sio.emit('maltepe_calisan', result)

if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    
    import uvicorn

    uvicorn.run("server_kismi:app", host='localhost', port=8081, reload=True)
