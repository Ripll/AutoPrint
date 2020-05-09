from config import LIST_PRICE


class Lang:
    start_msg = "🇺🇦 Привіт! Я - бот першого в світі принтцентру без людей!\n" \
                "✅ 24/7\n" \
                "✅ Без черг\n" \
                "✅ Підходь та друкуй де зручно\n" \
                "✅ Готівка - у минулому, сплачуй карткою\n\n" \
                "Все просто! Відправляй мені файл та слідкуй за інструкцією!"
    how_to_print = "https://telegra.ph/YAk-drukuvati-z-RipllPrintBot-04-16"
    info_msg = f"<b>ТАРИФИ</b>\n" \
               f"Наразі доступний лише один тариф:\n" \
               f"<code>1 лист чорнобілого друку А4 - {LIST_PRICE:.2f}грн.</code>\n\n" \
               f"<b>ТОЧКИ ДРУКУ</b>\n" \
               f"<code>Всі точки у порядку найближчих до тебе можна подивитися натиснувши кнопку \"Всі точки\"</code>"
    menu_btns = ["Особистий кабінет", "Кошик", "Як друкувати?", "Інформація"]
    loyalty_program = "Знижка залежить від надрукованих тобою сторінок:\n\n" \
                      "100-500 -> 5%\n" \
                      "501-1000 -> 10%\n" \
                      "1000-2000 -> 20%\n" \
                      "2000+ -> 25%"
    inline_send_file = "Відправляю файл..."
    inline_empty_result = "Нічого не знайдено."
    all_btn = "Всі сторінки"
    admin_btn = "Адмін панель"
    admin_btns = ["Створити точку", "Броадкаст",
                  "Статистика", "Пошук задачі",
                  "Пошук користувача"]
    skip_btn = "Пропустити"
    cancel_btn = "Відмінити"
    back_btn = "Назад"
    allowed_formats = "Доступні формати:\n\n" \
                      "Найкращий варіант: PDF!\n\n" \
                      "Word: doc, docx, odt, ott, stw, sdw, sxw\n" \
                      "Excel:  xls, xlsx, ods, ots, sdc, sxc\n" \
                      "Powerpoint: ppt, pptx, odp, pps, ppsx, sxi\n" \
                      "Images: jpg, jpeg, png, tif, tiff"
    error_fileformat_msg = "Цей формат не підтримується :с"
    error_filesize_msg = "Підтримуються файли тільки до 10мб"
    error_msg = "Такої команди не знайдено :с"
