import os
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer
from pyftpdlib.filesystems import AbstractedFS
from fpdf import FPDF

# Configure logging to record all actions
logging.basicConfig(filename='ftp_honeypot.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Define the home directory for the FTP server and the upload directory
home_dir = "/ftphome"
upload_dir = os.path.join(home_dir, "uploads")

# Create the directories if they don't exist
os.makedirs(home_dir, exist_ok=True)
os.makedirs(upload_dir, exist_ok=True)

# Add some files to the home directory for attackers to collect
passwords_content = """
user1:password123
admin:adminpass
guest:guestpass
root:rootpass
"""

pdf_content = "One hack at a time."

files_to_create = {
    'confidential.txt': 'This files are encrypted: confidential.txt',
    'passwords.txt': passwords_content,
    'project_plan.pdf': pdf_content
}

def create_pdf(file_path, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(file_path)

for file_name, content in files_to_create.items():
    file_path = os.path.join(home_dir, file_name)
    if not os.path.exists(file_path):
        if file_name.endswith('.pdf'):
            create_pdf(file_path, content)
        else:
            with open(file_path, 'w') as f:
                f.write(content)

class HoneypotFTPHandler(FTPHandler):
    def on_connect(self):
        logging.info(f"Connection from {self.remote_ip}:{self.remote_port}")

    def on_disconnect(self):
        logging.info(f"Disconnection from {self.remote_ip}:{self.remote_port}")

    def on_login(self, username):
        logging.info(f"Login with username: {username}")

    def on_login_failed(self, username, password):
        logging.info(f"Failed login with username: {username}, password: {password}")

    def on_file_sent(self, file):
        logging.info(f"File sent: {file}")

    def on_file_received(self, file):
        logging.info(f"File received: {file}")

    def on_incomplete_file_sent(self, file):
        logging.info(f"Incomplete file sent: {file}")

    def on_incomplete_file_received(self, file):
        logging.info(f"Incomplete file received: {file}")

    def ftp_STOR(self, file):
        logging.info(f"File upload initiated: {file}")
        super().ftp_STOR(file)
        logging.info(f"File upload detected: {file}")
        uploaded_file_path = os.path.join(self.fs.root, file)
        if os.path.exists(uploaded_file_path):
            os.rename(uploaded_file_path, os.path.join(upload_dir, file))
            logging.info(f"File moved to upload directory: {file}")

    def ftp_RETR(self, file):
        super().ftp_RETR(file)
        logging.info(f"File download detected: {file}")

    def ftp_LIST(self, path):
        super().ftp_LIST(path)
        logging.info(f"Directory listing requested: {path}")

    def ftp_NLST(self, path):
        super().ftp_NLST(path)
        logging.info(f"Directory listing requested: {path}")

    def on_command_received(self, command, *args):
        logging.info(f"Command received: {command} {args}")

    def ftp_USER(self, user):
        logging.info(f"USER command received: {user}")
        self.respond('331 Username ok, need password.')
        self.username = user

    def ftp_PASS(self, password):
        logging.info(f"PASS command received for user {self.username}: {password}")
        if self.username == 'user' and password == '12345':
            self.respond('230 Login successful.')
            self.authenticated = True
            self.fs = AbstractedFS(home_dir, self)
        elif self.username == 'anonymous':
            self.respond('230 Login successful.')
            self.authenticated = True
            self.fs = AbstractedFS(home_dir, self)
        else:
            self.respond('530 Login incorrect.')
            self.authenticated = False

    def ftp_PWD(self, line):
        logging.info(f"PWD command received")
        if self.authenticated:
            self.respond(f'257 "{self.fs.cwd}" is the current directory')
        else:
            self.respond('530 Please login with USER and PASS.')

    def ftp_SYST(self, line):
        logging.info(f"SYST command received")
        if self.authenticated:
            self.respond('215 UNIX Type: L8')
        else:
            self.respond('530 Please login with USER and PASS.')

    def ftp_FEAT(self, line):
        logging.info(f"FEAT command received")
        if self.authenticated:
            features = "211-Features:\n MDTM\n REST STREAM\n SIZE\n MLST type*;size*;modify*;\n MLSD\n UTF8\n211 End"
            self.respond(features)
        else:
            self.respond('530 Please login with USER and PASS.')

    def ftp_STAT(self, path):
        logging.info(f"STAT command received for path: {path}")
        if self.authenticated:
            status = f"211-FTP server status:\n Connected to: {self.remote_ip}\n {1} users (the maximum allowed is 5)\n Waiting for commands.\n211 End of status"
            self.respond(status)
        else:
            self.respond('530 Please login with USER and PASS.')

    def ftp_NOOP(self, line):
        logging.info(f"NOOP command received")
        self.respond('200 NOOP ok.')

    def ftp_QUIT(self, line):
        logging.info(f"QUIT command received")
        self.respond('221 Goodbye.')
        self.close_when_done()

def main():
    try:
        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Create a user with full permissions (read/write)
        authorizer.add_user("user", "12345", home_dir, perm="elradfmw")

        # Create an anonymous user with read-only permissions
        authorizer.add_anonymous(home_dir, perm="elr")

        # Instantiate the FTP handler class
        handler = HoneypotFTPHandler
        handler.authorizer = authorizer

        # Define a customized banner
        handler.banner = "Welcome to the FTP Server."

        # Specify the FTP server address and port
        address = ('0.0.0.0', 21)
        server = ThreadedFTPServer(address, handler)

        # Passive mode configuration
        server.handler.passive_ports = range(60000, 65535)

        # Set a limit for connections
        server.max_cons = 256
        server.max_cons_per_ip = 5

        # Start the FTP server
        print("Starting FTP honeypot server...")
        logging.info("Starting FTP honeypot server...")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Error starting FTP honeypot server: {e}")
        print(f"Error starting FTP honeypot server: {e}")

if __name__ == "__main__":
    main()

