import json
import io
from js import Response, fetch
from PIL import Image

async def on_fetch(request, env):
    if request.method == "POST":
        try:
            data = await request.json()
            if "message" in data and "photo" in data["message"]:
                chat_id = data['message']['chat']['id']
                # Берем самую большую версию фото
                file_id = data["message"]["photo"][-1]["file_id"]
                
                # 1. Получаем путь к файлу от Telegram
                file_info = await fetch(f"https://api.telegram.org/bot{env.BOT_TOKEN}/getFile?file_id={file_id}")
                file_data = await file_info.json()
                file_path = file_data["result"]["file_path"]
                
                # 2. Скачиваем фото
                img_res = await fetch(f"https://api.telegram.org/file/bot{env.BOT_TOKEN}/{file_path}")
                img_bytes = await img_res.arrayBuffer()
                
                # 3. Обработка (Логика из твоего collage_maker.py)
                img = Image.open(io.BytesIO(img_bytes.to_py()))
                # ТУТ ТВОИ ПРЕОБРАЗОВАНИЯ (например, ресайз или фильтр)
                img = img.rotate(90) # Пример
                
                # 4. Отправка обратно
                out_io = io.BytesIO()
                img.save(out_io, format="PNG")
                # ... код отправки файла в Telegram ...

            return Response.new("ok")
        except Exception as e:
            return Response.new(str(e))
    return Response.new("Бот готов к созданию коллажей!")
