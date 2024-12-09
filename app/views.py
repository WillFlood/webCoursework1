from flask import render_template, session, jsonify, flash, redirect, url_for, request
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Event, Register, RSVP, Upvotes
from app.forms import EventForm, RegisterForm, LoginForm, EditProfileForm, EditPasswordForm, EditEventForm
from datetime import date
from flask_restful import Api, Resource
import json


api = Api(app)


@app.route('/') # The first page that the user sees when searching up the website
def aboutUs():
    return render_template("aboutUs.html", title='About Us') #Only an information page, to tell the user what my website does before the register and login

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashPassword = generate_password_hash(form.password.data) #Hashing the password as it keeps it safe
        newUser = Register(
            username=form.username.data,
            email=form.email.data,
            password=hashPassword
        )
        db.session.add(newUser)
        db.session.commit()
        flash('Registered successfully!')
        return redirect(url_for('login')) #When the user has filled out the register form correctly, it redirects the user to the login page
    return render_template('register.html',
                           title='Register',
                           form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data): #Checking for the same email and hashed password
            session['user_id'] = user.id
            flash('Welcome back!')
            return redirect(url_for('yourEvents')) #First goes to their created events
        else:
            flash('Invalid email or password.')
    return render_template('login.html',
                               title='login',
                               form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None) #Removing the session id and redirecting the user back to the login page
    flash('You have been logged out!')
    return redirect(url_for('login'))
    
@app.route('/createEvent', methods=['GET', 'POST'])
def create():
    form=EventForm()
    if form.validate_on_submit():

        user_id = session.get('user_id') #Now checking whether the user is logged in, this is because they need to be logged in to access these pages.
        if not user_id:
            flash('Please log in')
            return redirect(url_for('login')) #Redirect the user back to the login page if they haven't logged in yet                   

        newEvent = Event(
            eventTitle=form.eventTitle.data,
            eventDate=form.eventDate.data,
            eventPlace=form.eventPlace.data,
            eventCategory=form.eventCategory.data,
            eventDescription=form.eventDescription.data,
            creator_id=user_id
        )
        db.session.add(newEvent)
        db.session.commit()

        flash('Event Created successfully!')
        return redirect(url_for('create'))
    return render_template('createEvent.html',
                           title='Create an event',
                           form=form)
 
@app.route('/goingEvents', methods=['GET']) #RSVP events
def goingEvents():
    #Again ensuring that the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first')
        return redirect(url_for('login'))

    #Fetching the current date for filtering 
    current_date = date.today()

    #FetchING events the user has RSVP'd to
    rsvpd_events = Event.query.join(RSVP).filter(RSVP.user_id == user_id).all()

    for event in rsvpd_events:
        # Determine if the current user has RSVPed to this event
        event.user_has_upvoted = Upvotes.query.filter_by(event_id=event.id, user_id=user_id).first() is not None

    #Pass the events to the template
    return render_template(
        'rsvpEvents.html',
        title='Your Events',
        rsvpd_events=rsvpd_events,
        current_date=current_date)

@app.route('/yourEvents', methods=['GET'])
def yourEvents():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first')
        return redirect(url_for('login'))

    #Fetching the current date for filtering 
    current_date = date.today()

    #Fetching events created by the user
    category = request.args.get('category', '')

    if category:
        created_events = Event.query.filter_by(eventCategory=category) #Apply filter if category is provided
    else:
        created_events = Event.query.filter_by(creator_id=user_id).all()

    return render_template(
        'createdEvents.html',
        title='Your Events',
        created_events=created_events,
        current_date=current_date)


@app.route('/rsvpEvent', methods=['POST']) 
def rsvp():

    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'error', 'message': 'Please log in first'}, 401

    event_id = request.json.get('event_id')
    if not event_id:
        return {'status': 'error', 'message': 'Invalid event ID'}, 400

    #Check if the user has already rsvp'd
    rsvp = RSVP.query.filter_by(event_id=event_id, user_id=user_id).first()
    if rsvp:
        #Cancel the rsvp
        db.session.delete(rsvp)
        db.session.commit()
        attendees_count = RSVP.query.filter_by(event_id=event_id).count()
        return {'status': 'success', 'message': 'RSVP cancelled', 'attendees_count': attendees_count}, 200
    else:
        #Add RSVP
        print("Adding RSVP")
        new_rsvp = RSVP(event_id=event_id, user_id=user_id)
        db.session.add(new_rsvp)
        db.session.commit()
        attendees_count = RSVP.query.filter_by(event_id=event_id).count()
        return {'status': 'success', 'message': 'RSVP confirmed', 'attendees_count': attendees_count}, 200
    
@app.route('/upvoteEvent', methods=['POST'])
def upvoteEvent():
    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'error', 'message': 'Please log in first'}, 401

    event_id = request.json.get('event_id')
    if not event_id:
        return {'status': 'error', 'message': 'Invalid event ID'}, 400

    upvote = Upvotes.query.filter_by(event_id=event_id, user_id=user_id).first()
    if upvote:
        db.session.delete(upvote)
        db.session.commit()
        upvotes_count = Upvotes.query.filter_by(event_id=event_id).count()
        return {'status': 'success', 'message': 'Upvote removed', 'upvotes_count': upvotes_count}, 200
    else:
        new_upvote = Upvotes(event_id=event_id, user_id=user_id)
        db.session.add(new_upvote)
        db.session.commit()
        upvotes_count = Upvotes.query.filter_by(event_id=event_id).count()
        return {'status': 'success', 'message': 'Event upvoted', 'upvotes_count': upvotes_count}, 200


@app.route('/event', methods=['GET', 'POST'])
def allEvents():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view events.')
        return redirect(url_for('login'))
    
    category = request.args.get('category', '')
    
    today = date.today()

    if category:
        events = Event.query.filter_by(eventCategory=category) #Apply filter if category is provided
    else:
        events=Event.query.filter(Event.eventDate >= today).all()

    for event in events:
        event.user_has_rsvped = RSVP.query.filter_by(event_id=event.id, user_id=user_id).first() is not None
        event.user_has_upvoted = Upvotes.query.filter_by(event_id=event.id, user_id=user_id).first() is not None
        event.upvotes_count = Upvotes.query.filter_by(event_id=event.id).count()

    return render_template('event.html',
                           title='All Events',
                           events=events)

@app.route('/deleteEvent', methods=['POST'])
def deleteEvent():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    event_id = request.form['event_id']
    event = Event.query.get(event_id)

    RSVP.query.filter_by(event_id=event_id).delete() #Delete from the rsvp page if its there

    Upvotes.query.filter_by(event_id=event_id).delete() #Delete it from the liked eventts page if its there

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('yourEvents'))


@app.route('/editProfile', methods=['GET', 'POST'])
def edit():
    user = Register.query.get(session['user_id'])
    if 'user_id' not in session:
        flash('Please log in to access this page')
        return redirect(url_for('login'))

    form=EditProfileForm()

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email #Ensuring the form is already filled when the user 

    if form.validate_on_submit():
        if form.email.data != user.email:
            exisitingUser = Register.query.filter_by(email=form.email.data).first()
            if exisitingUser:
                flash('Email already registered', 'danger')
                return redirect(url_for('edit'))
        
        user.username = form.username.data
        if form.email.data != user.email:
            user.email = form.email.data #Only updating the email if it is different
        db.session.commit()

        flash('Profile updated successfully!')
        return redirect(url_for('edit'))
    return render_template('editProfile.html',
                           title='Edit your profile',
                           form=form)

@app.route('/changePassword', methods=['GET','POST'])
def changePassword():
    user = Register.query.get(session['user_id'])
    if 'user_id' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    
    form = EditPasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(user.password, form.oldPassword.data):
            flash('Incorrect current password') #Checking whether the old password matches the one the user has inputted now
        else:
            user.password = generate_password_hash(form.newPassword.data)
            db.session.commit() #If the ol passwords match then commit new password and hash it to ensure security 
            flash('Password updated successfully')
            return redirect(url_for('edit'))
    return render_template('changePassword.html',
                           title='Change Password',
                           form=form)

@app.route('/likedEvents', methods=['GET'])
def liked():
    user_id = session.get('user_id')
    if 'user_id' not in session:
        flash('Please log in')
        return redirect(url_for('login'))
    
    likedEvents = Event.query.join(Upvotes).filter(Upvotes.user_id == user_id).all()
    for event in likedEvents:
        # Determine if the current user has RSVPed to this event
        event.user_has_rsvped = RSVP.query.filter_by(event_id=event.id, user_id=user_id).first() is not None #Ensuring that if the user has rsvpd, the rsvp button doesnt reset causing confusion

    return render_template('upvotedEvents.html',
                           title='Your liked events',
                           likedEvents=likedEvents)

@app.route('/editEvent', methods=['GET', 'POST'])
def editEvent():
    #Ensuring the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    event_id = request.args.get('event_id') or request.form.get('event_id')
    if not event_id:
        flash('No event specified for editing.')
        return redirect(url_for('yourEvents'))

    event = Event.query.filter_by(id=event_id, creator_id=user_id).first()

    # Initialising the form with the event's data for GET requests
    form = EventForm(obj=event)

    # Handle form submission
    if form.validate_on_submit():
        # Update the event fields with form data
        event.eventTitle = form.eventTitle.data
        event.eventDate = form.eventDate.data
        event.eventPlace = form.eventPlace.data
        event.eventCategory = form.eventCategory.data
        event.eventDescription = form.eventDescription.data

        # Commit changes to the database
        db.session.commit()

        flash('Event updated successfully!')
        return redirect(url_for('yourEvents'))

    return render_template(
        'editEvent.html',
        title='Edit Your Event',
        form=form,
        event=event
    )

