from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from ..forms import NotesReviewForm, SearchForm, UserSearchForm
from ..models import User, Review, Notes
from ..utils import current_time, get_b64_img

import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64

notes = Blueprint('notes', __name__, static_folder='static', template_folder='templates')

@notes.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()
    user_search_form = UserSearchForm()

    users = User.objects()
    notes = Notes.objects()
    
    lst = []
    for user in users:
        count = 0
        for note in notes:
            if user == note.notetaker:
                count += 1
        lst.append((user, count))
    lst = sorted(lst, key=lambda x: x[1])
    
    size = len(lst)
    contributions = lst[:-5] if size > 4 else lst[:size]
    xdata = [i[0].username for i in contributions]
    ydata = [i[1] for i in contributions]

    matplotlib.use('agg')
    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)
    plt.bar(x=xdata, height=ydata)
    plt.xlabel('Contributors')
    plt.ylabel('Number of Contributions')

    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())

    if form.validate_on_submit():
        return redirect(url_for("notes.query_results", query=form.search_query.data))
    if user_search_form.validate_on_submit():
        return redirect(url_for("notes.user_detail", username=user_search_form.username.data))

    return render_template("index.html", form=form, plot=figdata_png.decode('utf8'), form1=user_search_form)


@notes.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        class_names = set(Notes.objects(class_name__icontains=query))
        title_names = set(Notes.objects(title__icontains=query))
        results = list(set.union(class_names, title_names))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("notes.index"))

    return render_template("query.html", results=results)


@notes.route("/notes/<notes_id>", methods=["GET", "POST"])
def notes_detail(notes_id):
    try:
        result = Notes.objects(id=notes_id).first()
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("notes.index"))

    form = NotesReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            class_name=result.class_name,
            notes_id=notes_id,
            notes_title=result.title,
            rating=form.rating.data
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(notes_id=notes_id)
    print(reviews)
    pic_string = get_b64_img(result.id)

    return render_template(
        "notes_detail.html", form=form, notes=result, reviews=reviews, pic_string=pic_string
    )


@notes.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    notes = Notes.objects(notetaker=user)

    return render_template("user_detail.html", username=username, reviews=reviews, notes=notes, user=user)

@notes.route("/description")
def description():
    return render_template("description.html")