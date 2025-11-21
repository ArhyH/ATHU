from .bot import bot, keyboards
from modules.consts import user_states

from PIL import Image
from io import BytesIO
import threading
import requests
import time


def animate_progress(chat_id, message_id):
    frames = ["⏳", "⌛"]
    texts = [
        "Загружаю изображение...",
        "Анализирую формат...",
        "Сжимаю изображение...",
        "Оптимизирую качество...",
        "Почти готово...",
    ]

    frame_idx = 0
    text_idx = 0

    while user_states.get(chat_id, {}).get("compressing", False):
        try:
            emoji = frames[frame_idx % len(frames)]
            text = texts[text_idx % len(texts)]

            bot.edit_message_text(
                chat_id=chat_id, message_id=message_id, text=f"{emoji} {text}"
            )

            frame_idx += 1
            if frame_idx % 3 == 0:
                text_idx += 1

            time.sleep(0.5)
        except:
            break


def compress_image_pillow(image_data, quality=85):
    img = Image.open(image_data)
    original_format = img.format if img.format else "JPEG"

    has_transparency = img.mode in ("RGBA", "LA", "P") and "transparency" in img.info
    save_format = original_format
    file_extension = original_format.lower()

    if original_format == "JPEG" or original_format == "JPG":
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])
            else:
                gray = img.convert("L")
                background.paste(gray, mask=img.split()[1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        save_format = "JPEG"
        file_extension = "jpg"

    elif original_format == "PNG":
        if img.mode == "P":
            img = img.convert("RGBA") if has_transparency else img.convert("RGB")
        elif img.mode in ("L", "I", "F", "1"):
            img = img.convert("RGB")
        save_format = "PNG"
        file_extension = "png"

    elif original_format == "WEBP":
        if img.mode == "P":
            img = img.convert("RGBA") if has_transparency else img.convert("RGB")
        elif img.mode in ("L", "I", "F", "1"):
            img = img.convert("RGB")
        save_format = "WEBP"
        file_extension = "webp"

    else:
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode == "LA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            gray = img.convert("L")
            background.paste(gray, mask=img.split()[1])
            img = background
        elif img.mode == "P":
            img = img.convert("RGB")
        elif img.mode not in ("RGB", "RGBA"):
            try:
                img = img.convert("RGB")
            except:
                img = img.convert("RGBA").convert("RGB")
        save_format = "JPEG"
        file_extension = "jpg"

    max_dimension = 2048
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    output = BytesIO()

    save_params = {"optimize": True}

    if save_format in ("JPEG", "JPG"):
        save_params.update({"quality": quality, "progressive": True})
    elif save_format == "PNG":
        save_params.update({"compress_level": 9})
    elif save_format == "WEBP":
        save_params.update({"quality": quality, "method": 6})

    img.save(output, format=save_format, **save_params)
    output.seek(0)

    return output, save_format, file_extension


@bot.message_handler(commands=["tinyimg"])
def tinyimg_command(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"waiting_for_image": True}

    bot.send_message(
        chat_id,
        "📸 Отправьте мне изображение, которое нужно сжать.\n\n"
        "Поддерживаются все популярные форматы: PNG, JPEG, WebP, BMP и др.",
    )


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    chat_id = message.chat.id

    if not user_states.get(chat_id, {}).get("waiting_for_image"):
        return

    user_states[chat_id]["waiting_for_image"] = False
    user_states[chat_id]["compressing"] = True

    progress_msg = bot.send_message(chat_id, "⏳ Начинаю обработку...")

    animation_thread = threading.Thread(
        target=animate_progress, args=(chat_id, progress_msg.message_id)
    )
    animation_thread.start()

    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)

        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        response = requests.get(file_url)
        image_data = BytesIO(response.content)
        original_size = len(response.content)

        compressed_image, format_name, file_ext = compress_image_pillow(
            image_data, quality=85
        )
        compressed_size = len(compressed_image.getvalue())

        compression_ratio = ((original_size - compressed_size) / original_size) * 100

        user_states[chat_id]["compressing"] = False
        animation_thread.join()

        bot.delete_message(chat_id, progress_msg.message_id)

        compressed_image.seek(0)
        compressed_image.name = f"compressed_image.{file_ext}"

        if compressed_size < original_size:
            bot.send_photo(
                chat_id,
                compressed_image,
                caption=(
                    f"✅ Изображение успешно сжато!\n\n"
                    f"📄 Формат: {format_name}\n\n"
                    f"📊 Исходный размер: {original_size / 1024:.2f} KB\n\n"
                    f"📉 Сжатый размер: {compressed_size / 1024:.2f} KB\n\n"
                    f"💾 Сэкономлено: {compression_ratio:.1f}%"
                ),
            )

        else:
            bot.send_message(
                chat_id,
                "ℹ️ Изображение уже хорошо оптимизировано.\n"
                f"Текущий размер: {original_size / 1024:.2f} KB",
            )

    except Exception as error:
        user_states[chat_id]["compressing"] = False
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=progress_msg.message_id,
            text=f"❌ Произошла ошибка: {str(error)}",
        )

    finally:
        if chat_id in user_states:
            user_states[chat_id].clear()

        bot.send_message(
            chat_id,
            "Чем я могу ещё помочь?",
            reply_markup=keyboards["/start"],
        )


@bot.message_handler(content_types=["document"])
def handle_document(message):
    chat_id = message.chat.id

    if not user_states.get(chat_id, {}).get("waiting_for_image"):
        return

    if message.document.mime_type and message.document.mime_type.startswith("image/"):
        user_states[chat_id]["waiting_for_image"] = False
        user_states[chat_id]["compressing"] = True

        progress_msg = bot.send_message(chat_id, "⏳ Начинаю обработку...")

        animation_thread = threading.Thread(
            target=animate_progress, args=(chat_id, progress_msg.message_id)
        )
        animation_thread.start()

        try:
            file_info = bot.get_file(message.document.file_id)
            file_url = (
                f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
            )

            response = requests.get(file_url)
            image_data = BytesIO(response.content)
            original_size = len(response.content)
            compressed_image, format_name, file_ext = compress_image_pillow(
                image_data, quality=85
            )
            compressed_size = len(compressed_image.getvalue())

            compression_ratio = (
                (original_size - compressed_size) / original_size
            ) * 100

            user_states[chat_id]["compressing"] = False
            animation_thread.join()

            bot.delete_message(chat_id, progress_msg.message_id)

            compressed_image.seek(0)
            compressed_image.name = f"compressed_image.{file_ext}"

            if compressed_size < original_size:
                bot.send_document(
                    chat_id,
                    compressed_image,
                    caption=(
                        f"✅ Изображение успешно сжато!\n\n"
                        f"📄 Формат: {format_name}\n\n"
                        f"📊 Исходный размер: {original_size / 1024:.2f} KB\n\n"
                        f"📉 Сжатый размер: {compressed_size / 1024:.2f} KB\n\n"
                        f"💾 Сэкономлено: {compression_ratio:.1f}%"
                    ),
                )

            else:
                bot.send_message(
                    chat_id,
                    "ℹ️ Изображение уже хорошо оптимизировано.\n"
                    f"Текущий размер: {original_size / 1024:.2f} KB",
                )

        except Exception as e:
            user_states[chat_id]["compressing"] = False
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress_msg.message_id,
                text=f"❌ Произошла ошибка: {str(e)}",
            )

        finally:
            if chat_id in user_states:
                user_states[chat_id].clear()

            bot.send_message(
                chat_id,
                "Чем я могу ещё помочь?",
                reply_markup=keyboards["/start"],
            )

    else:
        bot.send_message(chat_id, "❌ Пожалуйста, отправьте изображение.")
