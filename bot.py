import json

async def on_fetch(request, env):
    if request.method == "POST":
        try:
            # Читаем сообщение от Telegram
            data = await request.json()
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')

            # Отправляем ответ напрямую через API Telegram
            url = f"https://api.telegram.org/bot{env.BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"Бот на Cloudflare работает! Вы написали: {text}"
            }
            
            # Делаем запрос к Telegram
            await fetch(url, method="POST", body=json.dumps(payload), headers={"Content-Type": "application/json"})
            
            return Response.new("ok", status=200)
        except Exception as e:
            return Response.new(str(e), status=200)

    return Response.new("Бот онлайн и ждет сообщений!", status=200)
