"""
Simple script to help setup and configure a site


"""

from collections import OrderedDict

import sys

import re

from CoderPad.constants import DEFAULT_DB, CONFIG_FILE, load_config, save_config
from CoderPad.models import get_db_context, db, User


def py23_input(prompt=''):
    try:
        return raw_input(prompt)
    except:
        return input(prompt)

def valid_input(prompt,test=lambda x:bool(x),error_msg="Invalid input",allow_null=False,default=None):
    if default and not allow_null:
        allow_null = True
    while True:
        result = py23_input(prompt)
        if test(result):
            return result
        if not result and allow_null:
            return default
        print(error_msg)

def ask_yesno(prompt,choices='yn',error_msg="Invalid Input",default=None):
    result = valid_input(prompt,
                       test=lambda x:len(x) and x[0].lower() in choices,
                       error_msg=error_msg,allow_null=default and default in choices)

    if default and not result:
        result = default
    return result[0].lower() == choices[0]

def email_input(prompt,error_msg="please enter a valid email address",
                allow_null=False,default=None):
    if default and not allow_null:
        allow_null=True
    result = valid_input(prompt,
                       test=lambda x: "@" in x and x.split("@",1)[-1].count(".") >= 1,
                       error_msg=error_msg,allow_null=allow_null)
    if not result and default:
        return default
    return result

def choice_input(prompt,choices,error_msg="'{result}' is not a valid selection",default=None):
    result = valid_input(prompt,
                       test=lambda x:x in choices,
                       error_msg=error_msg,allow_null=default in choices)
    if default and not result:
        return default
    return result

def setup_email(args,current_config):
    current_from_email = current_config.get('email_from',None)
    current_config['email_from'] = email_input("Enter From Address({email}):".format(email=current_from_email),default=current_from_email)

    current_email_subj = current_config.get('email_subject', "You have been invited to a coderpad session")
    current_config['email_subject'] = valid_input("(current:{subject})\nEnter SubjectLine:".format(subject=current_email_subj), default=current_email_subj )


def configure_stmp(args,current_config):
    current_server = current_config.get('email_server','localhost')
    current_user = current_config.get('email_user','')
    current_password = current_config.get('email_pass','')
    email_server = py23_input("STMP Server (%s):"%current_server)
    if not email_server:
        email_server=current_server
    email_user = py23_input("STMP Username(%s):"%repr(current_user))
    if not email_user:
        email_user=current_user
    email_pass = py23_input("STMP Password(%s):" % repr(current_password))
    if not email_pass:
        email_pass = current_password
    current_config['stmp_server']=email_server
    current_config['stmp_username']=email_user
    current_config['stmp_password']=email_pass

def create_prompt(args,current_config):
    current_prompt = current_config.get('prompt','')
    print "Existing Prompt:"
    print current_prompt
    print "------------\nLeave new prompt blank to use above prompt\n------"
    lines = [py23_input("Enter your prompt (empty line when done):"),]
    if lines[0]:
        lines.extend(list(iter(py23_input,"")))
    prompt =  "\\n".join(lines)
    if not prompt.strip():
        current_config['prompt']=current_prompt
    else:
        current_config['prompt']=prompt

def create_admin_user(args,current_config):
    db_uri = current_config.get('db_uri',None)
    if not db_uri:
        print("Database URI Not Found Creating ...")
        print("Default Database is %s"%(DEFAULT_DB,))
        db_uri = py23_input("Enter Your Database URI sqlite3://...?")
        if not db_uri:
            use_default = py23_input("use default(%s)[y/N]?"%(DEFAULT_DB,)).lower().startswith("y")
            if use_default:
                db_uri = DEFAULT_DB
            else:
                print("Ok Leaving... re-run to try again")
                sys.exit(-1)

        while not db_uri.startswith("sqlite",'postgresql','mysql'):
            print("Database URI should look like mysql://<user>:<pw>@<host>:<port>/<db_name>")
            db_uri = py23_input("Enter Your Database URI sqlite3://...?")

    with get_db_context(db_uri.strip()):
        db.create_all()
        username = valid_input("Enter Username:",
                               test=lambda x:User.query.filter_by(username=x).count()==0,
                               error_msg="That name is already taken!")
        password = valid_input("Enter Password:")
        email = valid_input("Enter Email:",
                            test=lambda e:"@" in e and e.split("@",1)[-1].count(".") >= 1,
                            error_msg="please enter a valid email address!")
        realname = valid_input("Enter realname:",lambda x:" " in x)
        user = User.get_or_create(username,password,realname,email)
        user.is_admin = True
        db.session.commit()

def wizard(args,current_config=None):
    if not current_config:
        current_config=load_config()
    curr_host =current_config.get('host','127.0.0.1')
    curr_port =current_config.get('port','8080')
    if ask_yesno("Update Host (%s:%s)[y/n]?"%(curr_host,curr_port)):
        current_config['host'] = py23_input("Enter Host(%s):"%curr_host) or curr_host
        current_config['port'] = py23_input("Enter Port(%s):"%curr_port) or curr_port
    curr_db_uri = current_config.get('db_uri',DEFAULT_DB)
    if ask_yesno("Update DB URI (%s)[y/n]?" % curr_db_uri):
        current_config['db_uri'] = py23_input("Enter DB URI:") or curr_db_uri

    if ask_yesno("Create A Prompt Message[y/n]?"):
        create_prompt(args,current_config)
    if ask_yesno("Create Admin User[y/n]?"):
        create_admin_user(args,current_config)
    if ask_yesno("Configure Email[y/n]?"):
        configure_stmp(args,current_config)
        setup_email(args,current_config)
    save_config(current_config)


def GetParser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host',nargs="?",help='which host to serve on(0.0.0.0 = all available interfaces)',default=None)
    parser.add_argument('port',nargs="?",help='set the port number to serve on',default=None)
    parser.add_argument("-w","--wizard",action='store_true',help="Use wizard prompts to setup your whole config")
    parser.add_argument("--create-prompt",action='store_true',help="Create The Prompt that appears at the top of righthand chat panel")
    parser.add_argument("--configure-stmp",action='store_true',help="Setup email credentials for stmp email notifications")
    parser.add_argument("--setup-email",action='store_true',help="Setup email credentials for stmp email notifications")
    parser.add_argument("--create-admin",action='store_true',help="Create an admin account")
    parser.add_argument("-d",'--database-uri',help="set the uri string for the database connection")
    return parser

def DoSetupCoderpadSite(args=None):
    current_config = load_config()
    parser = GetParser()
    if not args or isinstance(args,(list,tuple)):
        args = parser.parse_args(args)

    if args.wizard:
        return wizard(args,current_config)
    action_flag=0
    if args.database_uri:
        action_flag = 1
        current_config['db_uri'] = args.database_uri
    else:
        current_config['db_uri'] = current_config.get('db_uri',DEFAULT_DB)
    if args.host:
        action_flag = 1
        current_config['host'] = args.host
    else:
        current_config['host'] = current_config.get('host', "127.0.0.1")
    if args.port:
        action_flag = 1
        current_config['port'] = args.host
    else:
        current_config['port'] = current_config.get('port', "8080")

    if args.create_prompt:
        action_flag = 1
        create_prompt(args,current_config)
    if args.create_admin:
        action_flag = 1
        create_prompt(args, current_config)
    if args.setup_email:
        action_flag = 1
        setup_email(args, current_config)
    if not action_flag:
        parser.print_help()
    else:
        save_config(current_config)



if __name__ == "__main__":
    DoSetupCoderpadSite()