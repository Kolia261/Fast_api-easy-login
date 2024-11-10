from fastapi import FastAPI, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from auth import get_password_hash, verify_password, get_current_user
from database import get_db, engine, Base
from models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already exists"})

    new_user = User(username=username, password=get_password_hash(password), email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse("index.html", {"request": request, "message": "Registration successful"})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    if not verify_password(form_data.password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})


    return templates.TemplateResponse("index.html", {"request": request, "user": user, "message": "Login successful"})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
