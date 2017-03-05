NumberOfCorrections = 100  # TODO: keep or not?

# -----------------------------------------------------------------------------#

# TODO: bring the following back later

def to_be_handled():
    # -------------------------------------------------------------------------#
    #        input and output files
    # -------------------------------------------------------------------------#

    Signatures_outfile = open(outfile_Signatures_name, 'w')

    SigTransforms_outfile = open(outfile_SigTransforms_name, 'w')

    FSA_outfile = open(outfile_FSA_name, 'w')

    # July 15, 2014, Jackson Lee

    outfile_Signatures_name_JL = outfolder + corpus_stem + "_Signatures-JL.txt"
    Signatures_outfile_JL = open(outfile_Signatures_name_JL, 'w')



    # -------------------------------------------------------------------------#
    #       write log file header | TODO keep this part or rewrite?
    # -------------------------------------------------------------------------#

    #    outfile_log_name            = outfolder + corpus_stem + "_log.txt"
    #    log_file = open(outfile_log_name, "w")
    #    print("Language:", language, file=log_file)
    #    print("Minimum Stem Length:", MinimumStemLength,
    #          "\nMaximum Affix Length:", MaximumAffixLength,
    #          "\n Minimum Number of Signature uses:", MinimumNumberofSigUses,
    #          file=log_file)
    #    print("Date:", end=' ', file=log_file)





    # -------------------------------------------------------------------------#
    # -------------------------------------------------------------------------#
    #                     Main part of program                              #
    # -------------------------------------------------------------------------#
    # -------------------------------------------------------------------------#

    # For the following dicts ---
    # BisigToTuple:  keys are tuples of bisig   Its values are (stem, word1, word2)
    # SigToStems:    keys are signatures.  Its values are *sets* of stems.
    # StemToWord:    keys are stems.       Its values are *sets* of words.
    # StemToSig:     keys are stems.       Its values are individual signatures.
    # WordToSig:     keys are words.       Its values are *lists* of signatures.
    # StemCounts:    keys are words.      Its values are corpus counts of stems.


    BisigToTuple = {}
    SigToStems = {}
    WordToSig = {}
    StemToWord = {}
    StemCounts = {}
    StemToSig = {}
    numberofwords = len(wordlist)



    # -------------------------------------------------------------------------#
    #    1. Make signatures, and WordToSig dictionary,
    #       and Signature dictionary-of-stem-lists, and StemToSig dictionary
    # -------------------------------------------------------------------------#
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("1.                Make signatures 1")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    # -------------------------------------------------------------------------#
    #    1a. Declare a linguistica-style FSA
    # -------------------------------------------------------------------------#

    splitEndState = True
    morphology = FSA_lxa(splitEndState)

    # -------------------------------------------------------------------------#
    #    1b. Find signatures, and put them in the FSA also.
    # -------------------------------------------------------------------------#

    SigToStems, WordToSig, StemToSig = MakeSignatures(StemToWord,
                                                      FindSuffixesFlag, MinimumNumberofSigUses)

    # -------------------------------------------------------------------------#
    #    1c. Print the FSA to file.
    # -------------------------------------------------------------------------#

    # print "line 220", outfile_FSA_name # TODO: what's this line for?

    # morphology.printFSA(FSA_outfile)


    # ------------ Added Sept 24 (year 2013) for Jackson's program ------------#
    if True:
        printSignatures(SigToStems, WordToSig, StemCounts,
                        Signatures_outfile, g_encoding, FindSuffixesFlag)
        # added July 15, 2014, Jackson Lee
        printSignaturesJL(SigToStems, WordToSig, StemCounts,
                          Signatures_outfile_JL, g_encoding, FindSuffixesFlag)
    Signatures_outfile_JL.close()



    # -------------------------------------------------------------------------#
    # 5. Look to see which signatures could be improved, and score the improvement
    #    quantitatively with robustness.
    # Then we improve the one whose robustness increase is the greatest.
    # -------------------------------------------------------------------------#

    print("***", file=Signatures_outfile)
    print("*** 5. Finding robust suffixes in stem sets\n\n", file=Signatures_outfile)


    # -------------------------------------------------------------------------#
    #    5a. Find morphemes within edges: how many times? NumberOfCorrections
    # -------------------------------------------------------------------------#

    for loopno in range(NumberOfCorrections):
        # ---------------------------------------------------------------------#
        #    5b. For each edge, find best peripheral piece that might be
        #           a separate morpheme.
        # ---------------------------------------------------------------------#
        morphology.find_highest_weight_affix_in_an_edge(Signatures_outfile,
                                                        FindSuffixesFlag)

    # -------------------------------------------------------------------------#
    #    5c. Print graphics based on each state.
    # -------------------------------------------------------------------------#
    if True:
        for state in morphology.States:
            graph = morphology.createPySubgraph(state)
            if len(graph.edges()) < 4:
                continue
            graph.layout(prog='dot')
            filename = outfolder + 'morphology' + str(state.index) + '.png'
            graph.draw(filename)
            filename = outfolder + 'morphology' + str(state.index) + '.dot'
            graph.write(filename)


    # -------------------------------------------------------------------------#
    #    5d. Print FSA again, with these changes.
    # -------------------------------------------------------------------------#

    if True:
        morphology.printFSA(FSA_outfile)


    # -------------------------------------------------------------------------#
    localtime1 = time.asctime(time.localtime(time.time()))
    print("Local current time :", localtime1)

    morphology.dictOfLists_parses = morphology.parseWords(wordlist)

    localtime2 = time.asctime(time.localtime(time.time()))
    # print "Time to parse all words: ", localtime2 - localtime1


    # -------------------------------------------------------------------------#


    print("Finding common stems across edges.", file=FSA_outfile)
    HowManyTimesToCollapseEdges = 9
    for loop in range(HowManyTimesToCollapseEdges):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Loop number", loop)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        (commonEdgePairs, EdgeToEdgeCommonMorphs) = morphology.findCommonStems()
        # We now have a list of pairs of edges, sorted by how many stems they share in common.
        # In the current implementation, we consider only pairs of edges that have a common mother or daughter....


        if len(commonEdgePairs) == 0:
            print("There are no more pairs of edges to consider.")
            break
        edge1, edge2 = commonEdgePairs[0]
        state1 = edge1.fromState
        state2 = edge2.fromState
        state3 = edge1.toState
        state4 = edge2.toState
        print("\n\nWe are considering merging edge ", edge1.index, "(", edge1.fromState.index, "->",
              edge1.toState.index, ") and  edge", edge2.index, "(", edge2.fromState.index, "->", edge2.toState.index,
              ")")

        print("Printed graph", str(loop), "before_merger")
        graph = morphology.createDoublePySubgraph(state1, state2)
        graph.layout(prog='dot')
        filename = outfolder + corpus_stem + str(loop) + '_before_merger' + str(state1.index) + "-" + str(
            state2.index) + '.png'
        graph.draw(filename)

        if state1 == state2:
            print("The from-States are identical")
            state_changed_1 = state1
            state_changed_2 = state2
            morphology.mergeTwoStatesCommonMother(state3, state4)
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        elif state3 == state4:
            print("The to-States are identical")
            state_changed_1 = state3
            state_changed_2 = state4
            morphology.mergeTwoStatesCommonDaughter(state1, state2)
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        elif morphology.mergeTwoStatesCommonMother(state1, state2):
            print("Now we have merged two sister edges from line 374 **********")
            state_changed_1 = state1
            state_changed_2 = state2
            morphology.EdgePairsToIgnore.append((edge1, edge2))


        elif morphology.mergeTwoStatesCommonDaughter((state3, state4)):
            print("Now we have merged two daughter edges from line 377 **********")
            state_changed_1 = state3
            state_changed_2 = state4
            morphology.EdgePairsToIgnore.append((edge1, edge2))

        graph = morphology.createDoublePySubgraphcreatePySubgraph(state1)
        graph.layout(prog='dot')
        filename = outfolder + str(loop) + '_after_merger_' + str(state_changed_1.index) + "-" + str(
            state_changed_2.index) + '.png'
        print("Printed graph", str(loop), "after_merger")
        graph.draw(outfile_FSA_graphics_name)

    # -------------------------------------------------------------------------#
    # We create a list of words, each word with its signature transform (so DOGS is turned into NULL.s_s, for example)

    if True:
        printWordsToSigTransforms(SigToStems, WordToSig, StemCounts, SigTransforms_outfile, g_encoding,
                                  FindSuffixesFlag)


    # -------------------------------------------------------------------------#
    # -------------------------------------------------------------------------#
    #    Close output files
    # -------------------------------------------------------------------------#

    FSA_outfile.close()
    Signatures_outfile.close()
    SigTransforms_outfile.close()


    # -------------------------------------------------------------------------#
    #    Logging information
    # -------------------------------------------------------------------------#

    localtime = time.asctime(time.localtime(time.time()))
    print("Local current time :", localtime)

    numberofwords = len(wordlist)
    logfilename = outfolder + "logfile.txt"
    logfile = open(logfilename, "a")

    print(outfile_Signatures_name.ljust(60),
          '%30s wordcount: %8d data source:' % (localtime, numberofwords),
          infilename.ljust(50), file=logfile)



