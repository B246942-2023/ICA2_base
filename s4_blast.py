#!/usr/bin/python3
#=================================================  module import==================================================
import os
import subprocess
import shutil
import sys
import time

#=================================================function define==================================================
# to use linux commands in python
def linux_commands( str ):
    result = subprocess.run(str, shell = True,capture_output = True,text = True)
    return result.stdout ,result.stderr
# check/make/clear output_directory
def check_output_directory( outfolder ):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    else :
        shutil.rmtree(outfolder)
        os.makedirs(outfolder)
# write data to file
def writefile(data, filename):
    with open(filename, 'w') as file:
        file.write(data)
# handle the usr's input (used in menu choices 2)
def process_input(input_text):
    lines = input_text.strip().split()
    return '\n'.join(lines)
# handle duplicate_ids (used in menu choices 1)
def remove_duplicate_ids(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    processing = False
    ncbi_ids = set()
    processed_lines = []

    for line in lines:
        if line.startswith('@'):#start to collect data
            processing = True
            processed_lines.append(line)
            continue

        if processing:
            ncbi_ids.add(line.strip())
        else:
            processed_lines.append(line)

    # add all id in to the file again
    for id in ncbi_ids:
        processed_lines.append(id + '\n')

    with open(filepath, 'w') as file:
        file.writelines(processed_lines)
# make a blast list (menu choices 1)
def make_blast_list():
    # Make the blast list
    while True:
        # make the filename
        outfolder = "s4_out"
        filename = f'{outfolder}/seqBLAST_pre.txt'

        # write the first two line
        header = 'BLASTseqs'.center(100)
        separator = 'Quene line'.center(100,"@")
        content = f"{header}\n{separator}\n"

        # Handle autoscreen.txt 
        print("AutoScreen".center(100,"="))
        print("Results".center(100))
        print()   
        with open('s3_out/autoscreen.txt', 'r') as file:
            print(file.read()) 
        flag_autoscreen = input("Do you use the ID in 'autoscreen.txt'in BLAST?(y/n): ").lower()
        if flag_autoscreen == "y":
            if os.path.exists('s3_out/autoscreen.txt'):
                with open('s3_out/autoscreen.txt', 'r') as file:
                    content += process_input(file.read()) + '\n'
            else:
                print("CAN'T FOUND autoscreen FILE!")

        # Handle the usrs input
        if input("Do you want to input some ID to BLAST BY YOURSELF (y/n): ").lower() == 'y':
            while True:
                print("\n\n")
                print("-".center(100,"-"))
                print("PLEASE PASTE(press Ctrl+D when finished):\n")
                user_input = sys.stdin.read()
                print()
                print("YOUR INPUT".center(100,"-"))
                print()
                print(process_input(user_input))
                print("-".center(100,"-"))
                print()
                if input("Do you want to input again?(y/n): ").lower() != 'y':
                    content += process_input(user_input) + '\n'
                    break
        writefile(content, filename)
        print("Current BLAST quene line".center(100,"-"))
        print("\n\n")
        with open(filename,"r") as file:
            print(file.read())
        print()
        print("-".center(100,"-"))
        print("\n\n")
        if input("Do you want to SAVE data?(y/n): ").lower() == 'y':
            print(f"Data have been saved".center(100,"="))
            break
#Menu
def menu():
    while True:
        #1 check the s4_out/seqBLAST_pre.txt status
        file_path = 's4_out/seqBLAST_pre.txt'
        #initialise the flags
        flag_BLAST_LIST = False
        flag_BLAST_runnings = False
        flag_FINISH = False
        if os.path.exists(file_path):
            flag_BLAST_LIST = True
            #check if there is a BLAST is running
            with open(file_path,"r") as file:
                content = file.read()
                if "Running" in content:
                    flag_BLAST_runnings = True
                if ("FINISH" in content) and (not flag_BLAST_runnings)  :
                    flag_FINISH = True
        else:
            flag_BLAST_LIST = False


        #2 Menu it self
        print("MENU_BLAST".center(100,"="))
        print()
        print(f"BLAST_LIST  Exist : {flag_BLAST_LIST}" .center(100))
        print(f"BLAST Running State : {flag_BLAST_runnings}" .center(100))
        print(f"BLAST FINISH State : {flag_FINISH}" .center(100))
        print(f"    BLAST saved folder : s4_out" )
        print()
        print(f'''    1.Read the BLAST_LIST
    2.Make a BLAST_LIST
    3.Start BLAST   
    4.Check/Monitor BLAST State
    5.Reset and Delete
    6.Quit''')
        print()
        print("=".center(100,"="))

        choices = input("Input your choices : ")
        if choices == "1":
            if flag_BLAST_LIST:
                with open(file_path,"r") as f:
                    print(f.read())
            else:
                print()
                print("No BLAST list , pls choose 2 to make one".center(100))
                print() 
            input("Press Enter to back the BLAST MENU".center(100,"-"))
            continue
        if choices == "2":
            if flag_BLAST_runnings == False:
                make_blast_list()
                remove_duplicate_ids(file_path)
            else:
                print("There is a BLAST running now, can't make a new one".center(100))
            continue
        if choices == "3":
            if flag_BLAST_runnings == True :
                print()
                print("BLAST is running , can't run new one")
                print()
            elif flag_BLAST_LIST == False:
                print()
                print("No BLAST list , pls choose 2 to make one".center(100))
                print()
            else:
                #copy all fasta file to a new folder to blast
                check_output_directory("s4_out/blast_copy")
                for file in os.listdir("s3_out"):
                    if file.endswith(".fasta"):
                        shutil.copy(f"s3_out/{file}",f"s4_out/blast_copy/{file}")
                count = 0
                while count <5: #run 5 blast at a same time
                    subprocess.Popen(["python3", "s4.1_runblast.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(0.3)
                    count+=1
                print()
                print("BLAST Start")
                print()
            input("Press Enter to continue".center(100,"-"))
            continue
        if choices == "4":
            if flag_FINISH:
                with open(file_path,"r") as f:
                    print(f.read())
                    input("Press Enter to back the BLAST MENU".center(100,"-"))
            elif flag_BLAST_runnings:
                continue_monitoring = True
                while continue_monitoring:
                    print("Monitoring On".center(100,"="))
                    with open(file_path, "r") as file:
                        content = file.read()
                    print(content)
                    print()
                    print("-".center(100,"-"))
                    out,error = linux_commands("ps -u $(whoami) -o pid,tty,time,cmd | grep [b]lastp | grep sh")
                    print(out)
                    print("-".center(100,"-"))
                    print()
                    print("Enter to Refresh".center(100))
                    stop = input("q to stop monitoring".center(100))
                    print()
                    print("-".center(100,"-"))
                    if stop == "q":
                        continue_monitoring = False
            else :
                print()
                print("No BLAST data or running process, pls start a BLAST".center(100)) 
                print()
                input("Press Enter to back the BLAST MENU".center(100,"-"))
            continue

        if choices == "5":
            print()
            if  flag_BLAST_runnings:
                if input("IMPORTANT: BLAST is running , still reset?(y/n)").lower() == "y":
                    for i in range(5):
                        linux_commands("pkill -f 'blastp' -u $(whoami)")
                        print()
                        print("RESETING".center(100))
                        out,error = linux_commands("ps -u $(whoami) -o pid,tty,time,cmd | grep [b]lastp | grep sh")
                        print(out)
                        print()
                        time.sleep(3)
                    check_output_directory( outfolder )
                    print("All BLAST data are delete".center(100,"-"))
            else:
                if input("Are you sure to delete ALL BLAST data?(y/n)").lower() == "y":
                    check_output_directory( outfolder )
                    print("All BLAST data are delete".center(100,"-"))
            continue
        if choices == "6":  
            break
        else:
            print("Wrong input")
#=====================================================main body==================================================

# make sure there is a folder
outfolder = "s4_out"
if not os.path.exists(outfolder):
        os.makedirs(outfolder)

# run blast menu
menu()







