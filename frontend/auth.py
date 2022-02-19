from flask import Blueprint, make_response, redirect, render_template

bp = Blueprint('auth', __name__)


@bp.get('/login')
def login():
    return render_template('login.html')


@bp.get('/register')
def register():
    return render_template('register.html')


@bp.get('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0)
    return resp
