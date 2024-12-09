from app import db
from datetime import datetime

class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), index=True, nullable=False)
    email = db.Column(db.String(500), index=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

    events_created = db.relationship('Event', back_populates='creator')

    rsvps = db.relationship('RSVP', back_populates='user') #Allows theuser to access all the events that the user has rsvpd to
    upvotes = db.relationship('Upvotes', back_populates='user') #Allows the user to access all the events the user has liked

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventTitle = db.Column(db.String(100), index=True, nullable=False)
    eventDate = db.Column(db.Date, nullable=False)
    eventPlace = db.Column(db.String(250), nullable=False)
    eventCategory = db.Column(db.String(50), nullable=False)
    eventDescription = db.Column(db.String(1000), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)

    creator = db.relationship('Register', back_populates='events_created') #Establishes relationship with the register model
    rsvps = db.relationship('RSVP', back_populates='event')
    upvotes = db.relationship('Upvotes', back_populates='event')

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))

    event = db.relationship('Event', back_populates='rsvps') #Linking with the event model
    user = db.relationship('Register', back_populates='rsvps')


class Upvotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    event = db.relationship('Event', back_populates='upvotes')
    user = db.relationship('Register', back_populates='upvotes')