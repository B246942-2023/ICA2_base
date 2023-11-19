#!/usr/bin/python3
#===================================================module import==================================================
import os
import subprocess
import shutil
import threading
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
print("START STEP2".center(100, '-'))
print(f'''STEP2:Caculate the conservation level''')
input("Press Enter to Align".center(100,"-"))
print("Aligning".center(100, '-'))
print("Please Wait".center(100))

#1 check and make directory
outfolder = "s2_out"
check_output_directory( outfolder )

#2 Align 
#define the in/out path of align
filename_base = os.listdir("s1_out")[0].replace(".fasta","") # get the filename for subsequent rename
clustalo_inputpath = f"s1_out/*"
clustalo_outputpath= "s2_out/"+filename_base+".fasta"
# run clustalo in 128 threads , --force means will cover the file
command_clustalo = f"clustalo -i {clustalo_inputpath} -o {clustalo_outputpath} --outfmt=fasta --threads=64 --seqtype=protein "
clustalo_out,clustalo_error = linux_commands(command_clustalo)
print(clustalo_error)
print("Align Finished".center(100))

#3 Show the graph to the screen
input("Press any key to Show conservation graph".center(100,"-"))
command_plotcon_screen = f"plotcon -sequence {clustalo_outputpath}  -winsize 10 -graph x11 -scorefile EBLOSUM62 "
# It is a subprocess to make sure the main process will not be stop when usr doing anything to the x11 photo
thread = threading.Thread(target=linux_commands, args=(command_plotcon_screen,))
thread.start()
thread.join()
#print("hello world")

#4 Make a png conservation photo
plotcon_outputpath = f"s2_out"
command_plotcon_png = f"plotcon -sequence {clustalo_outputpath} -gdirectory {plotcon_outputpath} -winsize 10 -graph png -goutfile {filename_base} -scorefile EBLOSUM62 "
plotcon_out,plotcon_error = linux_commands(command_plotcon_png)

print("The conservation graph are saved in the form of PNG")
print("End the STEP2 ".center(100,"-"))