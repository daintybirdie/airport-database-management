#!/usr/bin/env python3
# Imports
import pg8000
import configparser
import sys
import bcrypt
from datetime import datetime

#  Common Functions
##     database_connect()
##     dictfetchall(cursor,sqltext,params)
##     dictfetchone(cursor,sqltext,params)
##     print_sql_string(inputstring, params)


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None

    # choose a connection target, you can use the default or
    # use a different set of credentials that are setup for localhost or winhost
    connectiontarget = 'DATABASE'
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y2?i2120_unikey',
            host='awsprddbs4836.shared.sydney.edu.au,
            password='password_from_config',
            user='y2?i2120_unikey')
        '''
        targetdb = ""
        if ('database' in config[connectiontarget]):
            targetdb = config[connectiontarget]['database']
        else:
            targetdb = config[connectiontarget]['user']

        connection = pg8000.connect(database=targetdb,
                                    user=config[connectiontarget]['user'],
                                    password=config[connectiontarget]['password'],
                                    host=config[connectiontarget]['host'],
                                    port=int(config[connectiontarget]['port']))
        connection.run("SET SCHEMA 'airline';")
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection

######################################
# Database Helper Functions
######################################
def dictfetchall(cursor,sqltext,params=[]):
    """ Returns query results as list of dictionaries."""
    """ Useful for read queries that return 1 or more rows"""

    result = []
    
    cursor.execute(sqltext,params)
    if cursor.description is not None:
        cols = [a[0] for a in cursor.description]
        
        returnres = cursor.fetchall()
        if returnres is not None or len(returnres > 0):
            for row in returnres:
                result.append({a:b for a,b in zip(cols, row)})

    print("returning result: ",result)
    return result

def dictfetchone(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    """ Useful for create, update and delete queries that only need to return one row"""

    result = []
    cursor.execute(sqltext,params)
    if (cursor.description is not None):
        print("cursor description", cursor.description)
        cols = [a[0] for a in cursor.description]
        returnres = cursor.fetchone()
        print("returnres: ", returnres)
        if (returnres is not None):
            result.append({a:b for a,b in zip(cols, returnres)})
    return result

##################################################
# Print a SQL string to see how it would insert  #
##################################################

def print_sql_string(inputstring, params=None):
    """
    Prints out a string as a SQL string parameterized assuming all strings
    """
    if params is not None:
        if params != []:
           inputstring = inputstring.replace("%s","'%s'")
    
    print(inputstring % params)

###############
# Login       #
###############

def check_login(username, password):
    '''
    Check Login given a username and password
    '''
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    print("checking login")

    if conn is None:
        return None
    cur = conn.cursor()

    try:
        sql = """SELECT *
                FROM Users
                    JOIN UserRoles ON
                        (Users.userroleid = UserRoles.userroleid)
                WHERE userid = %s"""
        print_sql_string(sql, (username,))
        
        result = dictfetchone(cur, sql, (username,))  # Fetch the first row
        
        if result:
            # part changed from
            user_data = result[0]  # Get the first (and only) dictionary from the list
            stored_password = user_data['password']  # Access password using key
            
            # Check if the entered password matches the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return result 
            # part changed ended 
            else:
                print("Invalid password")
                return None
        else:
            print("User not found")
            return None

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error Invalid Login")
    finally:
        cur.close()                     
        conn.close()                    
    
    return None


# helper function to hash

def hash_and_update_all_passwords():
    conn = database_connect()
    if conn is None:
        return
    cur = conn.cursor()

    try:
        cur.execute("SELECT userid, password FROM Users;")
        users = cur.fetchall()

        for userid, old_password in users:
            hashed_password = bcrypt.hashpw(old_password.encode('utf-8'), bcrypt.gensalt())
            
            cur.execute("UPDATE Users SET password = %s WHERE userid = %s;", (hashed_password.decode('utf-8'), userid))
        
        conn.commit()  
        print("All passwords updated successfully.")

    except Exception as e:
        conn.rollback()
        print("An error occurred:", e)
    
    finally:
        cur.close()
        conn.close()



    
########################
#List All Items#
########################

# Get all the rows of users and return them as a dict
def list_users():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                    FROM users """
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        import traceback
        traceback.print_exc()
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

def list_userroles():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                    FROM userroles """
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

########################
#List Single Items#
########################

# Define a set of allowed attribute names to prevent SQL injection
ALLOWED_ATTRIBUTES = {"firstname", "lastname", "userroleid", "password", "userid"}  # Add all valid attributes here

def list_users_equifilter(attributename, filterval):
    if attributename.lower().strip() not in ALLOWED_ATTRIBUTES:
        print(f"Invalid attribute name: {attributename}")
        return None
    
    conn = database_connect()
    if conn is None:
        return None
    
    cur = conn.cursor()
    val = None

    try:
        # Use parameterized queries to prevent SQL injection
        sql = f"""SELECT *
                    FROM users
                    WHERE {attributename} = %s;"""
        val = dictfetchall(cur, sql, (filterval,))
    
    except Exception:
        print("Error Fetching from Database: ")

    finally:
        cur.close()
        conn.close()

    return val

    # Return the resul
    


########################### 
#List Report Items #
###########################
    
# # A report with the details of Users, Userroles
def list_consolidated_users():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                FROM users 
                    JOIN userroles 
                    ON (users.userroleid = userroles.userroleid) ;"""
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict

def list_user_stats():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT userroleid, COUNT(*) as count
                FROM users 
                    GROUP BY userroleid
                    ORDER BY userroleid ASC ;"""
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

####################################
##  Search Items - inexact matches #
####################################

# Search for users with a custom filter
# filtertype can be: '=', '<', '>', '<>', '~', 'LIKE'
def search_users_customfilter(attributename, filtertype, filterval):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None

    # Set up the rows as a dictionary
    cur = conn.cursor()
    val = None

    # arrange like filter
    filtervalprefix = ""
    filtervalsuffix = ""
    if str.lower(filtertype) == "like":
        filtervalprefix = "'%"
        filtervalsuffix = "%'"
        
    try:
        # Retrieve all the information we need from the query
        sql = f"""SELECT *
                    FROM users
                    WHERE lower({attributename}) {filtertype} {filtervalprefix}lower(%s){filtervalsuffix} """
        print_sql_string(sql, (filterval,))
        val = dictfetchall(cur,sql,(filterval,))
    except:
        # If there are any errors, we print something nice and return a null value
        import traceback
        traceback.print_exc()
        print("Error Fetching from Database: ", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return val


#####################################
##  Update Single Items by PK       #
#####################################


def update_single_user(userid, firstname, lastname, userroleid, password):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if conn is None:
        # If a connection cannot be established, send a Null object
        return None
    
    # Set up the cursor
    cur = conn.cursor()
    val = None

    # Data validation checks are assumed to have been done in route processing

    try:
        setitems = []
        values = []
        #change start
        if firstname is not None:
            setitems.append("firstname = %s")
            values.append(firstname)
        if lastname is not None:
            setitems.append("lastname = %s")
            values.append(lastname)
        if userroleid is not None:
            setitems.append("userroleid = %s::bigint")
            values.append(userroleid)
        if password is not None:
            #change made from
            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            setitems.append("password = %s")
            values.append(hashed_password)
            # changes finished
        # Retrieve all the information we need from the query
        if setitems:
            sql = f"""UPDATE users
                        SET {', '.join(setitems)}
                        WHERE userid = %s;"""
            values.append(userid)  # Append the userid for the WHERE clause
            # changes end
            print_sql_string(sql, tuple(values))  # Pass values as a tuple
            cur.execute(sql, tuple(values))  # Execute with parameters
            conn.commit()
            val = cur.fetchone()  # Assuming you want to return the updated user

    except Exception:
        conn.rollback()
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database: ")

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # Return our struct
    return val


##  Insert / Add

def add_user_insert(userid, firstname, lastname, userroleid, password):
    """
    Add a new User to the system
    """
    # Data validation checks are assumed to have been done in route processing

    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # end of change

    sql = """
        INSERT into Users(userid, firstname, lastname, userroleid, password)
        VALUES (%s, %s, %s, %s, %s);
    """
    print_sql_string(sql, (userid, firstname, lastname, userroleid, hashed_password))
    try:
        # Try executing the SQL and get from the database
        cur.execute(sql, (userid, firstname, lastname, userroleid, hashed_password))
        
        r = []
        conn.commit()                   # Commit the transaction
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except Exception:
        conn.rollback()
        print("Unexpected error adding a user:")
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        raise


##  Delete
###     delete_user(userid)
def delete_user(userid):
    """
    Remove a user from your system
    """
    # Data validation checks are assumed to have been done in route processing
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = f"""
        DELETE
        FROM users
        WHERE userid = '{userid}';
        """

        cur.execute(sql,())
        conn.commit()                   # Commit the transaction
        r = []
        # r = cur.fetchone()
        # print("return val is:")
        # print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error deleting  user with id ",userid, sys.exc_info()[0])
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        raise

#####################################
# ALL METHODS BELOW WERE CREATED BY THE STUDENT

def get_airports_paginated(offset=0, limit=50):
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = "SELECT * FROM airports ORDER BY airportid OFFSET %s LIMIT %s"
        cur.execute(sql, (offset, limit))
        airports = cur.fetchall()
        return airports
    except pg8000.DatabaseError:
        return f"Database Error"
    except pg8000.DataError:
        return f"Data Error"
    except pg8000.OperationalError:
        return f"Operational Error"
    except Exception as e:
        return f"Unexpected error adding airport"
    finally:
        cur.close()
        conn.close()

def get_airport_count():
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT COUNT(*) FROM airline.airports"""
        cur.execute(sql)
        count = cur.fetchone()[0]
        return count
    except Exception:
        print(f"Error fetching airports")
        return None
    finally:
        cur.close()
        conn.close()


def get_all_airports_alphabetic():
    conn = database_connect()
    cur = conn.cursor()
    try:
        cur.execute("SELECT airportid, name, iatacode, city, country FROM airline.airports ORDER BY name")
        return cur.fetchall()  
    except Exception:
        print(f"Error fetching airports")
        return []
    finally:
        cur.close()
        conn.close()

def get_airport_by_id(airport_id):
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT airportid, name, iatacode, city, country FROM airports WHERE airportid = %s"""
        cur.execute(sql, (airport_id,))
        airport = cur.fetchone()
        return airport
    except Exception:
        print(f"Error fetching airport by ID")
        return None
    finally:
        cur.close()
        conn.close()

def add_airport(airport_id, name, iatacode, city, country):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    cur = conn.cursor()
    try:
        insert_sql = """
        INSERT INTO airports (airportid, name, iatacode, city, country)
        VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, (airport_id, name, iatacode, city, country))
        conn.commit()
        return True
    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except pg8000.DataError:
        conn.rollback()
        return f"Data Error"
    except pg8000.OperationalError:
        conn.rollback()
        return f"Operational Error"
    except pg8000.IntegrityError:
        conn.rollback()
        return f"Integrity Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error adding airport"
    finally:
        cur.close()
        conn.close()


def airport_exists_name(name):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    
    cur = conn.cursor()
    try:
        sql = """
        SELECT COUNT(*)
        FROM airports
        WHERE name = %s;
        """
        cur.execute(sql, (name,))
        count = cur.fetchone()[0]
        return count > 0  
    except Exception:
        return f"Error checking for existing airport"
    finally:
        cur.close()
        conn.close()

def airport_exists_code(iatacode):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    
    cur = conn.cursor()
    try:
        sql = """
        SELECT COUNT(*)
        FROM airports
        WHERE iatacode = %s;
        """
        cur.execute(sql, (iatacode,))
        count = cur.fetchone()[0]
        return count > 0  
    except Exception as e:
        return f"Error checking for existing airport"
    finally:
        cur.close()
        conn.close()


def delete_airport(code):
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        # Step 1: Check for any future flights involving the airport
        current_time = datetime.now()
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        sql_check_flights = """
            SELECT flightid FROM airline.flights
            WHERE (departureairportid = %s OR arrivalairportid = %s)
            AND (arrivaltime > %s)
        """
        sql_get_airportid = """
            SELECT airportid
            FROM airline.airports
            WHERE iatacode = %s
        """
        cur.execute(sql_get_airportid, (code.upper(),))
        airport_id = cur.fetchone()[0]
        print(f'attempting to print aiport id {airport_id}')
        cur.execute(sql_check_flights, (int(airport_id), int(airport_id), current_time))
        future_flights = cur.fetchall()


        if future_flights:
            return "Cannot delete airport. There are upcoming flights associated with this airport."




        # Step 2: Proceed with flight and airport deletion if no future flights found
        sql_delete_flight = """
        DELETE FROM airline.flights
        WHERE ((arrivalairportid = %s) AND (%s > arrivaltime)) OR ((departureairportid = %s) AND (%s > departuretime))
        """
        sql_delete_airport = """DELETE FROM airline.airports WHERE iatacode = %s"""
        cur.execute(sql_delete_flight,(airport_id,current_time,airport_id, current_time))
        cur.execute(sql_delete_airport, (code,))
        conn.commit()


        if cur.rowcount > 0:
            return airport_id  # Deletion successful
        else:
            return "No airport found with the specified IATA code."


    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except pg8000.DataError:
        conn.rollback()
        return f"Data Error"
    except pg8000.OperationalError:
        conn.rollback()
        return f"Operational Error"
    except pg8000.IntegrityError:
        conn.rollback()
        return f"Integrity Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error removing airport"
    finally:
        cur.close()
        conn.close()



def get_next_airport_id():
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT MAX(airportid) FROM airline.airports"""
        cur.execute(sql)
        max_id = cur.fetchone()[0]
        return max_id + 1 if max_id is not None else 1 
    except Exception as e:
        print(f"Error Retrieving max id")
        return None
    finally:
        cur.close()
        conn.close()

def get_airport_by_iatacode(code):
    conn = database_connect()  
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = "SELECT airportid, name, iatacode, city, country FROM airline.airports WHERE iatacode = %s"
        cur.execute(sql, (code,))  
        airport_info = cur.fetchone()  
        
        if airport_info is None:  
            return None 
        return airport_info  
    except pg8000.DatabaseError:
        return f"Database Error"
    except Exception:
        return f"Unexpected error retrieving airport information"
    finally:
        cur.close()  
        conn.close()  

    
def airport_summary():
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT country, COUNT(country) FROM airline.airports 
        GROUP BY country ORDER BY COUNT(*) DESC"""
        cur.execute(sql)
        summary = cur.fetchall()
        return summary
    except Exception:
        result = f"Error retrieving summary max"
        return result
    finally:
        cur.close()
        conn.close()

def update_airport_name(airport_id, new_name):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    cur = conn.cursor()
    try:
        sql = """
        UPDATE airline.airports  
        SET name = %s 
        WHERE airportid = %s
        """
        cur.execute(sql, (new_name, airport_id))
        conn.commit()
        if cur.rowcount == 0:
            return False
        return True
    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error updating airport name"
    finally:
        cur.close()
        conn.close()

def update_airport_iatacode(airport_id, new_iatacode):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    cur = conn.cursor()
    try:
        sql = """
        UPDATE airline.airports 
        SET iatacode = %s 
        WHERE airportid = %s
        """
        cur.execute(sql, (new_iatacode, airport_id))
        conn.commit()
        if cur.rowcount == 0:
            return False
        return True
    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error updating airport IATA code"
    finally:
        cur.close()
        conn.close()

def update_airport_city(airport_id, new_city):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    cur = conn.cursor()
    try:
        sql = """
        UPDATE airline.airports 
        SET city = %s 
        WHERE airportid = %s
        """
        cur.execute(sql, (new_city, airport_id))
        conn.commit()
        if cur.rowcount == 0:
            return False
        return True
    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error updating airport city"
    finally:
        cur.close()
        conn.close()

def update_airport_country(airport_id, new_country):
    conn = database_connect()
    if conn is None:
        return "Failed to connect to the database."
    cur = conn.cursor()
    try:
        sql = """
        UPDATE airline.airports  
        SET country = %s 
        WHERE airportid = %s
        """
        cur.execute(sql, (new_country, airport_id))
        conn.commit()
        if cur.rowcount == 0:
            return False
        return True
    except pg8000.DatabaseError:
        conn.rollback()
        return f"Database Error"
    except Exception:
        conn.rollback()
        return f"Unexpected error updating airport country"
    finally:
        cur.close()
        conn.close()
