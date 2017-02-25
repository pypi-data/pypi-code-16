#!/usr/bin/env python3


#  TO RUN JUST TYPE:
#  python3 analysis_pipeline.py

# INPUT FILES AND OPTIONS WILL BE REQUESTED AS USER INPUT


# THE FOLLOWING PROGRAMME IS PART OF the PACtool package (https://pypi.python.org/pypi/PACtool)
# OUTPUT FILES FROM PACtool GWAS ANALYSIS CAN BE ANALYZED 
# FOR THE SELECTION OF STATISTICALLY SIGNIFICANT SNPs.

# OPTIONS TO PERFORM EITHER COMBINATION OF THE FOLLOWING TESTS ARE AVAILABLE:

# Minor Allele Frequency Screening; only keep SNPs with MAF > 0.05
# HWE;                              only keep samples with Hardy Weiberg Expectation p-value > 0.001
# Association Test;                 option to select p-value threshold   (p < 0.000001 recommended )


# INPUT FILES SHOULD BE THE PACtool OUTPUT FILES
# WITH THE FOLLOWING FILE EXTENSION SUFFIXES:
#
#          .frequency 
#          .hwe 
#          .association 
#
# FOR MORE DETAILS TYPE: 
#  python pactool.py -h




import csv                                      # To store output of screening in a file
import timeit                                   # For checking runtime in secs
import math                                     # Just to round up runtime float, with math.ceil(runtime)  
 
freqs_start = timeit.default_timer() 
    
#Naming the lists that we will use in the end to take the SNPs that satisfy all selected tests' criteria:
#Leaving them empty allows for flexibility if a test is not selected.
 
maf_intersection_list   = []
hwe_intersection_list   = []
assoc_intersection_list = []


###########################################################################################################
# START OF MINOR ALLELE FREQUENCY TEST  BLOCK:
###########################################################################################################

MAF_threshold = 0.05   
     
print("Please select tests for your SNP screening:")

input_maf = """\nMAF Test:
This test will keep only the SNPs with Minor Allele Frequency (MAF) > 0.05.
Proceed [y/n]:\n""" 

maf_test = input(input_maf)
     
if maf_test == "y":
     
    maf_file = input("\nEnter output.frequency filename (e.g  chr20.frequency) from PACtool analysis:\n\n")     
     
    try:
        with open(maf_file) as f:
 
            freqs_LIST = [x.split() for x in f]         
                                                        # freqs_LIST: A LIST, which each row of the file as sublist
                                                        # [i] print(len(freqs_LIST), freqs_LIST[0:2])
                                                        # [o] 195146 
                                                        # [ 
                                                        #   ['snp_code', 'ref_freq_control', 'alt_freq_control', 'ref_freq_cases', 'alt_freq_cases', 'ref_freq_total', 'alt_freq_total'], 
                                                        #   ['snp_0', '0.802', '0.198', '0.785', '0.215', '0.7935', '0.2065']
                                                        # ]
 
 
 
            freqs_cols = [x for x in zip(*freqs_LIST)]  
                                                        # freqs_cols: A list, with 7 tuples;
                                                        # 0.snp_code         ______freqs_cols[0] ('snp_code', 'snp_0', 'snp_1')
                                                        # 1.ref_freq_control
                                                        # 2.alt_freq_control
                                                        # 3.ref_freq_cases 
                                                        # 4.alt_freq_cases 
                                                        # 5.ref_freq_total   ______freqs_cols[5]
                                                        # 6.alt_freq_total   ______freqs_cols[6]
 
            #BEFORE KEEPING SNPs WITH MAF > 0.05
            #WE HAVE TO FIND WHICH ONE IS THE MAF.
             
            #CREATING THE LISTS and COUNTERS NEEDED
            #TO KEEP MINOR ALLELE FREQUENCY OF EACH SNPs
            #Read below, the if loop for more details:
 
            snp_code_freqs = list(freqs_cols[0][1:])   #freqs_cols[0][0] is the header, so we start from [0][1]
 
            ref_freqs      = list(freqs_cols[5][1:])   #refers to total observed frequency in the population for the REF allele
 
            alt_freqs      = list(freqs_cols[6][1:])   #refers to total observed frequency in the population for the ALT allele
 
 
 
            minor_snps_kept  = []                      #the very same list as this one: snp_code_freqs = list(freqs_cols[0][1:])
 
            minor_freqs_kept = []                      #a list that  will hold the value of the minor allele frequency for each snp_code   
 
            minor_freqs_from = []                      #a list, with len= 195145, containing these strings: "ref", "alt" | order stays true to the above lists
                                                       #thus we could know which is the minor allele for each snp
 
 
            ref_minor_snps    = []                     #a list that stores the snp_codes of snps with the REF as the minor allele  
            ref_minor_counter = 0                      #a counter that counts how many snps have the ref as minor allele
                                                       #len(ref_minor_snps) == ref_minor_counter ==  minor_freqs_from.count("ref")| check if True 
 
            alt_minor_snps    = []                     #a list that stores the snp_codes of snps with the ALT as the minor allele
            alt_minor_counter = 0                      #a counter that counts how many snps have the ALT as minor allele
                                                       #len(alt_minor_snps) == alt_minor_counter ==  minor_freqs_from.count("alt")| check if True 
 
 
            # FINDING THE MINOR ALLELE FOR EACH SNP:
            # x ____  snp_code_freqs
            # q ____  ref_freqs
            # z ____  alt_freqs
            # The loop below compares the values of ref_freq_total and alt_freq_total of a snp, 
            # the value that is smaller of the two, is the minor allele frequency
 
 
            for x,q,z in zip(snp_code_freqs, ref_freqs, alt_freqs ):  #order is super important here - be meticulous  
 
                if float(q) < float(z):                              #IF    aka REF is the minor allele:
                                                                     #THEN:
                    minor_freqs_kept.append(float(q))                #      add that value to the list with the minor allele freqs
                    minor_snps_kept.append(x)                        #      add the respective snp_code for that value in the list that holds the snp_codes | yes, redundant list; either redundant or ugly
                    ref_minor_snps.append(x)                         #      add the respective snp_code for that value also in ref_minor_snps | only if minor is ref here
                    minor_freqs_from.append("ref")                   #      add a "ref", in the list minor_freqs_from, for the respective snp
                    ref_minor_counter = ref_minor_counter + 1        #      add 1 to the counter so that we know how many SNPs have the REF as minor allele
 
 
                else:                                                #ELSE: aka if float(y) > float(z), aka ALT is the minor allele:
                    minor_freqs_kept.append(float(z))                #THEN:
                    minor_snps_kept.append(x)                        #      add that value to the list with the minor allele freqs
                    alt_minor_snps.append(x)                         #      add the respective snp_code for that value in the list that holds the snp_codes 
                    minor_freqs_from.append("alt")                   #      add an "alt", in the list minor_freqs_from, for the respective snp
                    alt_minor_counter = alt_minor_counter + 1        #      add 1 to the counter so that we know how many SNPs have the ALT as minor allele
 
 
            #STORING snp_code, minor_freq, ref/alt for each SNP
            #as a sublist in a LIST, that holds as many sublists
            #as the SNPs; 195145 that is. 
            #So, len(kept_LIST)==195145 (check if True)
            #kept_LIST[i][0] is snp_code
            #kept_LIST[i][1] is the value of minor allele freq for snp_i
            #kept_LIST[i][2] is either "ref" or "alt"; denotes which one is the minor for snp_i
 
        ##############################################################################################################################  
            #COMMENTED OUT BLOCK THAT CREATES A FILE WITH ALL SNPs, EVEN < 0.05 MINOR ALLELE FREQ
            ##minor_LIST = [list(x) for x in zip(freqs_snps_kept, minor_freqs_kept, minor_freqs_from)] 
            ## with open("minor_freq_SNPs.txt", "w") as q:  #just changing the usual f to q, for avoiding conflict of variable claiming
            ## writer1 = csv.DictWriter(q, fieldnames = ["snp_code", "minor_freq", "minor_allele"], delimiter = ' ')
            ## writer1.writeheader()
            ## writer2 = csv.writer(q, delimiter =' ')
            ## writer2.writerows(minor_LIST)
        ###############################################################################################################################    
 
            # CREATING THE LISTS and COUNTERS NEEDED
            # TO ONLY KEEP SNPs with ALLELE FREQUENCY > 0.05
            # Read comments above the following if-Loop for more details:
 
            final_minor_freqs   = []
            final_minor_snps    = []
            final_minor_allele  = []
            final_minor_counter = 0
            final_minor_out     = 0
 
            # DISCARDING SNPs with minor allele frequency < 0.05:
            # w_________freqs_snps_kept
            # e_________minor_freqs_kept
            # r_________minor_freqs_from
 
        for w,e,r in zip(minor_snps_kept, minor_freqs_kept, minor_freqs_from):                                
 
            if float(e) > 0.05:                                  #(ONLY) IF the minor allele frequency > 0.05 (hint:KEEP SNP)
                                                                 #THEN:
                final_minor_freqs.append(float(e))               #add that value to the list with the final SNPs' minor allele freqs
                final_minor_snps.append(w)                       #add the respective snp_code for that value in the list that holds the snp_codes 
 
                maf_intersection_list.append(w)                  #add the respective snp_code in the list for the intersection btween tests
                 
                final_minor_allele.append(r)                     #add the "ref" or "alt", to denote the minor allele
                final_minor_counter = final_minor_counter + 1    #add 1 to the counter so that we know how many SNPs have minor all freq > 0.05
            else:
                final_minor_out = final_minor_out + 1            #add 1 to the counter so that we know how many SNPs have minor all freq < 0.0
                                                                 #final_minor_counter+final_minor_out == 195145 | check if True

        #########################################################################################################################################                                                         
                                                                 
        # FEEL FREE TO COMMENT OUT THE FOLLOWING BLOCK THAT STORES SNPs IN A FILE.
        # IF YOU NEED TO SAVE TIME AND DO NOT NEED THE OUTPUT FILE, 
        # YOUR SNPs WILL BE ONLY STORED IN THE LIST: final_minor_snps
        # *NOTE* 
        # PREFERABLY COMMENT OUT CODE WITH 2 HASHTAGS, TO DENOTE THAT IT IS NOT COMMENTS BUT "SILENCED" CODE
 
 
        ##########################################################################################################################################
        FILE_minor_start     = timeit.default_timer()
 
 
 
        final_minor_LIST = [list(x) for x in zip(final_minor_snps, final_minor_freqs, final_minor_allele)]
        with open("maf_screening_snps.txt", "w") as e: 
            writer1 = csv.DictWriter(e, fieldnames = ["snp_code", "minor_freq", "minor_allele"], delimiter = ' ')
            writer1.writeheader()
            writer2 = csv.writer(e, delimiter =' ')
            writer2.writerows(final_minor_LIST)
 
        FILE_minor_end     = timeit.default_timer()
        FILE_minor_runtime = FILE_minor_end - FILE_minor_start
 
        ##########################################################################################################################################
        freqs_end = timeit.default_timer() 
        freqs_runtime = freqs_end - freqs_start
 
 
        print(">MINOR ALLELE FREQUENCY SCREENING:")
        print(final_minor_out, "SNPs were discarded from total (", len(snp_code_freqs) ,") in the Minor Allele Frequency screening.")
        print(len(final_minor_snps),"SNPs with Minor Allele Frequency >", MAF_threshold ,"were kept in the Minor Allele screening.")
        print("Minor Allele Frequency Screening Runtime:", math.ceil(freqs_runtime), "seconds\n")
        #print("FILE storing Runtime:", math.ceil(FILE_minor_runtime), "seconds\n")
        #print("FILE storing Runtime:", FILE_minor_runtime, "seconds\n")
        print("The SNPs with Minor Allele Frequency >", MAF_threshold ,"have been saved in the file: maf_screening_snps.txt ")
         
         
    except:
        print("""\nFile not found or not in the required format.
Please make sure:
-You have spelled the filename correctly.
-The file is in the directory you run the programme.
-The file is in the requested format.
*NOTE*
For help and file format info type:
    python3 pactool.py -h    
 """)
             
else:
    no_maf_file = "Minor Allele Frequency test not selected"
    print(no_maf_file)

    
    
###########################################################################################################
# END OF MINOR ALLELE FREQUENCY TEST  BLOCK:
###########################################################################################################    

    
    
###########################################################################################################
# START OF HWE TEST  BLOCK:
###########################################################################################################     
hwe_start   = timeit.default_timer() 
 
HWE_threshold = 0.001

input_hwe ="""\nHWE Test:
This test will keep only the SNPs with Hardy Weinberg expectation p-value > 0.001.
Proceed [y/n]:\n"""

hwe_test = input(input_hwe)
     
if hwe_test == "y":
 
    hwe_file = input("\nEnter output.hwe filename (e.g  analysis.hwe) from PACtool analysis.\n")     
    try:
        with open(hwe_file) as f:
 
            hwe_LIST = [x.split() for x in f]       # hwe_LIST: A LIST, which each row of the file as sublist
                                                    # [i] print(len(hwe_LIST), hwe_LIST[0:2])
                                                    # [o] 195146 [['snp_code', 'hwe_statistic', 'p-value'], ['snp_0', '0.420491403517', '0.810385108461']]
     
     
     
            hwe_cols = [x for x in zip(*hwe_LIST)]  # hwe_cols: A list, with 3 tuples; could use list(x) for x if LIST of sublists needed
     
                                                    # 1st tuple = 1st column, snp_code 
                                                    # len(hwe_cols[0]) = 195146
                                                    # hwe_cols[0][0:3]: ('snp_code', 'snp_0', 'snp_1')
         
                                                    # 2nd tuple = 2nd column, hwe_statistic
                                                    # len(hwe_cols[1]) = 195146
                                                    # hwe_cols[1][0:3]: ('hwe_statistic', '0.420491403517', '0.320919559327')
         
                                                    # 3rd tuple = 3rd column, p_value
                                                    # len(hwe_cols[2]) = 195146
                                                    # hwe_cols[2][0:3]: ('p-value', '0.810385108461', '0.851752080638')
     
            #NOTE:                                        
            #The output.hwe has a header; hence the [1:] below 
     
            hwe_pvalues = list(hwe_cols[2][1:])     # [i] print(len(pvalues_keep))
                                                    # [o] 195145
     
            hwe_SNPs = list(hwe_cols[0][1:])        # [i] print(len(snp_keep)) 
                                                    # [o] 195145
     
            hwe_pvals_kept = []                     # hwe_pvals_kept: a list that will store all HWE pvalues > 0.001
            hwe_snps_kept  = []                     # hwe_snps_kept:  a list that will store all snp_codes, from sample with HWE pvalues > 0.001
            hwe_count_out  = 0                      # hwe_count_out:  a counter that will count how many samples were discarted in the HWE filtering
 
            for x,y in zip(hwe_pvalues,hwe_SNPs):           
                if float(x) > HWE_threshold:        #aka: if pvalue > 0.001
                    hwe_pvals_kept.append(float(x))
                    hwe_snps_kept.append(y)         #redundant list, yeap
                     
                    hwe_intersection_list.append(y)
                 
                else:
                    hwe_count_out = hwe_count_out + 1
 
        # AT THIS POINT WE HAVE A LIST WITH SNP_CODES OF SNPs THAT PASSED THE HWE pvalue TEST
        # THIS LIST WILL BE COMPARED TO THE RESPECTIVE LISTS THAT WILL BE GENERATED IN THE NEXT TWO TESTS:
        # (ii)SNPs with minor allele frequencies > 0.05 and 
        # (iii)statistically significant SNPs from the ASSOCIATION TEST
 
        # FINALLY, THE INTERSECTION OF ALL THREE LISTS WILL BE THE SELECTED SNPs FOR FURTHER ANALYSIS
 
        # HWE test SNPs THAT PASSED THE "expectation p-value < 0.001" TEST
        # ARE STORED NOW  IN THE LIST NAMED: hwe_snps_kept
        # WILL BE ALSO STORED  IN  A  FILE NAMED: hwe_screening_SNPs.txt
 
 
        # FEEL FREE TO COMMENT OUT THE FOLLOWING BLOCK THAT STORES SNPs IN A FILE, 
        # IF YOU NEED TO SAVE TIME AND DO NOT NEED THE OUTPUT FILE. 
        # YOUR SNPs WILL BE ONLY STORED IN THE LIST: hwe_snps_kept
        # *NOTE* 
        # PREFERABLY COMMENT OUT CODE WITH 2 HASHTAGS, TO DENOTE THAT IT IS NOT COMMENTS BUT "SILENCED" CODE. 
 
        ###############################################################################################
        FILE_start     = timeit.default_timer()
 
 
        hwe_kept_LIST = [list(x) for x in zip(hwe_snps_kept, hwe_pvals_kept)]
        with open("hwe_screening_SNPs.txt", "w") as h: 
            writer1 = csv.DictWriter(h, fieldnames = ["snp_code", "hwe_pvalue"], delimiter = ' ')
            writer1.writeheader()
            writer2 = csv.writer(h, delimiter =' ')
            writer2.writerows(hwe_kept_LIST)
     
            #NOTE: hwe_screening_SNPs.txt file has a header, so it should be: 
            #[i]: wc -l hwe_screening_SNPs.txt
            #[o]: len(hwe_snps_kept + 1 | here: 192207 + 1 = 192208
     
            FILE_end     = timeit.default_timer()
            FILE_runtime = FILE_end - FILE_start
     
     
            #################################################################################################
     
            hwe_end     = timeit.default_timer()
            hwe_runtime = hwe_end - hwe_start
     
            print(">HWE SCREENING:")
            print(hwe_count_out, "SNPs were discarded from total (", len(hwe_SNPs),")in the HWE screening.")
            print(len(hwe_snps_kept),"SNPs with expectaton pvalue >", HWE_threshold ,"were kept in the HWE screening.")
            print("HWE Screening Runtime:", math.ceil(hwe_runtime), "seconds\n")
            #print("FILE storing Runtime:", math.ceil(FILE_runtime), "seconds\n")
            #print("HWE Screening Runtime:", hwe_runtime, "seconds\n")
            #print("FILE storing Runtime:", FILE_runtime, "seconds\n")
     
     
            print("The SNPs with Hardy Weiberg expectaton pvalue >", HWE_threshold , " have been saved in the file: hwe_screening_SNPs.txt ")
             
    except:
        print("""\nFile not found or not in the required format.
Please make sure:
-You have spelled the filename correctly.
-The file is in the directory you run the programme.
-The file is in the requested format.
*NOTE*
For help and file format info type:
    python3 pactool.py -h    
 """)
         
else:
    no_hwe_file = "HWE test not selected"
    print(no_hwe_file)    

###########################################################################################################
# END OF HWE TEST  BLOCK:
###########################################################################################################      
    

###########################################################################################################
# START OF ASSOCIATION TEST  BLOCK:
###########################################################################################################  
    
assoc_start = timeit.default_timer() 


input_assoc = """\nAssociation Test:
This test will keep only statistically significant SNPs.
Proceed [y/n]:\n"""

assoc_test = input(input_assoc)

     
if assoc_test == "y":
        
    try:
        assoc_file = input("\nEnter output.association filename (e.g  chr20.association) from PACtool analysis:\n")     
        ASSOC_threshold = input("\nPlease select p-value threshold as a float number, e.g. 0.0001\nRecommended threshold 0.000001 or lower.\n")    
        
        with open('outputassoc_total.txt') as asc:
             
            assoc_LIST = [x.split() for x in asc]       # assoc_LIST: A LIST, which each row of the file as sublist
                                                        # len(assoc_LIST) = 144192
                                                        # assoc_LIST[0]): ['snp_code', 'locus', 'ref', 'alt', 'p-value', 'OR_rr_ra', 'OR_rr_aa', 'OR_ra_aa']
                                                          
                                                      
                 
            assoc_cols = [x for x in zip(*assoc_LIST)]  # assoc_cols:     A list, with 8 tuples;
                                                        # assoc_cols[0]___1. snp_code
                                                        #                 2. locus
                                                        #                 3. ref
                                                        #                 4. alt
                                                        # assoc_cols[4]___5. p-value
                                                        #                 6. OR_rr_ra
                                                        #                 7. OR_rr_aa
                                                        #                 8. OR_ra_aa
                                                          
             
                                                        
                 
            assoc_pvalues = list(assoc_cols[4][1:])     # [1:] ,because of the header, 
                                                        # [i] print(len(assoc_pvalues), assoc_pvalues[0:2])    
                                                        # [o] 144191 ['0.591069437423', '0.467213155849']
                 
            assoc_SNPs = list(assoc_cols[0][1:])        # Skip HEADER again! [1:]
                                                        # [i] print(len(assoc_SNPs), assoc_SNPs[0:4])    
                                                        # [o] 144191 ['snp_0', 'snp_2', 'snp_3', 'snp_4']
                 
            assoc_pvals_kept = []                       # assoc_pvals_kept: a list that'll store all assoc test samples w/ pvalues < 0.001
            assoc_snps_kept  = []                       # assoc_snps_kept:  a list that'll store all snp_codes, from all assoc test samples w/ pvalues < 0.001
            assoc_count_out  = 0                        # assoc_count_out:  a counter for how many samples were discarted in the assoc test pvalues < 0.001 filtering
         
            for x,y in zip(assoc_pvalues,assoc_SNPs):           
                if float(x) < float(ASSOC_threshold):
                    assoc_pvals_kept.append(float(x))
                    assoc_snps_kept.append(y)
                    
                    assoc_intersection_list.append(y)   #for the final comparison of SNPs left in all selected tests
                    
                else:
                    assoc_count_out = assoc_count_out + 1
         
                      
        # AT THIS POINT WE HAVE A LIST WITH SNP_CODES OF SNPs THAT PASSED THE Association pvalue TEST
        # THIS LIST WILL BE COMPARED TO THE RESPECTIVE LISTS THAT WILL BE GENERATED IN OTHER TWO TESTS:
        # (i)   HWE p-value > 0.001
        # (ii)SNPs with minor allele frequencies > 0.05 and 
         
          
        # FINALLY, THE INTERSECTION OF ALL THREE LISTS WILL BE THE SELECTED SNPs FOR FURTHER ANALYSIS
          
        # SNPs THAT PASSED THE "Association Test p-value < 0.000001" TEST
        # ARE STORED NOW  IN THE LIST NAMED: assoc_snps_kept
        # ARE STORED ALSO IN  A  FILE NAMED: assoc_screening_SNPs.txt
          
             
        # FEEL FREE TO COMMENT OUT THE FOLLOWING BLOCK THAT STORES SNPs IN A FILE, 
        # IF YOU NEED TO SAVE TIME AND DO NOT NEED THE OUTPUT FILE. 
        # YOUR SNPs WILL BE ONLY STORED IN THE LIST: assoc_snps_kept
        # *NOTE* 
        # PREFERABLY COMMENT OUT CODE WITH 2 HASHTAGS, TO DENOTE THAT IT IS NOT COMMENTS. 
          
        ###############################################################################################
        FILE_assoc_start     = timeit.default_timer()
          
        assoc_kept_LIST = [list(x) for x in zip(assoc_snps_kept, assoc_pvals_kept)]
        with open("assoc_screening_SNPs.txt", "w") as a: 
            writer1 = csv.DictWriter(a, fieldnames = ["snp_code", "assoc_pvalue"], delimiter = ' ')
            writer1.writeheader()
            writer2 = csv.writer(a, delimiter =' ')
            writer2.writerows(assoc_kept_LIST)
             
             
         
        FILE_assoc_end     = timeit.default_timer()
        FILE_assoc_runtime = FILE_assoc_end - FILE_assoc_start
        ################################################################################################
         
        assoc_end = timeit.default_timer() 
         
         
        assoc_end = timeit.default_timer() 
        assoc_runtime = assoc_end - assoc_start
          
          
        print(">ASSOCIATION TEST SCREENING:")
        print(assoc_count_out, "SNPs were discarded from total (",len(assoc_SNPs) ,") of file outputassoc_total.txt, during the Association Test screening.")
        print(len(assoc_snps_kept),"SNPs with Association Test p-value <", ASSOC_threshold ," were kept in the  Association Test screening.")
        print("Association Test Screening Runtime:", math.ceil(assoc_runtime), "seconds\n")
        #print("FILE storing Runtime:", math.ceil(FILE_assoc_runtime), "seconds\n")
        #print("Association Test Screening Runtime:", assoc_runtime, "seconds\n")
        #print("FILE storing Runtime:", FILE_assoc_runtime, "seconds\n")
          
          
        print("The SNPs with Association Test p-value <",ASSOC_threshold ," have been saved in the file: assoc_screening_SNPs.txt \n")    
                
    except:
        print("""\nFile not found or not in the required format.
Please make sure:
-You have entered a valid float number for p-value.
-You have spelled the filename correctly.
-The file is in the directory you run the programme.
-The file is in the requested format.
*NOTE*
For help and file format info type:
    python3 pactool.py -h    
 """)
         
else:
    no_assoc_file = "Association Test not selected."
    print(no_assoc_file)        


###########################################################################################################
# END OF ASSOCIATION TEST  BLOCK:
###########################################################################################################  




# INTERSECTION MADmESS: 
# All possible test combinations the user might have chosen.
# -Find the intersections of the seleted SNPs for each combo
# -Keeping the snp_code in 1 column files:
    

    
# 1: maf + hwe + assoc    
if maf_test == "y" and hwe_test == "y" and assoc_test == "y":
    maf_hwe_assoc = (set(maf_intersection_list+assoc_intersection_list).intersection(hwe_intersection_list))
    print('\n'.join(maf_hwe_assoc), file=open("maf_hwe_assoc_snps.txt", "w") )
    print("After MAF, HWE and association test", len(maf_hwe_assoc), " SNPs were left")
    print("A list with the selected SNPs has been saved in the file: maf_hwe_assoc_snps.txt")
else:
    pass


# 2: maf + hwe
if maf_test == "y" and hwe_test == "y" and  assoc_test != "y":
    maf_hwe = (set(maf_intersection_list).intersection(hwe_intersection_list))
    print('\n'.join(maf_hwe), file=open("maf_hwe_snps.txt", "w") )
    print("After MAF and HWE test", len(maf_hwe), " SNPs were left")
    print("A list with the selected SNPs has been saved in the file: maf_hwe_snps.txt")
else:
    pass


# 3: maf + assoc
if maf_test == "y" and hwe_test != "y" and  assoc_test == "y":
    maf_assoc = (set(maf_intersection_list).intersection(assoc_intersection_list))
    print('\n'.join(maf_assoc), file=open("maf_assoc_snps.txt", "w") )
    print("After MAF and association test", len(maf_assoc), " SNPs were left")
    print("A list with the selected SNPs has been saved in the file: maf_assoc_snps.txt")
else:
    pass


# 4: hwe + assoc
if maf_test != "y" and hwe_test == "y" and  assoc_test == "y":
    hwe_assoc = (set(assoc_intersection_list).intersection(hwe_intersection_list))
    print('\n'.join(hwe_assoc), file=open("hwe_assoc_snps.txt", "w") )
    print("After HWE and association test", len(hwe_assoc), " SNPs were left")
    print("A list with the selected SNPs has been saved in the file: hwe_assoc_snps.txt")
else:
    pass


# 5: hwe
if maf_test != "y" and hwe_test == "y" and  assoc_test != "y":
    print('\n'.join(hwe_intersection_list), file=open("hwe_snps.txt", "w") )
    print(len(hwe_intersection_list), "passed the HWE threshold, p >", HWE_threshold, ".")
    print("A list with the selected SNPs has been saved in the file: hwe_snps.txt")
else:
    pass


# 6: maf
if maf_test == "y" and hwe_test != "y" and  assoc_test != "y":
    print('\n'.join(maf_intersection_list), file=open("maf_snps.txt", "w") )
    print(len(maf_intersection_list), "passed the Minor Allele Frequency Threshold >" , MAF_threshold, ".")
    print("A list with the selected SNPs has been saved in the file: maf_snps.txt")
else:
    pass


# 7: assoc

if maf_test != "y" and hwe_test != "y" and  assoc_test == "y":
    print('\n'.join(assoc_intersection_list), file=open("assoc_snps.txt", "w") )
    print(len(assoc_intersection_list),"passed the Association test threshold", ASSOC_threshold, ".")
    print("A list with the selected SNPs has been saved in the file: assoc_snps.txt")
else:
    pass


#print(len(maf_intersection_list))
#print(len(hwe_intersection_list))
#print(len(assoc_intersection_list))


#####################################################################################################################
#
#                                          T H E     E N D  
#
#####################################################################################################################





