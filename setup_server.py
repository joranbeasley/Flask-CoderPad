from collections import OrderedDict


def py23_input(prompt):
    try:
        return raw_input(prompt)
    except:
        return input(prompt)
def load_config(fpath):
    try:
        return OrderedDict([x.strip() for x in line.split("=")] for line in open(fpath,'rb') if "=" in line)
    except:
        return OrderedDict()

def setup_email(args,current_config):
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
def create_prompt(args,current_config):
    current_prompt = current_config.get()
    print "Existing Prompt:"
    print current_prompt
    print "------------\nLeave new prompt blank to use above prompt\n------"
    lines = [py23_input("Enter your prompt (empty line when done):"),]
    if lines[0]:
        lines.extend(list(iter(py23_input,"")))
    prompt =  "\n".join(lines)
    if not prompt.strip():
        return current_prompt
    return prompt
def wizard(args):
    current_config=load_config()



def ParseArgs(args=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w","--wizard",action='store_true',help="Use wizard prompts to setup your whole config")
    parser.add_argument("--create-prompt",action='store_true',help="Create The Prompt that appears at the top of righthand chat panel")
    parser.add_argument("--setup-email",action='store_true',help="Setup email credentials for stmp email notifications")
    parser.add_argument("--create-admin",action='store_true',help="Create an admin account")
    parser.add_argument("-d",'--database-uri',help="set the uri string for the database connection")
    parser.add_argument('-p','--port',help='set the port number to serve on',default="8000")
    parser.add_argument('-h','--host',help='which host to serve on(0.0.0.0 = all available interfaces)',default="127.0.0.1")
    return parser.parse_args(args)


