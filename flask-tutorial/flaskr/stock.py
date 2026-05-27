from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("stock", __name__)


@bp.route("/")
def index():
    db = get_db()
    stocks = db.execute(
        "SELECT s.id, symbol, link, priority, u.id, u.username"
        " FROM stock s JOIN user u ON s.user_id = u.id"
    ).fetchall()

    return render_template("stock/index.html", stocks=stocks)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        symbol = request.form["symbol"]
        link = request.form["link"]
        p_up = request.form["p_up"]
        p_down = request.form["p_down"]
        priority = 1

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO stock (symbol, link, priority, percentage_up, percentage_down, user_id)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, link, priority, 5, 5, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("stock.index"))

    return render_template("stock/create.html")
