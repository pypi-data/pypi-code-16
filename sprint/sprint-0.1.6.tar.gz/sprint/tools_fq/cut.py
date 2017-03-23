def cut(fq_in_dir=0,fq_out_dir=0,cutnum=6,name='read1'):
	fi=open(fq_in_dir)
	fo=open(fq_out_dir,'w')
	cutnum=int(cutnum)
	line1=fi.readline()
	line2=fi.readline()
	line3=fi.readline()
	line4=fi.readline()
	idd=1
	while line1 !='':
		fo.write('@id_'+str(idd)+'_'+name+'\n')
		fo.write(line2[cutnum:])
		fo.write(line3)
		fo.write(line4[cutnum:])
		line1=fi.readline()
		line2=fi.readline()
		line3=fi.readline()
		line4=fi.readline()
		idd=idd+1
	fi.close()
	fo.close()	
