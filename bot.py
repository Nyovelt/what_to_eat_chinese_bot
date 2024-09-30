import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler
from uuid import uuid4
from openai import OpenAI
from typing import List
import os

# Setup OpenAI API key
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)  # Ensure the key is set via environment variables
client = OpenAI(api_key=OPENAI_API_KEY)
# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def ask_chatgpt() -> str:
    """
    Interact with OpenAI to get a food suggestion.
    Returns:
        A string containing a food suggestion or an error message.
    """
    prompt = "请随机告诉我一道菜的名字。中式或者西式皆可。直接回答这道菜的名字。"
    try:
        logger.info("Sending request to OpenAI...")
        response = client.chat.completions.create(  # type: ignore
            model="gpt-3.5-turbo",  # Using GPT-4 Turbo model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=10,
            temperature=1,
        )
        food_name: str = response.choices[0].message.content  # type: ignore
        logger.info(f"Received food suggestion: {food_name}")
        return food_name
    except Exception as e:
        logger.error(f"Error with OpenAI API: {e}")
        return "无法获取食物名称，请稍后再试。"


async def inline_query(update: Update, context) -> None:
    """
    Handle inline queries from users and respond with a food suggestion.

    Args:
        update: Update object from Telegram.
        context: Context object from Telegram.
    """
    query: str = update.inline_query.query  # type: ignore
    logger.info(f"Received inline query: {query}")
    food_name: str = await ask_chatgpt()
    results: List[InlineQueryResultArticle] = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"建议食物: {food_name}",
            input_message_content=InputTextMessageContent(food_name),
        )
    ]
    await update.inline_query.answer(results, cache_time=0)  # type: ignore


async def start(update: Update, context) -> None:
    """
    Responds to the /start command with a greeting message.

    Args:
        update: Update object from Telegram.
        context: Context object from Telegram.
    """
    logger.info("Start command received.")
    await update.message.reply_text(  # type: ignore
        '你好！使用 inline 模式输入 "吃什么" 获取食物建议。'
    )


def main() -> None:
    """
    Main function to start the Telegram bot and register handlers.
    """
    # Set up the Telegram bot with the token
    token: str = os.getenv("TELEGRAM_BOT_TOKEN")  # type: ignore # Token should be set as an environment variable
    if not token:
        logger.error("Telegram bot token not found in environment variables.")
        return

    application = Application.builder().token(token).build()

    # Register command and inline query handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
