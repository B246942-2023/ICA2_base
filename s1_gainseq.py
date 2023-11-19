#!/usr/bin/python3
#=================================================  module import==================================================
import os
import subprocess
import shutil
import sys

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

#show the input menu
def show_menu() :
    #initialize the return variable
    protein_family = ""
    taxonomic_group = ""

    while True :
        print("MENU".center(100,"-"))
        flag = input(f'''Do you want the default search: 
                d1     : default1 glucose-6-phosphatase proteins from Aves (birds)
                d2     : default2 ABC transporter in mammals
                d3     : default3 kinase in rodents
                d4     : default4 adenyl cyclase in vertebrates
                n      : I want to input [protein name] and [taxonomic tree] by myself
                other  : Same as "n"
        yourinput: ''')
        if flag == "d1" :
            protein_family  = "glucose-6-phosphatase"
            taxonomic_group = "Aves"
            break
        if flag == "d2" :
            protein_family  = "ABC transporter"
            taxonomic_group = "mammals"
            break
        if flag == "d3" :
            protein_family  = "kinase"
            taxonomic_group = "rodents"
            break
        if flag == "d4" :
            protein_family  = "adenyl cyclase"
            taxonomic_group = "vertebrates"
            break

        else :
            print("IMPORTANT:Please do not enter plural nouns for proteins")
            protein_family = input("Enter the protein family of interest: ")
            taxonomic_group = input("Enter the taxonomic group: ")
            print("Your choices".center(100, '-'))
            print( f'''
                protein family : {protein_family}
                taxnomic group : {taxonomic_group}'''
            )

            print()
            flag_confirm = input(f'''PLS confirm your selection(y/n):
            y       : yes 
            n       : input again
            other   : input again
            Your Input : ''')
            print("-".center(100, '-'))
            if flag_confirm == "y":
                break
    return protein_family,taxonomic_group

# make a query 
def make_query(query):
    print(f'''Your NCBI query:
                {query}
''')
    print("Searching...".center(100, '-'))
    print("Please Wait".center(100))
    esearch_command = f"esearch -db protein -query '{query}' | efetch -format fasta"
    search_out,search_errors = linux_commands(esearch_command)
    return search_out,search_errors

# analysis the fasta_data # and show results
def analysis_fasta(fasta):
    fasta_list = fasta.split("\n")
    seq_info_dict = {} # a dict [key]: id_number , value : (partial_State,Specise) 
    species_set = set() # easy to count the num of species
    for line in fasta_list:
        if line.startswith(">"):#>KFM01312.1 Glucose-6-phosphatase, partial [Aptenodytes forsteri]
            id = line.split()[0][1:]  #[0]:>KFM01312.1 ,don't need > so form [1:]
            flag_partial = "partial" in line.lower()
            species_name = line.split('[')[-1].split(']')[0] #get species names
            seq_info_dict[id] = (flag_partial,species_name)
            species_set.add(species_name)
    #show results
    print("RESULTS".center(100))
    print(f"There are {len(seq_info_dict)} data")
    print(f"The data are from {len(species_set)} specises")
    #print(seq_info_dict)
    return len(seq_info_dict)

#Help manual when no search results
def help_manual():
    print("IMPORTANT".center(100,"-"))
    print("Found 0 results in your search!")
    print()
    print(f'''Suggestions: 
                1 : Please do not enter plural nouns for proteins eg: kinases x     kinase √
                2 : Check your final query below to find if there is any spell faults
                3 : Paste the query to the ncbi website to see if there is any difference (That means net error) 
''')
    
#=====================================================main body==================================================
print("START STEP1".center(100, '-'))
print(f'''STEP1:Input your protein of interest and do a search
  ''')

# main loop : keeping loop when the usr don't want to save data
while True:
    loop_flag = True

    #1 check/make/clear output_directory
    check_output_directory("s1_out")

    #2 show input menu and ask for the input
    protein_family,taxonomic_group = show_menu()
    query_not_partial   = f"({protein_family}[Protein name]) AND ({taxonomic_group}[Organism]) NOT PARTIAL"
    query_all           = f"({protein_family}[Protein name]) AND ({taxonomic_group}[Organism])"

    #3 make a query in NCBI
    #Both Partial & Not Partial
    input("Press Enter to start seach".center(100,"-"))
    search_out_all,search_error_all                 = make_query(query_all)
    search_out_not_partial,search_error_not_partial = make_query(query_not_partial)

    #4 analysis fasta data and show
    print()#new line
    print()
    print()
    print("ALL Data".center(100, '='))
    num_data_all = analysis_fasta(search_out_all)


    print()#new line
    print("Not Partial Data".center(100, '='))
    num_data_not_partial = analysis_fasta(search_out_not_partial)

    #4.5 help the usr imporve the input when no results
    if (num_data_all == 0 or num_data_not_partial == 0) :
        help_manual()
        print(f'''Your NCBI query:
                {query_all}
                {query_not_partial}
''')
        print(f'''Input "s" and do a search again'''.center(100,))
        input("Press any key to continue".center(100, '-'))

    #5 decide the data quality and save
    print("Data Process".center(100, '-'))
    while True:
        flag_research = input(f'''How to handle the data?
                s       : search again 
                a       : only save the ALL Data
                b       : only save the NOT Partial Data                            
                q       : QUIT THE PRGRAMME
            yourinput: ''')
        if flag_research == "s":
            break

        if flag_research == "a": #save the all data
            outfolder = "s1_out"
            protein_family = protein_family.strip().replace(" ", "_")
            taxonomic_group = taxonomic_group.strip().replace(" ", "_")
            output_path = f"{outfolder}/{protein_family}_in_{taxonomic_group}.fasta" 
            with open(output_path, 'w') as file:
                file.write(str(search_out_all))
            loop_flag = False
            break

        if flag_research == "b": #save the not partial data
            outfolder = "s1_out"
            protein_family = protein_family.strip().replace(" ", "_")
            taxonomic_group = taxonomic_group.strip().replace(" ", "_")
            output_path = f"{outfolder}/{protein_family}_in_{taxonomic_group}.fasta" 
            with open(output_path, 'w') as file:
                file.write(str(search_out_not_partial))
            loop_flag = False
            break

        if flag_research == "q":
            sys.exit("Quit Sucessfully") 

        else :
            print("Input Wrong , try again!")

    #6 Decide Quit
    if loop_flag == False:
        print("End the STEP1 ".center(100,"-"))
        break 


