from .database import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    likes_meme = db.relationship("Meme", secondary='likes')

    def follows_creator(self, meme):
        return Followers.query.filter_by(user_username=meme.creator_username, follower_username=self.username).count() > 0

    def self_creator(self, meme):
        return self.username == meme.creator_username

    def follow_status_followed(self, other_user):
        return Followers.query.filter_by(user_username=other_user.user_username, follower_username=self.username).count() > 0

    def follow_status_follower(self, other_user):
        return Followers.query.filter_by(user_username=other_user.follower_username, follower_username=self.username).count() > 0

    def has_liked_meme(self, meme):
        return Likes.query.filter_by(user_id=self.id, meme_id=meme.id).count() > 0

    def like(self, meme):
        if not self.has_liked_meme(meme):
            new_like = Likes(user_id=self.id, meme_id=meme.id)
            db.session.add(new_like)

    def unlike(self, meme):
        if self.has_liked_meme(meme):
            old_like = Likes.query.get((self.id, meme.id))
            db.session.delete(old_like)

    # profile photo


class Followers(db.Model):
    __tablename__ = 'followers'
    user_username = db.Column(db.String, db.ForeignKey("user.username"), primary_key=True, nullable=False)
    follower_username = db.Column(db.String, db.ForeignKey("user.username"), primary_key=True, nullable=False)


class Meme(db.Model):
    __tablename__ = 'meme'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String)
    caption = db.Column(db.String)
    creator_username = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    extension = db.Column(db.String)
    likes = db.Column(db.Integer)
    creator = db.relationship("User", secondary='meme_creators')
    # time stamp needs to be added
    # ability to add images needs to be added


class MemeCreators(db.Model):
    __tablename__ = 'meme_creators'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    meme_id = db.Column(db.Integer, db.ForeignKey("meme.id"), primary_key=True, nullable=False)


class Likes(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    meme_id = db.Column(db.Integer, db.ForeignKey("meme.id"), primary_key=True, nullable=False)
