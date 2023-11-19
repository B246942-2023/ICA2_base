#!/usr/bin/python3
#===================================================module import==================================================
import os
import subprocess
import shutil
#=================================================function define==================================================
# check/make/clear output_directory
def check_output_directory( outfolder ):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    else :
        shutil.rmtree(outfolder)
        os.makedirs(outfolder)

# only make ,don't clear
def make_dir(outfolder):
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

#collate_data into a fold 
def collate_data(filepath):
    #make a dirctory to save data
    check_output_directory( f"{filepath}" )
    check_output_directory( f"{filepath}/fetched_sequences" )
    check_output_directory( f"{filepath}/conservation_analysis_results" )
    check_output_directory( f"{filepath}/motif_scan_results" )
    check_output_directory( f"{filepath}/motif_scan_results/Every_id" )
    check_output_directory( f"{filepath}/blast_results" )
    #handle s1_out
    for filename in os.listdir("s1_out"):
        source_path = os.path.join("s1_out", filename)
        destination_path = os.path.join(f"{filepath}/fetched_sequences", filename)
        shutil.copy(source_path, destination_path)
    #handle s2_out
    for filename in os.listdir("s2_out"):
        if filename.endswith('.png'):
            source_path = os.path.join("s2_out", filename)
            destination_path = os.path.join(f"{filepath}/conservation_analysis_results", filename)
            shutil.copy(source_path, destination_path)
    #handle s3_out
    for filename in os.listdir("s3_out"):
        if filename.endswith('report.txt'):#the report
            source_path = os.path.join("s3_out", filename)
            destination_path = os.path.join(f"{filepath}/motif_scan_results", filename)
            shutil.copy(source_path, destination_path)
        if filename.endswith('motifs.txt'):#the every_ids
            source_path = os.path.join("s3_out", filename)
            destination_path = os.path.join(f"{filepath}/motif_scan_results/Every_id", filename)
            shutil.copy(source_path, destination_path)
    #handle s4_out
    for filename in os.listdir("s4_out"):
        if filename.endswith('.txt'):
            source_path = os.path.join("s4_out", filename)
            destination_path = os.path.join(f"{filepath}/blast_results", filename)
            shutil.copy(source_path, destination_path)
#export the data
def export_data():
    while True:
        print("-".center(100,"-"))
        print()
        print("Input your export path".center(100))
        print()
        print("Example:".center(100))
        print("Results/glucose-6-phosphatase_Aves".center(100))
        print()
        path=input("Your Path: ")
        path = path.strip()
        if os.path.exists(path):
            print("IMPORTANT:Path already exsit, input again".center(100))
            print()
            input("Press Enter to continue".center(100,"-"))
        else:
            print("Make a double check:".center(100))
            print(path.center(100))
            print()
            if input("Confirm(y/n) : ") == "y" :
                collate_data(path)
                break
#reset the folder(delete all the un".py" end files and folders)
def reset(directory):
    for item in os.listdir(directory):
        if item.startswith('.'):#I lost all my git log before adding this.FUCK
            continue
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        elif not item.endswith('.py'):
            os.remove(item_path)

def track_status():
    flag_search_fecth_done = False
    flag_conservation_analysis = False
    flag_motif_scan = False
    flag_BLAST =False    
    flag_BLAST_finished = False
    search_name = "noname"
    
    #track the search and fetch
    if os.path.exists("s1_out"):
        for file in os.listdir("s1_out"):
            if file.endswith('.fasta'):
                flag_search_fecth_done = True
                search_name = file.replace('.fasta',"")
    #track the conservation
    if os.path.exists("s2_out"):
        for file in os.listdir("s2_out"):
            if file.endswith('.1.png'):
                file=file.replace('.1.png',"")
                if file == search_name :
                    flag_conservation_analysis = True

    #track the motif scan
    if os.path.exists("s3_out"):
        for file in os.listdir("s3_out"):
            if file.endswith('_motif_report.txt'):
                file=file.replace('_motif_report.txt',"")
                if file == search_name :
                    flag_motif_scan = True

    #track the blast running and finish
    if os.path.exists("s4_out/seqBLAST_pre.txt"):
        #check if there is a BLAST is running
        with open("s4_out/seqBLAST_pre.txt","r") as file:
            content = file.read()
            if "Running" in content:
                flag_BLAST = True
            if ("FINISH" in content) and (not flag_BLAST)  :
                flag_BLAST_finished = True
    
    return flag_search_fecth_done,flag_conservation_analysis,flag_motif_scan,flag_BLAST,flag_BLAST_finished,search_name

#=====================================================main body==================================================
#1 make all the dir
make_dir("s1_out")
make_dir("s2_out")
make_dir("s3_out")
make_dir("s4_out")

while True:
    #status check : many steps can only work when the search and fecth fasta have done
    flag_search_fecth_done,flag_conservation_analysis,flag_motif_scan,flag_BLAST,flag_BLAST_finished,search_name = track_status()

    # menu content
    print("MENU".center(100,"="))
    print("Central Control".center(100))
    print()
    print(f"Data Fetched  : {flag_search_fecth_done}" .center(100))
    print(f"BLAST Running : {flag_BLAST}" .center(100))
    print()
    print(f"    Current Sequences Set : {search_name}")
    print()
    print(f'''    1.Search and Fetch 
    2.Analysis the Conservation
    3.Scan the Motifs
    4.BlAST
    5.Collate results
    6.Export data
    7.Reset
    8.Auto Mode
    9.Quit''')
    print()
    print()
    print(f"\tConservation Data : {flag_conservation_analysis}\t Motif Scan Data : {flag_motif_scan}\t\t BLAST Data : {flag_BLAST_finished}")
    print()
    print()
    print("=".center(100,"="))

    # handle input 
    central_choices = input("Input your choices : ")
    if central_choices == "1":
        subprocess.run(["python3","s1_gainseq.py"]) # "python3" here is as same as the shebang line in the script 
    if central_choices == "2":
        if flag_search_fecth_done:
            subprocess.run(["python3","s2_conservation.py"]) 
        else :
            print("IMPORTANT:No data, Do '1.Search and Fetch' ".center(100))
    if central_choices == "3":
        if flag_search_fecth_done:
            subprocess.run(["python3","s3_motifs.py"])
        else :
            print("IMPORTANT:No data, Do '1.Search and Fetch' ".center(100))
    if central_choices == "4":
        if flag_search_fecth_done:
            subprocess.run(["python3","s4_blast.py"])
        else :
            print("IMPORTANT:No data, Do '1.Search and Fetch' ".center(100))
    if central_choices == "5":#collate_data
        if flag_search_fecth_done:
            collate_data("collate_data")
            print()
            print("Data are collected in folder : collected_data ".center(100))
            print()
        else :
            print("IMPORTANT:No data, Do '1.Search and Fetch' ".center(100))
    if central_choices == "6":#export_data
        if flag_search_fecth_done:
            export_data()
        else :
            print("IMPORTANT:No data, Do '1.Search and Fetch' ".center(100))
    if central_choices == "7":#reset
        if not flag_BLAST :
            if input("Confirm your reset:(y/n)") == "y":
                reset(".")
                print()
                print("Reset finished".center(100))
                print()
        else :
            print("IMPORTANT:BlAST is running,can't reset ".center(100))
    if central_choices == "8":
        print()
        print("I haven't finished this yet >-< ,sorry!".center(100))
        print()
    if central_choices == "9":
        break
    if central_choices not in "1%2^3(4!5@6+7#8*9":# if just 123456789 when input 12, it will not be handled
        print("Wrong Input")
    input("Press Enter to back the MENU".center(100,"-"))


