import json
from js import Response, fetch

async def on_fetch(request, env):
    if request.method == "POST":
        try:
            data = await request.json()
            if "message" in data:
                chat_id = data['message']['chat']['id']
                text = data['message'].get('text', 'Без текста')

                token = "8783400059:AAGKuUHfxkE4mMKlTGMKsVmgQcGjGQ4CNdk"
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                
                payload = {
                    "chat_id": chat_id,
                    "text": f"Бот на Cloudflare работает! Ты написал: {text}"
                }

                # Отправка через встроенный fetch
                await fetch(url, method="POST", 
                            body=json.dumps(payload), 
                            headers={"Content-Type": "application/json"})
            
            return Response.new("ok")
        except Exception as e:
            return Response.new(str(e))

    return Response.new("Бот успешно запущен!")
