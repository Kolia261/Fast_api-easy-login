import os
from fastapi import FastAPI, Request, Form, redirect,  Depends,  HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .auth import get_current_user, authenticate_user, signup_user
from .models import User, Base
from .database import engine, SessionLocal
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Настройка FastAPI
app = FastAPI()

# Создание базы данных
Base.metadata.create_all(bind=engine)

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Telegram Bot
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Замените на свой токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}! I'm your bot!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Обработка сообщения пользователя
    # (например, проверка команд, отправка ответов)

# Telegram Bot: Настройка и запуск
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

# FastAPI: Маршруты
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@app.post("/login", response_class=RedirectResponse)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db=SessionLocal(), username=form_data.username, password=form_data.password)
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    else:
        return RedirectResponse(url="/", status_code=302)

@app.post("/register", response_class=RedirectResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    signup_user(db=SessionLocal(), username=username, password=password)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db=SessionLocal(), username=form_data.username, password=form_data.password)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    else:
        token = user.generate_jwt()
        return {"access_token": token, "token_type": "bearer"}