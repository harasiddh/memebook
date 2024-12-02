import os, sqlite3
from flask import Flask, request
from flask import render_template
from flask import redirect
from flask import current_app as app
from sqlalchemy import desc
from application.models import User, Meme, Followers, Likes, MemeCreators
from application.database import db
import logging
from application.config import LocalDevelopmentConfig
from werkzeug.utils import secure_filename

logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")


@app.route("/", methods=["GET", "POST"])
def landing_page():
    return render_template("landing_page.html", confirmation_message=None)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == 'GET':
        return render_template('login_page.html')
    if request.method == 'POST':
        form = request.form
        login_username = form["username"]
        login_password = form["password"]
        user = None
        user = User.query.filter_by(username=login_username).first()
        print(user, type(user))
        if user:
            if user.password == login_password:
                return redirect('/' + login_username + '/home')
            else:
                error_message = "Username or Password is incorrect"
                return render_template('login_page.html', error_message=error_message)
        else:
            error_message = "Username or Password is incorrect"
            return render_template('login_page.html', error_message=error_message)


def allowed_first_name(first_name):
    allowed = True
    for i in first_name:
        if not i.isalpha():
            allowed = False
            break
    return allowed


def allowed_last_name(last_name):
    allowed = True
    for i in last_name:
        if not i.isalpha():
            allowed = False
            break
    return allowed


def allowed_email(email):
    allowed = True
    if '@' not in email or '.' not in email:
        allowed = False
        return allowed
    if email[0]=='@' or email[0]=='.':
        allowed = False
        return allowed
    if email[-1]=='@' or email[-1]=='.':
        allowed = False
        return allowed
    for i in range(len(email)):
        if not (email[i].isalpha() or email[i].isdigit() or email[i] == '@' or email[i] == '.'):
            allowed = False
            break
        if email[i] == '@':
            if email[i+1] == '.':
                allowed = False
                break
    return allowed


def allowed_username(username):
    allowed = True
    if len(username) > 12 or len(username) < 3:
        allowed = False
        return allowed
    for i in username:
        if not (i.isalpha() or i.isdigit() or (i == '_')):
            allowed = False
            break
    return allowed


def allowed_password(password):
    allowed = True
    if len(password) <= 5:
        allowed = False
    return allowed


def valid_password_change(current_password, new_password, repeat_password, username):
    valid = 'Password changed successfully'
    user = User.query.filter_by(username=username).first()
    if current_password != user.password:
        return 'Please enter your current password correctly'
    if new_password != repeat_password:
        return 'Make sure you enter the new password correctly twice.'
    if new_password == user.password:
        return 'New password cannot be the same as current password.'
    if len(new_password) <= 5:
        return 'Passwords must be atleast 6 characters in length and can contain letters, digits, special characters and spaces'
    return valid


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == 'GET':
        return render_template('register_page.html')
    if request.method == 'POST':
        form = request.form
        register_username = form["username"]
        register_password = form["password"]
        register_repeat_password = form["repeat_password"]
        register_email = form["email"]
        register_first_name = form["first_name"]
        register_last_name = form["last_name"]
        user_username = None
        user_email = None
        user_username = User.query.filter_by(username=register_username).first()
        user_email = User.query.filter_by(email=register_email).first()
        if not allowed_first_name(register_first_name) or not allowed_last_name(register_last_name):
            error_message = "Names must contain letters only."
            return render_template('register_page.html', error_message=error_message)
        if not allowed_email(register_email):
            error_message = 'Please provide a valid email address'
            return render_template('register_page.html', error_message=error_message)
        if not allowed_username(register_username):
            error_message = 'Username must be of 3-12 characters and can contain letters, numbers or underscores.'
            return render_template('register_page.html', error_message=error_message)
        if user_email:
            error_message = "Email already in use. Please provide an alternate."
            return render_template('register_page.html', error_message=error_message)
        if user_username:
            error_message = "Username already in use. Please provide an alternate."
            return render_template('register_page.html', error_message=error_message)
        if register_password != register_repeat_password:
            error_message = "Passwords do not match."
            return render_template('register_page.html', error_message=error_message)
        if not allowed_password(register_password):
            error_message = 'Passwords must be atleast 6 characters in length and can contain letters, digits, special characters and spaces'
            return render_template('register_page.html', error_message=error_message)
        new_user = User(email=register_email, first_name=register_first_name, last_name=register_last_name,
                        username=register_username, password=register_password)
        db.session.add(new_user)
        db.session.commit()
        confirmation_message = "Account Successfully Created! You may login now."
        return render_template('landing_page.html', confirmation_message=confirmation_message)


@app.route("/<user1>/home", methods=["GET", "POST"])
def home(user1):
    memes = Meme.query.order_by(desc(Meme.id)).all()
    # code to show only memes made by users followed is present in html
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('home.html', active_username=user1, memes=memes, user=user)


@app.route("/<user1>/most_liked", methods=["GET", "POST"])
def most_liked(user1):
    memes = Meme.query.order_by(desc(Meme.likes), desc(Meme.id)).all()
    # code to show only memes made by users followed is present in html
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('most_liked.html', active_username=user1, memes=memes, user=user)


@app.route("/<user1>/your_likes", methods=["GET", "POST"])
def your_likes(user1):
    memes = Meme.query.order_by(desc(Meme.id)).all()
    # code to show only memes made by users followed is present in html
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    check_likes = Likes.query.filter_by(user_id=user.id).all()
    return render_template('your_likes.html', active_username=user1, memes=memes, user=user, check_likes=check_likes)


@app.route("/<user1>/search", methods=["GET", "POST"])
def search(user1):
    # created index for this in SQLITE Database
    if request.method == 'GET':
        return render_template('search.html', active_username=user1)
    if request.method == 'POST':
        form = request.form
        q = form["q"]
        other_users = User.query.filter(User.username.startswith(q)).all()
        user_identify = User.query.filter_by(username=user1).first()
        user = User.query.get(user_identify.id)
        return render_template('results.html', other_users=other_users, active_username=user1, user=user)


@app.route("/<user1>/my_profile", methods=["GET", "POST"])
def my_profile(user1):
    # getting memes made by user alone
    my_memes = Meme.query.filter_by(creator_username=user1).order_by(desc(Meme.id)).all()
    count_memes = len(my_memes)
    # getting count of followers
    followers = Followers.query.filter_by(user_username=user1).all()
    count_followers = len(followers)
    # getting count of following
    following = Followers.query.filter_by(follower_username=user1).all()
    count_following = len(following)
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('my_profile.html', my_memes=my_memes,
                           active_username=user1,
                           count_memes=count_memes,
                           count_followers=count_followers,
                           count_following=count_following,
                           user=user)


@app.route("/<user1>/my_followers", methods=["GET", "POST"])
def my_followers(user1):
    followers = Followers.query.filter_by(user_username=user1).all()
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('my_followers.html',
                           followers=followers,
                           active_username=user1,
                           user=user)


@app.route("/<user1>/my_following", methods=["GET", "POST"])
def my_following(user1):
    following = Followers.query.filter_by(follower_username=user1).all()
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('my_following.html',
                           following=following,
                           active_username=user1,
                           user=user)


@app.route("/<user1>/edit_username", methods=["GET", "POST"])
def edit_username(user1):
    if request.method == 'GET':
        user = User.query.filter_by(username=user1).first()
        return render_template('edit_username.html', active_username=user1)
    if request.method == 'POST':
        user_identify = User.query.filter_by(username=user1).first()
        user = User.query.get(user_identify.id)
        form = request.form
        new_username = form['new_username']
        if new_username == user.username:
            error_message = 'New username cannot be same as current username'
            return render_template('edit_username.html', active_username=user1, error_message=error_message)
        unique_check = User.query.filter_by(username=new_username).first()
        if unique_check:
            error_message = "Username already in use. Please provide an alternate."
            return render_template('edit_username.html', active_username=user1, error_message=error_message)
        if not allowed_username(new_username):
            error_message = 'Username must be of 3-12 characters and can contain letters, numbers or underscores.'
            return render_template('edit_username.html', active_username=user1, error_message=error_message)
        user.username = new_username
        memes = Meme.query.filter_by(creator_username=user1).all()
        for element in memes:
            meme = Meme.query.get(element.id)
            meme.creator_username = new_username
        # update follower table
        followers_follower = Followers.query.filter_by(follower_username=user1).all()
        for follower in followers_follower:
            follower.follower_username = new_username
        # remove user from following list of others
        followers_following = Followers.query.filter_by(user_username=user1).all()
        for following in followers_following:
            following.user_username = new_username
        db.session.commit()
        return redirect('/'+new_username+'/my_profile')


@app.route("/<user1>/edit_email", methods=["GET", "POST"])
def edit_email(user1):
    if request.method == 'GET':
        user = User.query.filter_by(username=user1).first()
        return render_template('edit_email.html', active_username=user1, user=user)
    if request.method == 'POST':
        user_identify = User.query.filter_by(username=user1).first()
        user = User.query.get(user_identify.id)
        form = request.form
        new_email = form['new_email']
        if new_email == user.email:
            error_message = 'New email cannot be same as existing email.'
            return render_template('edit_email.html', active_username=user1, error_message=error_message, user=user)
        unique_check = User.query.filter_by(email=new_email).first()
        if unique_check:
            error_message = "Email already in use. Please provide an alternate."
            return render_template('edit_email.html', active_username=user1, error_message=error_message, user=user)
        if not allowed_email(new_email):
            error_message = 'Please provide a valid email address'
            return render_template('edit_email.html', active_username=user1, error_message=error_message, user=user)
        user.email = new_email
        db.session.commit()
        return redirect('/'+user1+'/my_profile')


@app.route("/<user1>/edit_password", methods=["GET", "POST"])
def edit_password(user1):
    if request.method == 'GET':
        user = User.query.filter_by(username=user1).first()
        return render_template('edit_password.html', active_username=user1)
    if request.method == 'POST':
        user_identify = User.query.filter_by(username=user1).first()
        user = User.query.get(user_identify.id)
        form = request.form
        current_password = form['current_password']
        new_password = form['new_password']
        repeat_password = form['repeat_password']
        valid = 'Password changed successfully'
        check_validity = valid_password_change(current_password, new_password, repeat_password, user1)
        if check_validity == valid:
            user.password = new_password
            db.session.commit()
            confirmation_message = valid
            return render_template('confirmation_success.html', confirmation_message=confirmation_message, active_username=user1, user=user)
        else:
            error_message = check_validity
            return render_template('edit_password.html', active_username=user1, error_message=error_message, user=user)


@app.route("/<user1>/delete_account", methods=["GET", "POST"])
def delete_account(user1):
    user = User.query.filter_by(username=user1).first()
    return render_template('delete_account.html', active_username=user1, user=user)


@app.route("/<user1>/delete_account/delete_confirmed", methods=["GET", "POST"])
def delete_account_confirmed(user1):
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    memes = Meme.query.filter_by(creator_username=user1).all()
    # deleting memes made by user
    for element in memes:
        meme = Meme.query.get(element.id)
        meme_extension = meme.extension
        meme_id = meme.id
        if meme_extension:
            os.remove(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, str(meme_id) + '.' + meme_extension))
        likes = Likes.query.filter_by(meme_id=meme.id).all()
        for like in likes:
            db.session.delete(like)
        db.session.delete(meme)
    meme_creator = MemeCreators.query.filter_by(user_id=user.id).all()
    for element in meme_creator:
        db.session.delete(element)
    # remove user from followers list of others
    followers_follower = Followers.query.filter_by(follower_username=user1).all()
    for follower in followers_follower:
        db.session.delete(follower)
    # remove user from following list of others
    followers_following = Followers.query.filter_by(user_username=user1).all()
    for following in followers_following:
        db.session.delete(following)
    # removing likes by user
    memes = Meme.query.all()
    for meme in memes:
        if user.has_liked_meme(meme):
            user.unlike(meme)
    likes = Likes.query.filter_by(user_id=user.id).all()
    for like in likes:
        db.session.delete(like)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in LocalDevelopmentConfig.ALLOWED_EXTENSIONS


def file_type(filename):
    return filename.rsplit('.', 1)[1].lower()


def rename_file(old_file, new_file):
    os.rename(old_file, new_file)


@app.route("/<user1>/create_meme", methods=["GET", "POST"])
def create_meme(user1):
    user = User.query.filter_by(username=user1).first()
    user_id = user.id
    if request.method == 'GET':
        return render_template('create_meme.html', active_username=user1)
    if request.method == 'POST':
        form = request.form
        meme_title = form["title"]
        meme_caption = form["caption"]
        meme_creator_username = user1
        meme_extension = None
        meme_likes = 0
        # code for saving the uploaded file
        file = request.files['file']
        new_meme = Meme(title=meme_title,
                        caption=meme_caption,
                        creator_username=meme_creator_username,
                        extension=meme_extension,
                        likes=meme_likes)
        db.session.add(new_meme)
        db.session.commit()
        if file:
            if allowed_file(file.filename):
                last_meme = Meme.query.order_by(desc(Meme.id)).first()
                str_meme_id = str(last_meme.id)
                filename = secure_filename(file.filename)
                file.save(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, filename))
                old_file = os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, filename)
                extension = file_type(filename)
                meme_extension = file_type(secure_filename(file.filename))
                last_meme.extension = meme_extension
                db.session.commit()
                new_file = os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, str_meme_id + '.' + extension)
                print(old_file, new_file)
                rename_file(old_file, new_file)
            else:
                error_message = 'Allowed File Formats: JPG, JPEG, PNG, GIF'
                return render_template('create_meme.html', active_username=user1, error_message=error_message)
        # code for updating the database
        last_meme = Meme.query.order_by(desc(Meme.id)).first()
        meme_id = last_meme.id
        meme_creator = MemeCreators(user_id=user_id, meme_id=meme_id)
        db.session.add(meme_creator)
        db.session.commit()
        return redirect('/' + user1 + '/home')


@app.route("/<user1>/edit_meme/<meme1_id>", methods=["GET", "POST"])
def edit_meme(user1, meme1_id):
    if request.method == 'GET':
        meme = Meme.query.filter_by(id=meme1_id).first()
        return render_template('edit_meme.html',
                               meme=meme,
                               active_username=user1,
                               meme1_id=meme1_id)
    if request.method == 'POST':
        meme = Meme.query.get(meme1_id)
        form = request.form
        if form["title"]:
            meme.title = form["title"]
        if form["caption"]:
            meme.caption = form["caption"]
        # write statement for image
        meme_id = meme1_id
        meme_extension = meme.extension
        file = request.files['file']
        if file:
            if allowed_file(file.filename):
                # os.remove(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, str(meme_id) + '.' + meme_extension))
                filename = secure_filename(file.filename)
                file.save(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, filename))
                old_file = os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, filename)
                extension = file_type(filename)
                meme_extension = file_type(secure_filename(file.filename))
                meme.extension = meme_extension
                new_file = os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, str(meme_id) + '.' + extension)
                print(old_file, new_file)
                rename_file(old_file, new_file)
            else:
                error_message = 'Allowed File Formats: JPG, JPEG, PNG, GIF'
                return render_template('edit_meme.html', active_username=user1, error_message=error_message, meme=meme)
        db.session.commit()
        return redirect('/' + user1 + '/my_profile')


@app.route("/<user1>/delete_meme/<meme1_id>", methods=["GET", "POST"])
def delete_meme(user1, meme1_id):
    meme = Meme.query.filter_by(id=meme1_id).first()
    return render_template('delete_meme.html',
                           meme=meme,
                           active_username=user1,
                           meme1_id=meme1_id)


@app.route("/<user1>/delete_meme/<meme1_id>/delete_confirmed", methods=["GET", "POST"])
def delete_meme_confirmed(user1, meme1_id):
    meme = Meme.query.get(meme1_id)
    meme_extension = meme.extension
    meme_id = meme1_id
    if meme_extension:
        os.remove(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, meme_id + '.' + meme_extension))
    likes = Likes.query.filter_by(meme_id=meme1_id).all()
    for like in likes:
        db.session.delete(like)
    meme_creator = MemeCreators.query.filter_by(meme_id=meme1_id).all()
    for element in meme_creator:
        db.session.delete(element)
    db.session.delete(meme)
    db.session.commit()
    return redirect('/' + user1 + '/my_profile')


@app.route("/<user1>/profile/<user2>", methods=["GET", "POST"])
def user_profile(user1, user2):
    if request.method == 'GET':
        if user1 == user2:
            return redirect('/' + user1 + '/my_profile')
        # getting memes made by user alone
        user_memes = Meme.query.filter_by(creator_username=user2).order_by(desc(Meme.id)).all()
        count_memes = len(user_memes)
        # getting count of followers
        followers = Followers.query.filter_by(user_username=user2).all()
        count_followers = len(followers)
        # getting count of following
        following = Followers.query.filter_by(follower_username=user2).all()
        count_following = len(following)
        # check if user1 follows user2
        follow_check = None
        follow_check = Followers.query.filter_by(user_username=user2, follower_username=user1).first()
        user_identify = User.query.filter_by(username=user1).first()
        user = User.query.get(user_identify.id)
        return render_template('user_profile.html',
                               user_memes=user_memes,
                               active_username=user1,
                               other_username=user2,
                               count_memes=count_memes,
                               count_followers=count_followers,
                               count_following=count_following,
                               follow_check=follow_check,
                               user=user)


@app.route("/<user1>/profile/<user2>/followers", methods=["GET", "POST"])
def user_followers(user1, user2):
    followers = Followers.query.filter_by(user_username=user2).all()
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('user_followers.html',
                           followers=followers,
                           active_username=user1,
                           other_username=user2,
                           user=user)


@app.route("/<user1>/profile/<user2>/following", methods=["GET", "POST"])
def user_following(user1, user2):
    following = Followers.query.filter_by(follower_username=user2).all()
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    return render_template('user_following.html',
                           following=following,
                           active_username=user1,
                           other_username=user2,
                           user=user)


@app.route("/<user1>/profile/<user2>/follow", methods=["GET", "POST"])
def follow_user(user1, user2):
    new_follow = Followers(user_username=user2, follower_username=user1)
    db.session.add(new_follow)
    db.session.commit()
    return redirect(request.referrer)


@app.route("/<user1>/profile/<user2>/unfollow", methods=["GET", "POST"])
def unfollow_user(user1, user2):
    old_follow = Followers.query.get((user2, user1))
    db.session.delete(old_follow)
    db.session.commit()
    return redirect(request.referrer)


@app.route("/<user1>/likes/<meme1_id>", methods=["GET", "POST"])
def likes_meme(user1, meme1_id):
    meme = Meme.query.get(meme1_id)
    meme.likes = meme.likes + 1
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    user.like(meme)
    db.session.commit()
    return redirect(request.referrer)


@app.route("/<user1>/unlikes/<meme1_id>", methods=["GET", "POST"])
def unlikes_meme(user1, meme1_id):
    meme = Meme.query.get(meme1_id)
    meme.likes -= 1
    user_identify = User.query.filter_by(username=user1).first()
    user = User.query.get(user_identify.id)
    user.unlike(meme)
    db.session.commit()
    return redirect(request.referrer)

