#!/usr/bin/python3
#=================================================  module import==================================================
import os
import subprocess
import shutil
import sys
import time
import threading
#=================================================function define==================================================
# write data to file
def writefile(data, filename):
    with open(filename, 'w') as file:
        file.write(data)

# read the blastseq file and return a list of ids 
def read_sequence_names(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith("@"):
            blastlist_start = lines.index(line)  # find the @ line

        if line.startswith("*"):
            blasting_start = lines.index(line)       # find the * line

    blast_list = [line.strip() for line in lines[blastlist_start+1:blasting_start]]
    blasting_info = lines[blasting_start+1:]

    blasting_list = []
    for line in blasting_info:
        status = ""
        if line.strip():  #  not an empty line
            parts = line.split()
            seq_id = parts[0]
            status = parts[-1] 
        if status:
            blasting_list.append((seq_id, status))
    return blast_list,blasting_list

#update the file status
def wirte_status(id,status):
    with open('s4_out/seqBLAST_pre.txt', 'r+') as file:
        lines = file.readlines()
        # a flag to check the id exsitence
        flag_found = False
        # iterate over the lines to find the sequence ID
        #flag_first to find the sec id
        flag_second = False
        for index, line in enumerate(lines):
            if line.startswith(id):
                if flag_second:
                    lines[index] = f"{id.ljust(50)}{status.rjust(50)}\n"
                    flag_found = True
                flag_second = True

       
        # id not found, append it with the new status
        if not flag_found:
            lines.append(f"{id.ljust(50)}{status.rjust(50)}\n")
        
        # Write the updated content back to the file
        file.seek(0)  # Go to the start of the file
        file.writelines(lines)

#=====================================================main body==================================================
#1 start BLASTing ,add the BLASTing ********** line
file_path = 's4_out/seqBLAST_pre.txt'
with open('s4_out/seqBLAST_pre.txt',"r") as f:
    content = f.read()
if content.find("*") == -1:
    content += "BLASTing".center(100,"*")+"\n"
    writefile(content, file_path)

#2 obtain the current seqs and their status
blast_list,blasting_list=read_sequence_names(file_path)

# Now, we want to find sequences in blast_list that are not in blasting_list, means that id has not been  started a blast 
sequences_to_blast = [seq for seq, status in blasting_list]
new_sequences_to_blast = [seq for seq in blast_list if seq not in sequences_to_blast] #the file in new_sequences means they haven't been BLAST

#3 BLAST 
# If there is any seq in new_sequences_to_blast_list,it will be blast 
if new_sequences_to_blast:
    id = new_sequences_to_blast[0]
    wirte_status(id,"Running")
    fasta_file = f's4_out/blast_copy/{id}.fasta'
    output_file = f's4_out/{id}_blast.txt'
    cmd = f'blastp -db nr -query {fasta_file} -out {output_file} -outfmt 7 -remote'
    try: 
        subprocess.run(cmd, shell=True, check=True)
        print(f"running blasting{fasta_file}")
        #time.sleep(10)
        wirte_status(id,"Completed")
    except Exception as e:
        wirte_status(id,"Error")
    subprocess.Popen(["python3", "s4.1_runblast.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)#DEVNULL means can be run in background

else :
    with open('s4_out/seqBLAST_pre.txt',"r") as file:
        content = file.read()
    if  content.find("~") == -1 :
        with open('s4_out/seqBLAST_pre.txt',"a") as file:
            file.write("FINISH".center(100,"~"))
        
exit()