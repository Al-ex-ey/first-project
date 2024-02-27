from flask import abort, flash, redirect, render_template, url_for
from . import app
from .forms import UploadForm


@app.route('/')
def index_view():
    try:
        return render_template('index.html')
    except:
        abort(404)


@app.route('/upload', methods=['GET', 'POST'])
def upload_view():
    form = UploadForm()
    if form.validate_on_submit():
        text = form.text.data
        if Opinion.query.filter_by(text=text).first():
            flash('Такое мнение уже было оставлено ранее!')
            return render_template('add_opinion.html', form=form)
        opinion = Opinion(
            title=form.title.data, 
            text=form.text.data, 
            source=form.source.data
        )
        db.session.add(opinion)
        db.session.commit()
        return redirect(url_for('opinion_view', id=opinion.id))
    return render_template('add_opinion.html', form=form)