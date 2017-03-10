
def main():
    from matplotlib import rc
    rc('backend', qt4="PySide")
    
    import junker, sys
    try:
        mainGui = junker.Junker()
    except SystemExit:
        del mainGui
        sys.exit()
        exit
        
# Instantiate a class
if __name__ == '__main__': # Windows multiprocessing safety
    print( "Image Junker" )
    print( "============" )
    print( "    Instructions:" )
    print( "    Right/Left arrow to traverse images" )
    print( "    Space/Del to remove images and associated files to ./junk" )
    print( "    S/Return to move images and associated files to ./salvage" )
    print( "    Z to move files back to current directory (undo)" )
    main()
