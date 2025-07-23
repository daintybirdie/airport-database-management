# Importing the Flask Framework

from flask import *
import database
import configparser
import re

# appsetup

page = {}
session = {}

# Defined regex patterns for validation
alphabetic_pattern = re.compile(r'^[A-Za-z\s]+$')  # Allow letters and spaces
iata_pattern = re.compile(r'^[A-Z]{3}$')  # Exactly 3 uppercase letters

# Initialise the FLASK applicationf
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'

with app.test_request_context('/'):
    session['key'] = 'value'
    print(session['key'])  # This will print 'value'

# Debug = true if you want debug output on error ; change to false if you dont
app.debug = False


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '10000':
    print('ERROR: Please change config.ini as in the comments or Lab instructions')
    exit(0)

session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website (home page)
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))

        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        search = database.search_users_customfilter(request.form['searchfield'],"~",request.form['searchterm'])
        print(search)
        
        users_listdict = None

        if search == None:
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if search == None or len(search) < 1:
            flash(f"No items found for search: {request.form['searchfield']}, {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = search
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Users search by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return render_template('search_users.html', page=page, session=session)
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    Delete a user
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None

    print("request form is:")
    newdict = {}
    print(request.form)

    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))

######
## Edit user
######
@app.route('/users/edit/<userid>', methods=['POST','GET'])
def edit_user(userid):
    """
    Edit a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Edit user details'

    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    user = users_listdict[0]
    validupdate = False

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that at least one value is available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        # assuming GET request, need to setup for this
        return render_template('edit_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles(),
                           user=user)


######
## add items
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that all values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not add user without a userid")
            return redirect(url_for('add_user'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['userid'], newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())
    

##################################################
# ALL METHODS BELOW WERE CREATED BY THE STUDENT

@app.route('/airports/add', methods=['GET', 'POST'])
def add_airport():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        country = request.form.get('country')
        iatacode = request.form.get('iatacode')  
        city = request.form.get('city')            
        
        # Validate inputs
        if not validate_airport_data(name, iatacode, city, country):
            return redirect(url_for('add_airport'))

        # Get the next airport_id
        airport_id = database.get_next_airport_id()

        # Convert IATA code to uppercase, to ensure uniformity and easier to query for equality
        iatacode = iatacode.upper().strip()
        name = name.title().strip()
        city = city.title().strip()
        country = country.title().strip()

        result = database.add_airport(airport_id, name, iatacode, city, country)
        
        if result is True: 
            flash(f'Airport with ID {airport_id} added successfully!')
            flash('Specified airport is the last row')
            return redirect(url_for('list_airports'))
        else:
            flash(f'Error adding airport: {result}')

    return render_template('add_airport.html', page={'title': 'Add Airport'}, session=session)


def validate_airport_data(name, iatacode, city, country):
    name = name.title()
    iatacode = iatacode.upper()
    # Validate Name
    if not alphabetic_pattern.match(name):
        flash('Invalid airport name. Only alphabetic characters are allowed.')
        return False

    # Validate IATA code
    if not iata_pattern.match(iatacode.upper()):  # Check against uppercase version
        flash('Invalid IATA code. It must be exactly 3 letters.')
        return False

    # Check for existing records
    if database.airport_exists_name(name):
        flash('An airport with this name already exists.')
        return False
    
    # Check for existing records
    if database.airport_exists_code(iatacode):
        flash('An airport with this IATA code already exists.')
        return False
    # Validate City
    if not alphabetic_pattern.match(city):
        flash('Invalid city name. Only alphabetic characters are allowed.')
        return False

    # Validate Country
    if not alphabetic_pattern.match(country):
        flash('Invalid country name. Only alphabetic characters are allowed.')
        return False

    return True


@app.route('/airports', methods=['GET'])
def list_airports():
    page = request.args.get('page', 1, type=int)  # Get the current page number from the query parameters
    limit = 50
    offset = (page - 1) * limit

    airports = database.get_airports_paginated(offset=offset, limit=limit)

    # Check if the list is empty
    if airports is None:
        flash('Error fetching airports. Please try again.')
        return redirect(url_for('list_airports')) 

    # Fetch total count of airports for pagination
    total_airports = database.get_airport_count()  

    if total_airports is None:
        flash('Error fetching total count of airports. Please try again.')
        return redirect(url_for('list_airports'))

    # Calculate total pages
    total_pages = (total_airports // limit) + (1 if total_airports % limit > 0 else 0)

    return render_template('list_airports.html', 
                           airports=airports, 
                           page={'title': 'View Airports', 'current_page': page, 'total_airports': total_airports, 'total_pages': total_pages}, 
                           session=session)





@app.route('/airports/remove/', methods=['GET', 'POST'])
def remove_airport():
    # Fetch all airports for dropdown
    airports = database.get_all_airports_alphabetic()  
    selected_airport = None  

    if request.method == 'POST':
        iatacode = request.form.get('iatacode')

        # Fetch selected airport details for confirmation
        selected_airport = database.get_airport_by_iatacode(iatacode)
        if selected_airport:
            return render_template('remove_airport.html', 
                                   page={'title': 'Remove Airport'}, 
                                   airports=airports, 
                                   selected_airport=selected_airport,
                                   session=session)

        flash('No airport found with the given IATA code.')
        return redirect(url_for('list_airports'))

    return render_template('remove_airport.html', page={'title': 'Remove Airport'}, airports=airports, session=session)

@app.route('/airports/remove/final/', methods=['POST'])
def remove_airport_final():
    iatacode = request.form.get('iatacode')

    # Attempt to delete the airport
    result = database.delete_airport(str(iatacode).upper())
    result = str(result)
    if (len(result) == 1):
        flash(f'Airport removed successfully! Removed airport with ID originally {result}') 
    else:
        flash(f'Error removing airport: {result}')

    return redirect(url_for('list_airports'))




@app.route('/airports/get_airport_by_id/', methods=['GET', 'POST'])
def get_airport_by_id():
    airport_data = None  

    if request.method == 'POST':
        airport_id = request.form.get('airportid')  

        airport_data = database.get_airport_by_id(airport_id)
        if not(airport_data):
            flash(f'Aiport with id: {airport_id} does not exist.')

    return render_template('get_airport_by_id.html', 
                           page={'title': 'Get Airport By Id'}, 
                           airport=airport_data, 
                           session = session)  

@app.route('/airports/get_summary')
def get_summary():
    data = database.airport_summary()
    return render_template('airport_summary.html', page = {'title': 'Airport Summary'}, airport = data, session = session)


@app.route('/airports/update_name/', methods=['GET', 'POST'])
def update_airport_name():
    airport_info = None  
    # Fetch all airports for dropdown
    airports = database.get_all_airports_alphabetic()  
    if request.method == 'POST':
        # Update the name based on selected IATA code
        if 'iatacode' in request.form and 'new_name' not in request.form:
            iatacode = request.form.get('iatacode')
            airport_info = database.get_airport_by_iatacode(iatacode)  # Fetch airport info

            if airport_info is None:
                flash('No airport found with the given IATA code.', 'danger')
            else:
                # Render to display current name
                return render_template('update_airport_name.html', 
                                       page={'title': 'Update Airport Name'}, 
                                       airport_info=airport_info, 
                                       airports=airports,  
                                       session=session)

        # Update airport name
        elif 'new_name' in request.form:
            iatacode = request.form.get('iatacode')  
            airport_info = database.get_airport_by_iatacode(iatacode)  
            
            new_name = request.form.get('new_name')

            if airport_info is not None:
                airport_id = airport_info[0]
                current_name = airport_info[1].strip()
                if current_name.casefold().split() == new_name.casefold().split():
                    flash('Attempting to change the name to the current name. No changes made.', 'warning')
                    return redirect(url_for('update_airport_name'))
                new_name = new_name.title().strip() # case & whitespace insensitivity
                if database.airport_exists_name(new_name):
                    flash('An airport with this name already exists.')
                    return redirect(url_for('update_airport_name'))
                if not alphabetic_pattern.match(new_name):
                     flash('Invalid airport name. Only alphabetic characters are allowed.')
                     return redirect(url_for('update_airport_name'))
                result = database.update_airport_name(airport_id, new_name)  
                if result is True:
                    flash(f'Airport name updated successfully for airport ID {airport_id}', 'success')
                    return redirect(url_for('list_airports'))
                else:
                    flash(f'Error updating airport name: {result}', 'danger')

    return render_template('update_airport_name.html', 
                           page={'title': 'Update Airport Name'}, 
                           airport_info=airport_info, 
                           airports=airports,  
                           session=session)



@app.route('/airports/update_iatacode/', methods=['GET', 'POST'])
def update_airport_iatacode():
    airport_info = None 
    # Fetch all airports for dropdown
    airports = database.get_all_airports_alphabetic()  
    if request.method == 'POST':
        # Update the IATA code based on selected IATA code
        if 'iatacode' in request.form and 'new_iatacode' not in request.form:
            iatacode = request.form.get('iatacode')
            airport_info = database.get_airport_by_iatacode(iatacode)  
            if airport_info is None:
                flash('No airport found with the given IATA code.', 'danger')
            else:
                # Render to display current IATA code
                return render_template('update_airport_iatacode.html', 
                                       page={'title': 'Update Airport IATA Code'}, 
                                       airport_info=airport_info, 
                                       airports=airports,  
                                       session=session)

        # Update airport IATA code
        elif 'new_iatacode' in request.form:
            iatacode = request.form.get('iatacode')  
            airport_info = database.get_airport_by_iatacode(iatacode) 
            
            new_iatacode = request.form.get('new_iatacode')

            if airport_info is not None:
                airport_id = airport_info[0]
                current_iatacode = airport_info[2].strip()
                if current_iatacode.casefold().split() == new_iatacode.casefold().split():
                    flash('Attempting to change the iatacode to the current code. No changes made.', 'warning')
                    return redirect(url_for('update_airport_iatacode'))  
                new_iatacode = new_iatacode.upper().strip()
                if not iata_pattern.match(new_iatacode):
                    flash(f'Length of IATA Code should be exactly 3 letters and alphabetic!')
                    return redirect(url_for('update_airport_iatacode')) 
                if database.airport_exists_code(new_iatacode):
                    flash('An airport with this IATA code already exists.')
                    return redirect(url_for('update_airport_iatacode')) 
                result = database.update_airport_iatacode(airport_id, new_iatacode)  
                if result is True:
                    flash(f'Airport IATA code updated successfully for airport ID {airport_id}', 'success')
                    return redirect(url_for('list_airports'))
                else:
                    flash(f'Error updating airport IATA code: {result}', 'danger')
                    return redirect(url_for('update_airport_iatacode')) 

    return render_template('update_airport_iatacode.html', 
                           page={'title': 'Update Airport IATA Code'}, 
                           airport_info=airport_info, 
                           airports=airports,  
                           session=session)



@app.route('/airports/update_country/', methods=['GET', 'POST'])
def update_airport_country():
    airport_info = None  
    airports = database.get_all_airports_alphabetic()  
    
    if request.method == 'POST':
        # Check if only the IATA code is provided to display current info
        if 'iatacode' in request.form and 'new_country' not in request.form:
            iatacode = request.form.get('iatacode')
            airport_info = database.get_airport_by_iatacode(iatacode)  

            if airport_info is None:
                flash('No airport found with the given IATA code.', 'danger')
            else:
                # Render to display current country
                return render_template('update_airport_country.html', 
                                       page={'title': 'Update Airport Country'}, 
                                       airport_info=airport_info, 
                                       airports=airports,  
                                       session=session)

        iatacode = request.form.get('iatacode')
        airport_info = database.get_airport_by_iatacode(iatacode) 

        if airport_info is None:
            flash('No airport found with the given IATA code.', 'danger')
        else:
            if 'new_country' in request.form:
                new_country = request.form.get('new_country')
                airport_id = airport_info[0]
                current_country = airport_info[4].strip()
                if current_country.casefold().split() == new_country.casefold().split():
                    flash('Attempting to change the country to the current country. No changes made.', 'warning')
                    return redirect(url_for('update_airport_country'))
                new_country = new_country.title().strip() 
                if not alphabetic_pattern.match(new_country):
                    flash('Invalid country name. Only alphabetic characters are allowed.')
                    return redirect(url_for('update_airport_country'))
                result = database.update_airport_country(airport_id, new_country)  
                if result is True:
                    flash(f'Airport country updated successfully for airport ID {airport_id}', 'success')
                    return redirect(url_for('list_airports'))
                else:
                    flash(f'Error updating airport country: {result}', 'danger')
    
    return render_template('update_airport_country.html',
                           page={'title': 'Update Airport Country'},
                           airport_info=airport_info,
                           airports=airports,
                           session=session)



@app.route('/airports/update_city/', methods=['GET', 'POST'])
def update_airport_city():
    airport_info = None  
    airports = database.get_all_airports_alphabetic()  
    
    if request.method == 'POST':
        # Check if only the IATA code is provided to display current info
        if 'iatacode' in request.form and 'new_city' not in request.form:
            iatacode = request.form.get('iatacode')
            airport_info = database.get_airport_by_iatacode(iatacode)  

            if airport_info is None:
                flash('No airport found with the given IATA code.', 'danger')
            else:
                # Render to display current city
                return render_template('update_airport_city.html', 
                                       page={'title': 'Update Airport City'}, 
                                       airport_info=airport_info, 
                                       airports=airports,  
                                       session=session)

        iatacode = request.form.get('iatacode')
        airport_info = database.get_airport_by_iatacode(iatacode)  

        if airport_info is None:
            flash('No airport found with the given IATA code.', 'danger')
        else:
            if 'new_city' in request.form:
                new_city = request.form.get('new_city')
                airport_id = airport_info[0]
                current_city = airport_info[3].strip()
                if current_city.casefold().split() == new_city.casefold().split():
                    flash('Attempting to change the city to the current city. No changes made.', 'warning')
                    return redirect(url_for('update_airport_city'))
                new_city = new_city.title().strip()
                if not alphabetic_pattern.match(new_city):
                    flash('Invalid city name. Only alphabetic characters are allowed.')
                    return redirect(url_for('update_airport_city'))
                result = database.update_airport_city(airport_id, new_city) 
                if result is True:
                    flash(f'Airport city updated successfully for airport ID {airport_id}', 'success')
                    return redirect(url_for('list_airports'))
                else:
                    flash(f'Error updating airport city: {result}', 'danger')
    
    return render_template('update_airport_city.html', 
                           page={'title': 'Update Airport City'}, 
                           airport_info=airport_info, 
                           airports=airports,  
                           session=session)
