import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from collage_maker import CollageMaker

API_TOKEN = '8783400059:AAGKuUHfxkE4mMKlTGMKsVmgQcGjGQ4CNdk'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
maker = CollageMaker()

COLLAGE_DIR = "gallery_collages"
PHOTO_DIR = "gallery_user_photos"

class Form(StatesGroup):
    waiting_for_title = State()       
    waiting_for_photos = State()      
    waiting_for_photo_name = State()  
    in_gallery = State()              

def get_main_menu():
    buttons = [[KeyboardButton(text="Создать коллаж"), KeyboardButton(text="Галерея")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_back_menu():
    buttons = [[KeyboardButton(text="Назад")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
@dp.message(F.text == "Назад")
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=get_main_menu())

# --- СОХРАНЕНИЕ ФОТО С ПРОВЕРКОЙ НА УНИКАЛЬНОСТЬ ---
@dp.message(F.photo, StateFilter(None))
async def process_single_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(temp_photo_id=photo.file_id)
    await message.answer("Принято. Введите уникальное имя для этого фото:", reply_markup=get_back_menu())
    await state.set_state(Form.waiting_for_photo_name)

@dp.message(Form.waiting_for_photo_name)
async def save_named_photo(message: types.Message, state: FSMContext):
    if message.text == "Назад": return
    
    name = "".join([c for c in message.text if c.isalnum() or c in (' ', '_')]).strip()
    file_path = os.path.join(PHOTO_DIR, f"{name}.jpg")
    
    # ПРОВЕРКА: существует ли уже такое имя в фото или коллажах
    collage_path = os.path.join(COLLAGE_DIR, f"{name}.jpg")
    
    if os.path.exists(file_path) or os.path.exists(collage_path):
        await message.answer(f"Ошибка! Имя '{name}' уже занято. Придумайте другое:")
        return

    data = await state.get_data()
    file_info = await bot.get_file(data['temp_photo_id'])
    await bot.download_file(file_info.file_path, file_path)
    await message.answer(f"Фото '{name}' успешно сохранено!", reply_markup=get_main_menu())
    await state.clear()

# --- ГАЛЕРЕЯ ---
@dp.message(F.text == "Галерея")
async def show_gallery(message: types.Message, state: FSMContext):
    collages = [f.replace(".jpg", "") for f in os.listdir(COLLAGE_DIR) if f.endswith(".jpg")]
    photos = [f.replace(".jpg", "") for f in os.listdir(PHOTO_DIR) if f.endswith(".jpg")]
    
    text = "📂 **Галерея**\n\n"
    text += "🖼 **Коллажи:** " + (", ".join(collages) if collages else "нет") + "\n"
    text += "📷 **Фотографии:** " + (", ".join(photos) if photos else "нет") + "\n\n"
    text += "Введите название для просмотра:"
    
    await message.answer(text, reply_markup=get_back_menu())
    await state.set_state(Form.in_gallery)

@dp.message(Form.in_gallery)
async def gallery_view(message: types.Message, state: FSMContext):
    name = message.text.strip()
    c_path = os.path.join(COLLAGE_DIR, f"{name}.jpg")
    p_path = os.path.join(PHOTO_DIR, f"{name}.jpg")
    
    path = c_path if os.path.exists(c_path) else p_path if os.path.exists(p_path) else None
    
    if path:
        await message.answer_photo(FSInputFile(path))
    else:
        await message.answer("Файл не найден.")

# --- КОЛЛАЖ (ПРОВЕРКА ИМЕНИ ПЕРЕД ЗАГРУЗКОЙ ФОТО) ---
@dp.message(F.text == "Создать коллаж")
async def start_collage(message: types.Message, state: FSMContext):
    await message.answer("Введите уникальное название темы для коллажа:", reply_markup=get_back_menu())
    await state.set_state(Form.waiting_for_title)

@dp.message(Form.waiting_for_title)
async def title_step(message: types.Message, state: FSMContext):
    name = "".join([c for c in message.text if c.isalnum() or c in (' ', '_')]).strip()
    c_path = os.path.join(COLLAGE_DIR, f"{name}.jpg")
    p_path = os.path.join(PHOTO_DIR, f"{name}.jpg")
    
    if os.path.exists(c_path) or os.path.exists(p_path):
        await message.answer(f"Название '{name}' уже используется. Введите другое:")
        return

    await state.update_data(title=message.text, photos=[])
    await message.answer(f"Тема '{message.text}' свободна. Пришлите 4 фото.")
    await state.set_state(Form.waiting_for_photos)

@dp.message(Form.waiting_for_photos, F.photo)
async def photo_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data['photos']
    file_info = await bot.get_file(message.photo[-1].file_id)
    temp_name = f"temp_{message.from_user.id}_{len(photos)}.jpg"
    await bot.download_file(file_info.file_path, temp_name)
    photos.append(temp_name)
    await state.update_data(photos=photos)
    
    if len(photos) < 4:
        await message.answer(f"Загружено {len(photos)}/4")
    else:
        await message.answer("Создаю коллаж...")
        res = await asyncio.to_thread(maker.create_grid_collage, photos, data['title'])
        await message.answer_photo(FSInputFile(res), caption="Готово!", reply_markup=get_main_menu())
        for p in photos: 
            if os.path.exists(p): os.remove(p)
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())