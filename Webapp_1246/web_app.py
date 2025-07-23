from routes import *
import sys


# Starting the python applicaiton
if __name__ == '__main__':
    # database.hash_and_update_all_passwords()
    print("-"*70)
    print("""If you are on the server: Please open your browser to: http://soitpa10005.shared.sydney.edu.au:"""+portchoice+"""/""")
    print("-"*70)
    print("-"*70)
    print("""If you are on Linux/Your Own Computer: Please open your browser to: http://127.0.0.1:"""+portchoice+"""/""")
    print("-"*70)
    page = {'title' : 'ISYS2120 Assignment'}

 #######################################
 # Changes I made   
 # Redirect stdout and stderr to /dev/null
    class NullWriter:
        def write(self, arg):
            pass

        def flush(self):
            pass

    sys.stdout = NullWriter()  
    sys.stderr = NullWriter()  

    ###############################
    app.run(debug=False, host='0.0.0.0', port=int(portchoice))
