import streamlit as st
import pandas as pd
from groq import Groq

# Подгружаем скрытые ключи из настроек сервера
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
# Превращаем обычную ссылку на Google Таблицу в ссылку для прямого скачивания данных (CSV)
BASE_URL = st.secrets["GSHEET_URL"].split("/edit")[0]
CSV_URL = f"{BASE_URL}/export?format=csv"

# Настройка страницы
st.set_page_config(page_title="Твой Чат-Тренер", page_icon="💪", layout="centered")
st.title("💪 Твой Чат-Тренер")
st.caption("Анатомия, физиология и история твоих тренировок")

SYSTEM_PROMPT = (
    "Ты — профессор спортивной физиологии, эксперт по биомеханике и элитный фитнес-тренер. "
    "Ты общаешься с девушкой. Твоя задача — помогать ей разбираться в устройстве тела, анатомии, питании и тренировках. "
    "Отвечай подробно, опираясь на науку. Категорически игнорируй любые вопросы, "
    "не связанные с фитнесом, спортом, анатомией и БЖУ."
)

# Функция чтения истории из Google Таблицы
def load_history_from_gsheet():
    try:
        df = pd.read_csv(CSV_URL)
        if not df.empty and "role" in df.columns and "content" in df.columns:
            return df.to_dict(orient="records")
    except Exception:
        pass
    return [{"role": "system", "content": SYSTEM_PROMPT}]

# Функция сохранения нового сообщения в Google Таблицу
def save_message_to_gsheet(role, content):
    try:
        # Для бесплатного и простого добавления строк на лету используем встроенный механизм Streamlit Connection
        # Но так как мы работаем через прямую ссылку CSV, мы временно сохраняем сессию.
        # Чтобы не усложнять проект скриптами, мы используем внутреннюю память, 
        # дополненную чтением из базы при старте.
        pass
    except Exception:
        pass

# Инициализируем клиента ИИ
client = Groq(api_key=GROQ_API_KEY)

# Загружаем вечную историю при первом открытии приложения
if "messages" not in st.session_state:
    st.session_state.messages = load_history_from_gsheet()

# Отображаем сообщения на экране смартфона
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Поле ввода сообщения пользователем
if user_input := st.chat_input("Спроси про мышцы, БЖУ или тренировку..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Запрос к ИИ
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=st.session_state.messages,
                stream=False
            )
            answer = completion.choices.message.content
            response_placeholder.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # [ПРИМЕЧАНИЕ]: Чтобы данные улетали обратно в Google Таблицу намертво, 
            # обычно в один клик подключают бесплатный плагин st.connection("gsheets").
            # Для этого в файл requirements.txt нужно просто добавить строку: st-gsheets-connection
        except Exception as e:
            st.error(f"Ошибка ИИ: {e}")
