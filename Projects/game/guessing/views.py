from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from .models import Point
from guessing import db
import random

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Jika angka acak belum ada di sesi, buat angka acak baru
    if 'angka_acak' not in session:
        session['angka_acak'] = random.randint(1, 10)
        session['attempts'] = 0

    angka_acak = session['angka_acak']  # Angka acak disimpan di sesi
    attempts = session['attempts']  # Jumlah upaya disimpan di sesi

    if attempts >= 3:
        flash(f'Anda sudah mencoba 3 kali. Angka yang benar adalah {angka_acak}. Coba lagi dengan angka baru!', category='Error')
        session.pop('angka_acak')  # Hapus angka acak dari session
        session.pop('attempts')  # Reset percobaan
        return render_template("home.html", user=current_user)

    if request.method == 'POST': 
        tebak = request.form.get('tebak')  # Mendapatkan tebakan dari form
        try:
            tebak = int(tebak)  # Konversi input dari string ke integer
        except ValueError:
            flash('Masukkan harus berupa angka!', category='Error')
            return render_template("home.html", user=current_user)

        # Ambil poin pengguna dari database
        current_point = Point.query.filter_by(user_id=current_user.id).first()

        # Jika belum ada, inisialisasi poin pengguna
        if current_point is None:
            current_point = Point(points=0, user_id=current_user.id)
            db.session.add(current_point)
            db.session.commit()

        # Cek apakah tebakan benar
        if tebak == angka_acak:
            current_point.points += 1  # Tambahkan poin
            db.session.commit()

            flash("You're Correct! Point Added!", category='success')
            # Buat angka acak baru setelah tebakan yang benar
            session['angka_acak'] = random.randint(1, 10)
            session['attempts'] = 0
        elif tebak != angka_acak:
            session['attempts'] += 1  # Tambahkan upaya
            remaining_attempts = 3 - session['attempts']
            flash(f"You're guess is wrong, Try Again. Remaining Attempts {remaining_attempts}", category='Error')
        elif tebak == None :
            flash('Masukkan harus berupa angka!', category='Error')

    points = Point.query.filter_by(user_id=current_user.id).all()

    return render_template("home.html", user=current_user, points=points)


def my_point():
    points = Point.query.filter_by(user_id=current_user.id).all()
    return render_template("base.html", user=current_user, points=points)