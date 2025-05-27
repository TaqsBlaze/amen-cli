import os
from pathlib import Path

from rich.console import Console

console = Console()

def scaffold_auth(app_path: Path, framework: str):
    """
    Scaffolds authentication boilerplate based on the specified framework.
    """
    if framework == "flask":
        _scaffold_flask_auth(app_path)
    elif framework == "fastapi":
        _scaffold_fastapi_auth(app_path)
    else:
        raise ValueError(f"Authentication scaffolding not implemented for framework: {framework}")

def _scaffold_flask_auth(app_path: Path):
    """
    Scaffolds authentication boilerplate for Flask.
    """
    # Create auth blueprint directory
    auth_bp_dir = app_path / "app" / "auth"
    os.makedirs(auth_bp_dir, exist_ok=True)

    # Create forms.py
    forms_content = """
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
"""
    with open(auth_bp_dir / "forms.py", "w") as f:
        f.write(forms_content)

    # Create routes.py
    routes_content = """
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from .forms import LoginForm, RegistrationForm
# from yourapp.models import User  # Import your User model
# from yourapp import db  # Import your database instance

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect to main page

    form = RegistrationForm()
    if form.validate_on_submit():
        # user = User(username=form.username.data, email=form.email.data)
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is None or not user.check_password(form.password.data):
        #     flash('Invalid email or password')
        #     return redirect(url_for('auth.login'))

        # login_user(user, remember=form.remember_me.data)
        # return redirect(url_for('main.index'))
        pass

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
"""
    with open(auth_bp_dir / "routes.py", "w") as f:
        f.write(routes_content)

    # Create templates directory
    templates_dir = auth_bp_dir / "templates" / "auth"
    os.makedirs(templates_dir, exist_ok=True)

    # Create login.html
    login_template_content = """
{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }}
        <p>
            {{ form.email.label }}<br>
            {{ form.email(size=32) }}<br>
            {% for error in form.email.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}<br>
            {% for error in form.password.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
"""
    with open(templates_dir / "login.html", "w") as f:
        f.write(login_template_content)

    # Create register.html
    register_template_content = """
{% extends "base.html" %}

{% block content %}
    <h1>Register</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.email.label }}<br>
            {{ form.email(size=32) }}<br>
            {% for error in form.email.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}<br>
            {% for error in form.password.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password2.label }}<br>
            {{ form.password2(size=32) }}<br>
            {% for error in form.password2.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
"""
    with open(templates_dir / "register.html", "w") as f:
        f.write(register_template_content)

    console.print(f"✅ Flask authentication scaffolding created in {auth_bp_dir}", style="green")

def _scaffold_fastapi_auth(app_path: Path):
    """
    Scaffolds authentication boilerplate for FastAPI.
    """
    # Create auth directory
    auth_dir = app_path / "app" / "auth"
    os.makedirs(auth_dir, exist_ok=True)

    # Create models.py
    models_content = """
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    disabled: Optional[bool] = None
"""
    with open(auth_dir / "models.py", "w") as f:
        f.write(models_content)

    # Create schemas.py
    schemas_content = """
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True
"""
    with open(auth_dir / "schemas.py", "w") as f:
        f.write(schemas_content)

    # Create security.py
    security_content = """
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
"""
    with open(auth_dir / "security.py", "w") as f:
        f.write(security_content)

    # Create routes.py
    routes_content = """
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# from yourapp import crud, models, schemas  # Import your CRUD operations, models, and schemas
# from yourapp.database import get_db  # Import your database dependency
# from yourapp.auth.security import get_password_hash, verify_password  # Import security functions

# @router.post("/token", response_model=schemas.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = crud.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = crud.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)

# @router.get("/users/me", response_model=schemas.User)
# async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
#     return current_user
"""
    with open(auth_dir / "routes.py", "w") as f:
        f.write(routes_content)

    console.print(f"✅ FastAPI authentication scaffolding created in {auth_dir}", style="green")
