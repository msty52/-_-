export default {
  async fetch(request, env) {
    // Обрабатываем только POST-запросы (сообщения от Telegram)
    if (request.method === "POST") {
      try {
        const data = await request.json();
        
        // Проверяем, есть ли в сообщении фото
        if (data.message && data.message.photo) {
          const chatId = data.message.chat.id;
          // Telegram присылает несколько размеров фото, берем самый большой (последний в списке)
          const fileId = data.message.photo[data.message.photo.length - 1].file_id;

          // 1. Получаем путь к файлу через API Telegram
          const fileInfoResponse = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/getFile?file_id=${fileId}`);
          const fileInfo = await fileInfoResponse.json();
          
          if (fileInfo.ok) {
            const filePath = fileInfo.result.file_path;
            
            // 2. Скачиваем само изображение
            const imageResponse = await fetch(`https://api.telegram.org/file/bot${env.BOT_TOKEN}/${filePath}`);
            const imageBuffer = await imageResponse.arrayBuffer();

            // 3. Формируем ответное сообщение с фото
            // В JS-воркере мы используем FormData для отправки файлов
            const formData = new FormData();
            formData.append('chat_id', chatId);
            formData.append('photo', new Blob([imageBuffer]), 'image.png');
            formData.append('caption', 'Облачный микросервис успешно обработал ваше изображение!');

            // 4. Отправляем фото обратно пользователю
            await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendPhoto`, {
              method: 'POST',
              body: formData
            });
          }
        }
        return new Response("OK", { status: 200 });
      } catch (e) {
        // Если что-то пошло не так, выводим ошибку в логи
        return new Response(e.message, { status: 200 });
      }
    }

    // Текст, который ты видишь в браузере
    return new Response("Микросервис активен и ожидает данных от Telegram API.");
  }
};
