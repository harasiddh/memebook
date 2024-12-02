import os
from werkzeug.datastructures import FileStorage
from sqlalchemy import desc
from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse

from application.database import db
from application.models import User, Meme, Followers, Likes, MemeCreators
from application.validation import NotFoundError, IncorrectPasswordError, EmptyForm, InvalidInputError, DependencyError
from application.config import LocalDevelopmentConfig


######################################


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
    if email[0] == '@' or email[0] == '.':
        allowed = False
        return allowed
    if email[-1] == '@' or email[-1] == '.':
        allowed = False
        return allowed
    for i in range(len(email)):
        if not (email[i].isalpha() or email[i].isdigit() or email[i] == '@' or email[i] == '.'):
            allowed = False
            break
        if email[i] == '@':
            if email[i + 1] == '.':
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


output_fields_user = {"username": fields.String, "email": fields.String}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('email', required=True, help='email cannot be blank')
create_user_parser.add_argument('first_name', required=True, help='first name cannot be blank')
create_user_parser.add_argument('last_name', required=True, help='last name cannot be blank')
create_user_parser.add_argument('username', required=True, help='username cannot be blank')
create_user_parser.add_argument('password', required=True, help='password cannot be blank. has to be filled twice')
create_user_parser.add_argument('repeat_password', required=True, help='password cannot be blank. has to be filled twice')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('current_password')
update_user_parser.add_argument('new_email')
update_user_parser.add_argument('new_username')
update_user_parser.add_argument('new_password')
update_user_parser.add_argument('repeat_new_password')

delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument('my_password')


class UserAPI(Resource):

    @marshal_with(output_fields_user)
    def get(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(output_fields_user)
    def put(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            raise NotFoundError(status_code=404)
        else:
            args = update_user_parser.parse_args()
            current_password = args.get('current_password', None)
            new_email = args.get('new_email', None)
            new_username = args.get('new_username', None)
            new_password = args.get('new_password', None)
            repeat_new_password = args.get('repeat_new_password', None)
            if current_password is None:
                raise IncorrectPasswordError(status_code=400, error_code="ERROR1", error_message='please enter current password')
            if current_password != user.password:
                raise IncorrectPasswordError(status_code=400, error_code="ERROR2", error_message='current password is incorrect')
            if new_email is None and new_username is None and new_password is None:
                raise EmptyForm(status_code=400, error_code='ERROR3', error_message='please update atleast one parameter')
            if new_email is not None and not allowed_email(new_email):
                raise InvalidInputError(status_code=400, error_code='ERROR4', error_message='invalid email')
            if new_username is not None and not allowed_username(new_username):
                raise InvalidInputError(status_code=400, error_code='ERROR5', error_message='invalid username')
            if new_password is not None and not allowed_password(new_password):
                raise InvalidInputError(status_code=400, error_code='ERROR6', error_message='invalid password')
            if new_password is not None and repeat_new_password is None:
                raise InvalidInputError(status_code=400, error_code='ERROR7', error_message='please enter new password twice')
            if new_password is None and repeat_new_password is not None:
                raise InvalidInputError(status_code=400, error_code='ERROR7', error_message='please enter new password twice')
            if new_password is not None:
                valid = valid_password_change(current_password, new_password, repeat_new_password, username)
                if valid != 'Password changed successfully':
                    raise InvalidInputError(status_code=400, error_code='ERROR8', error_message=valid)
            user_identify_email = User.query.filter_by(email=new_email).first()
            if user_identify_email:
                raise InvalidInputError(status_code=400, error_code='ERROR9', error_message='email already in use. choose a different one')
            user_identify_username = User.query.filter_by(email=new_username).first()
            if user_identify_username:
                raise InvalidInputError(status_code=400, error_code='ERROR10', error_message='username already in use. choose a different one')
            if new_email is not None:
                user.email = new_email
            if new_username is not None:
                user.username = new_username
            if new_password is not None and repeat_new_password is not None and new_password == repeat_new_password:
                if current_password == user.password:
                    user.password = new_password
            db.session.commit()
            return user

    def delete(self, username):
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            raise NotFoundError(status_code=404)
        args = delete_user_parser.parse_args()
        my_password = args.get('my_password', None)
        if my_password != user.password:
            raise InvalidInputError(status_code=400, error_code='ERROR0', error_message='incorrect password')
        memes = Meme.query.filter_by(creator_username=username).all()
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
        # remove user from followers list of others
        followers_follower = Followers.query.filter_by(follower_username=username).all()
        for follower in followers_follower:
            db.session.delete(follower)
        # remove user from following list of others
        followers_following = Followers.query.filter_by(user_username=username).all()
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
        meme_creator = MemeCreators.query.filter_by(user_id=user.id).all()
        for element in meme_creator:
            db.session.delete(element)
        db.session.delete(user)
        db.session.commit()
        return "", 200

    @marshal_with(output_fields_user)
    def post(self):
        args = create_user_parser.parse_args()
        email = args.get("email", None)
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        username = args.get("username", None)
        password = args.get("password", None)
        repeat_password = args.get("repeat_password", None)
        if email is None or username is None or password is None or first_name is None or last_name is None or repeat_password is None:
            raise EmptyForm(status_code=400, error_code='ERROR0', error_message='you need to fill all details')
        if not allowed_email(email):
            raise InvalidInputError(status_code=400, error_code='ERROR4', error_message='invalid email')
        if not allowed_username(username):
            raise InvalidInputError(status_code=400, error_code='ERROR5', error_message='invalid username')
        if not allowed_first_name(first_name):
            raise InvalidInputError(status_code=400, error_code='ERROR11', error_message='invalid first name')
        if not allowed_last_name(last_name):
            raise InvalidInputError(status_code=400, error_code='ERROR12', error_message='invalid last name')
        if not allowed_password(password):
            raise InvalidInputError(status_code=400, error_code='ERROR6', error_message='invalid password')
        if password != repeat_password:
            raise InvalidInputError(status_code=400, error_code='ERROR8', error_message='Passwords do not match')
        user_identify_email = User.query.filter_by(email=email).first()
        if user_identify_email:
            raise InvalidInputError(status_code=400, error_code='ERROR9',
                                    error_message='email already in use. choose a different one')
        user_identify_username = User.query.filter_by(email=username).first()
        if user_identify_username:
            raise InvalidInputError(status_code=400, error_code='ERROR10',
                                    error_message='username already in use. choose a different one')
        user = User(email=email, username=username, first_name=first_name, last_name=last_name, password=password)
        db.session.add(user)
        db.session.commit()
        return user, 201


######################################


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in LocalDevelopmentConfig.ALLOWED_EXTENSIONS


def file_type(filename):
    return filename.rsplit('.', 1)[1].lower()


def rename_file(old_file, new_file):
    os.rename(old_file, new_file)


output_fields_meme = {"title": fields.String, "caption": fields.String, "creator_username": fields.String}

create_meme_parser = reqparse.RequestParser()
create_meme_parser.add_argument('title')
create_meme_parser.add_argument('caption')
# create_meme_parser.add_argument('file', type=FileStorage, location=)
create_meme_parser.add_argument('creator_username')
create_meme_parser.add_argument('creator_password')
# create_meme_parser.add_argument('extension')
# create_meme_parser.add_argument('likes')

update_meme_parser = reqparse.RequestParser()
update_meme_parser.add_argument('creator_password')
update_meme_parser.add_argument('new_title')
update_meme_parser.add_argument('new_caption')
# update_meme_parser.add_argument('file', type=FileStorage, location=)
# update_meme_parser.add_argument('extension')

delete_meme_parser = reqparse.RequestParser()
delete_meme_parser.add_argument('creator_password')


class MemeAPI(Resource):

    @marshal_with(output_fields_meme)
    def get(self, id):
        meme = db.session.query(Meme).filter(Meme.id == id).first()
        if meme:
            return meme
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(output_fields_meme)
    def put(self, id):
        meme = db.session.query(Meme).filter(Meme.id == id).first()
        creator = User.query.filter_by(username=meme.creator_username).first()
        args = update_meme_parser.parse_args()
        creator_password = args.get('creator_password', None)
        new_title = args.get('new_title', None)
        new_caption = args.get('new_caption', None)
        if new_title is None and new_caption is None:
            raise EmptyForm(status_code=400, error_code='ERROR(-1)', error_message='please update atleast one parameter')
        if creator_password != creator.password:
            raise InvalidInputError(status_code=400, error_code='ERROR(-2)', error_message='incorrect password')
        meme.title = new_title
        meme.caption = new_caption
        db.session.commit()
        return meme

    def delete(self, id):
        meme = db.session.query(Meme).filter(Meme.id == id).first()
        if meme is None:
            raise NotFoundError(status_code=404)
        user = db.session.query(User).filter(User.username == meme.creator_username).first()
        args = delete_meme_parser.parse_args()
        creator_password = args.get('creator_password', None)
        if creator_password != user.password:
            raise InvalidInputError(status_code=400, error_code='ERROR(0)', error_message='incorrect password')
        meme_extension = meme.extension
        meme_id = id
        if meme_extension:
            os.remove(os.path.join(LocalDevelopmentConfig.UPLOADED_MEMES_DIR, str(meme_id) + '.' + meme_extension))
        likes = Likes.query.filter_by(meme_id=id).all()
        for like in likes:
            db.session.delete(like)
        meme_creator = MemeCreators.query.filter_by(meme_id=id).first()
        if meme_creator:
            db.session.delete(meme_creator)
        db.session.delete(meme)
        db.session.commit()
        return "", 200

    @marshal_with(output_fields_meme)
    def post(self):
        args = create_meme_parser.parse_args()
        title = args.get('title', None)
        caption = args.get('caption', None)
        creator_username = args.get('creator_username', None)
        creator_password = args.get('creator_password', None)
        user = User.query.filter_by(username=creator_username).first()
        user_id = user.id
        if user is None:
            raise InvalidInputError(status_code=400, error_code='ERROR(-3)', error_message='user does not exist')
        if user.password != creator_password:
            raise InvalidInputError(status_code=400, error_code='ERROR(0)', error_message='incorrect password')
        if title is None or caption is None:
            raise EmptyForm(status_code=400, error_code='ERROR(-1)', error_message='please fill up all parameters')
        meme = Meme(title=title, caption=caption, creator_username=creator_username, likes=0)
        db.session.add(meme)
        db.session.commit()
        last_meme = Meme.query.order_by(desc(Meme.id)).first()
        meme_id = last_meme.id
        meme_creator = MemeCreators(user_id=user_id, meme_id=meme_id)
        db.session.add(meme_creator)
        db.session.commit()
        return meme, 201

