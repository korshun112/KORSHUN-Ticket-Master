<div align="center">

# 🎫 KORSHUN Ticket Master

**Мощная и гибкая система тикетов для Discord**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-5865F2?logo=discord&logoColor=white)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial-orange)](LICENSE)

_Разработано студией **KORSHUN BOTS**_

</div>

---

## ✨ Возможности

- 🎫 **Создание тикетов через панель** с выбором категории
- 👀 **Кнопка «Рассмотреть тикет»** — автор тикета получает ЛС, что его тикетом занялись
- 🔒 **Кнопка «Закрыть тикет»** — с отправкой ЛС автору и выдачей роли
- ⚙️ **Полная кастомизация** панели: заголовок, описание, цвет, изображение, миниатюра
- 🎭 **Гибкая система ролей** — роль поддержки, роль при открытии, роль при закрытии
- 📝 **Логирование** — все открытия и закрытия тикетов пишутся в отдельный канал
- 📢 **Команда `/announce`** — рассылка объявлений в ЛС всем участникам сервера
- 🛡️ **Защита от спама** — один активный тикет на пользователя
- 💾 **SQLite + async** — устойчивость к нагрузкам
- 🏷️ **Водяной знак KORSHUN BOTS** в футере каждого сообщения

## 📖 Команды
**⚙️ Настройка (требуется Manage Server)**
- /setup_panel <канал>	Создать панель тикетов
- /refresh_panel	Обновить панель после изменения настроек
- /config	Показать текущие настройки
- /config_category <категория>	Категория Discord для каналов-тикетов
- /config_logs <канал>	Канал для логов тикетов
- /config_support_role <роль>	Роль поддержки (пингуется при создании тикета)
- /config_open_role <роль>	Роль, выдаваемая при открытии тикета
- /config_close_role <роль>	Роль, выдаваемая при закрытии тикета
- /config_close_role_clear	Убрать роль при закрытии

# 📂 Категории тикетов
- /add_category <имя> [эмодзи] [описание]	Добавить категорию
- /list_categories	Список всех категорий
- /remove_category <id>	Удалить категорию по ID
# 🎨 Кастомизация панели
- /set_panel_title <текст>	Заголовок панели
- /set_panel_description <текст>	Описание (поддерживает \n)
- /set_panel_color <#RRGGBB>	Цвет эмбеда
- /set_panel_image <url>	Изображение панели
- /set_panel_thumbnail <url>	Миниатюра панели
# 📢 Дополнительно
- /announce <текст> [заголовок]	Рассылка объявления в ЛС всем участникам
- /help	Справка по командам
# 📜 Лицензия
Проект распространяется под PolyForm Noncommercial License 1.0.0.

- ✅ Разрешено: личное, учебное, некоммерческое использование
- ❌ Запрещено: коммерческое использование без разрешения

См. [LICENSE](https://github.com/korshun112/KORSHUN-Ticket-Master/blob/main/LICENSE) для подробностей.

<div align="center">
© 2026 KORSHUN BOTS. All Rights Reserved.

Разработано с ❤️ студией KORSHUN BOTS

</div>
