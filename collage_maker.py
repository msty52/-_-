import os
from PIL import Image, ImageOps, ImageDraw, ImageFont

class CollageMaker:
    def __init__(self, output_dir="gallery_collages"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def create_grid_collage(self, image_paths, title="Без названия"):
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
        result_path = os.path.join(self.output_dir, f"{safe_title}.jpg")
        
        # Если файл уже есть, добавляем к названию уникальный индекс
        counter = 1
        original_path = result_path
        while os.path.exists(result_path):
            result_path = os.path.join(self.output_dir, f"{safe_title}_{counter}.jpg")
            counter += 1

        images = []
        for path in image_paths:
            img = Image.open(path).convert("RGB")
            img = ImageOps.fit(img, (800, 800), Image.Resampling.LANCZOS)
            images.append(img)

        collage = Image.new("RGB", (1600, 1700), (255, 255, 255))
        for i, img in enumerate(images):
            x = (i % 2) * 800
            y = (i // 2) * 800
            collage.paste(img, (x, y))

        draw = ImageDraw.Draw(collage)
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
            
        # Используем актуальное (возможно, измененное) имя для надписи на фото
        display_title = os.path.basename(result_path).replace(".jpg", "")
        draw.text((800, 1620), display_title, fill=(0, 0, 0), anchor="mt", font=font)
        
        collage.save(result_path, "JPEG", quality=95)
        return result_path