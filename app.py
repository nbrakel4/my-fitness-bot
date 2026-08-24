import os
import json
import streamlit as st
from groq import Groq

# Укажите ваш скопированный API-ключ с сайта Groq вместо текста ниже
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Имя файла на вашем Макбуке, где будет храниться история
HISTORY_FILE = "chat_history.json"

# Настройка внешнего вида страницы
st.set_page_config(page_title="Твой Чат-Тренер", page_icon="💪", layout="centered")
st.title("💪 Твой Чат-Тренер")
st.caption("Анатомия, физиология и история твоих тренировок")

# Жесткая инструкция для ИИ, чтобы он был узким фитнес-экспертом
SYSTEM_PROMPT = (
    "Ты — профессор спортивной физиологии, эксперт по биомеханике и элитный фитнес-тренер. "
    "Ты общаешься с девушкой. Твоя задача — помогать ей разбираться в устройстве тела, анатомии, питании и тренировках. "
    "Отвечай подробно, опираясь на науку. Категорически игнорируй любые вопросы, "
    "не связанные с фитнесом, спортом, анатомией и БЖУ."
)

# Функция для загрузки истории из файла
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

# Функция для сохранения истории в файл
def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# Инициализируем клиента ИИ
client = Groq(api_key=GROQ_API_KEY)

# Загружаем историю переписки в память текущей сессии
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# Отображаем на экране все старые сообщения (кроме системной роли)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Поле ввода сообщения пользователем
if user_input := st.chat_input("Спроси про мышцы, БЖУ или тренировку..."):
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Отправляем запрос к ИИ (используем модель Llama 3)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=st.session_state.messages,
                stream=False
            )
            answer = completion.choices[0].message.content
            response_placeholder.write(answer)
            
            # Добавляем ответ ИИ в историю и сохраняем на диск
            st.session_state.messages.append({"role": "assistant", "content": answer})
            save_history(st.session_state.messages)
            
        except Exception as e:
            st.error(f"Произошла ошибка при запросе к ИИ: {e}")

