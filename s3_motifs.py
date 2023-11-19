#!/usr/bin/python3
#===================================================module import==================================================
import os
import subprocess
import shutil
#=================================================function define==================================================
#run linux command in python
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
#=====================================================main body==================================================
print("START STEP3".center(100, '-'))
print(f'''STEP3:Scan the motifs''')
input("Press Enter to Scan".center(100,"-"))
print("Scaning".center(100))
print()

#1 check and make directory
outfolder = "s3_out"
check_output_directory( outfolder )

#2 sperate the big fasta into small fasta files(each one contains only one seqences info)
#get the orignal fasta file path
folder_path = "s1_out"
filename_base = os.listdir(folder_path)[0].replace(".fasta","") # get the base filename for subsequent rename
file_path = f"{folder_path}/{filename_base}.fasta"

#read the file
with open(file_path, "r") as file:
    fasta_data = file.read()
#cat the whole orig_fasta file into many fasta files (each one only have one seqences info)
fasta_list = fasta_data.split(">")[1:] #the first element is " ",so remove 
for eachseq_str in fasta_list:
    lines_list = eachseq_str.strip().split('\n')  # split eachseq by "\n"
    seq_id = lines_list[0].split()[0] # just get the id
    seq_info = lines_list[0]  # the seq_id line is the first element in the list
    seq_data = '\n'.join(lines_list[1:])  # get the seq 
    with open(f"{outfolder}/{seq_id}.fasta", "w") as f:
            f.write(f">{seq_id}\n{seq_data}")

#3 send all the small fasta files into patmatmotifs
input_folder_path = "s3_out"
file_list = os.listdir(input_folder_path)
for file_path in file_list:
    patmatmotifs_inputpath = input_folder_path+"/"+file_path
    patmatmotifs_outputpath = input_folder_path+"/"+file_path.replace(".fasta","_motifs.txt")
    command_patmatmotifs = f"patmatmotifs -sequence {patmatmotifs_inputpath} -outfile {patmatmotifs_outputpath} -full "
    patmatdb_out,patmat_error = linux_commands(command_patmatmotifs)


#4 Analysis the motifs_data
motifs_counts = {}  # [motifname]: count
motifs_id = {}      # [motifname] : [id1,id2,id3....]
id_motifs={}        # [id] : [motif1,motif2,...]
id_Hitcount = {}    # [id]: motifs_counts
no_motifs_id = []   # [id of those have no motifs]
file_total = 0      # count the total file

for filename in os.listdir(input_folder_path):
    if filename.endswith('.txt'):  # all the txt files
        id = filename.replace("_motifs.txt","")# eg : id_motifs.txt
        file_total += 1
        motif_exist_flag = False
        with open(os.path.join(input_folder_path, filename), 'r') as file:
            for line in file:
                if 'HitCount' in line :
                    id_Hitcount[id] = line.split()[-1]
                if 'Motif' in line:  # find the Motif line
                    motif_exist_flag = True # flag on exist turn into True
                    motif = line.split()[-1]
                    #print(id)
                    #print(motif)
                    if motif in motifs_counts:
                        motifs_counts[motif] += 1
                        motifs_id[motif].append(id)
                    else :
                        motifs_counts[motif] = 1
                        motifs_id[motif] = [id]
        if motif_exist_flag == False:
            no_motifs_id.append(id)

#5 Save and Show results
#write the result into a file
filepath_out = f'{outfolder}/{filename_base}_motif_report.txt'
#sort the dict:motifs_counts , to show the more frequent ones first
sorted_motifs_counts = sorted(motifs_counts.items(), key=lambda x: x[1], reverse=True) #sorted_motifs_counts = [(k,v),(k,v)(k,v)...]
#sort the dict:motifs_counts , from high hitcount to low one
sorted_id_Hitcount = sorted(id_Hitcount.items(), key=lambda x: x[1], reverse=True) #[(sq1,hits1),(sq2,hits2),(sq3,hits3)....]
#save the 10 highest counts data into blast queneline
filename="autoscreen.txt"
auto_out=f'{outfolder}/{filename}'
with open(auto_out, 'w') as auto:
    for id,counts in sorted_id_Hitcount[:10]:
        auto.write(f"{id}\n")


with open(filepath_out, 'w') as f:
    #write the title
    f.write("Motifs Scan".center(100,'=') + "\n")
    f.write("RESULTS".center(100) + "\n\n")
    #write the basic counts data
    f.write("Overall".center(100) + "\n\n")
    for key,value in sorted_motifs_counts:
        f.write(f"\tmotif:{key}".ljust(40))
        f.write(f"{value}/{file_total} counts/total_sequences".rjust(46) + "\n")
    f.write("\n")

    #write the ID Detail 
    f.write("-".center(100,'-') + "\n\n")
    f.write("ID Detail".center(100) + "\n\n")
    for key in motifs_id:
        f.write(f"motif:{key}".center(100) + "\n")
        for id in range(0,len(motifs_id[key]),5):
            f.write('\t'+'\t'.join(motifs_id[key][id:id+5]) + "\n")
        f.write("\n")           
    f.write("\n")

    # write the No Motif ID
    f.write("-".center(100,'-') + "\n\n")
    f.write("No Motif ID".center(100) + "\n\n")
    for id in range(0,len(no_motifs_id),5):
        f.write('\t'+'\t'.join(no_motifs_id[id:id+5]) + "\n")
    f.write("\n")

    # Print the 10 sequences_id of highest counts of motifs
    f.write("-".center(100,'-') + "\n\n")
    f.write("Auto Screen".center(100) + "\n\n")
    f.write(f"\tID".ljust(40))
    f.write(f"Motifs Counts".rjust(40) + "\n")
    f.write("\n")
    for id,counts in sorted_id_Hitcount[:10]:
        f.write(f"\t{id}".ljust(40))
        f.write(f"{counts}".rjust(40) + "\n")
    f.write("\n")

    f.write("=".center(100,"=") + "\n")

#6 print the file into the screen
with open(filepath_out, 'r') as f:
    print(f.read())

print()
print("End the STEP3 ".center(100,"-"))