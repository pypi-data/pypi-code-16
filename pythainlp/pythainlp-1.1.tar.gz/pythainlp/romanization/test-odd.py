import re
def is_match(regex, text):
    pattern = re.match(regex, text,re.U)
    return pattern is not None
def search(regex, text):
	return re.search(regex,text,re.U)
def vowel(data):
	vowel1=""
	if data=="ะ":
		vowel1+="อ"+data
	elif data=="ั":
		vowel1+="อ"+data
	elif data=="็":
		vowel1+="อ"+data
	elif data=="า":
		vowel1+="อ"+data
	elif data=="ำ":
		vowel1+="อ"+data
	elif data=="ิ":
		vowel1+="อ"+data
	elif data=="ำ":
		vowel1+="อ"+data
	elif data=="ุ":
		vowel1+="อ"+data
	elif data=="ู":
		vowel1+="อ"+data
	elif data=="โ":
		vowel1+=data+"อะ"
	return vowel1
def tone(data):
	if is_match(r"[ก-ฮ]",data):
		b=data+"อ"
	elif data == "่":
		b="ไม้เอก"
	elif data == "้":
		b="ไม้โท"
	elif data == "๊":
		b="ไม้ตรี"
	elif data == "๋":
		b="ไม้จัตวา"
	elif data == "็":
		b="ไม้ไต่คู้"
	elif data == "ั":
		b="ไม้หันอากาศ"
	else:
		b=vowel(data)
	return b
def word(data):
	v=list(data)
	aaa=list(data)
	m=search(r"[่|้|๊|๋]",data)
	if m:
		del(v[v.index(m.group(0))])
		v.append(m.group(0))
	#a=list(re.sub(r"[เ|แ]","*",data))
	a=v
	b=""
	i=0
	while i<len(a):
		m=search(r"[่|้|๊|๋]",a[i])
		if i+1<len(a):
			b+=tone(a[i])
		else:
			if m:
				b+=re.sub(r"[่|้|๊|๋]","",data)
				b+="-"
				b+=re.sub(r"[่|้|๊|๋]","",data)
				b+="-"
			b+=tone(a[i])
			b+="-"
		b+="-"
		i+=1
	b+=data
	bb = list(b)
	i=0
	while i<len(v):
		if is_match(r"[เ|แ]",v[i]) == True and ((is_match(r"[เ|แ]",v[i+1]) == False) and ((is_match(r"อ",v[i+2]) == False) and is_match(r"อ",v[i+3]))):
			if v[i]=="เ":
				h="-เอะ"
				#h+="-"
				bb.insert(bb.index(v[i+1])+2,h)
			elif v[i] == "แ":
				h="-แอะ"
				#h+="-"
				bb.insert(bb.index(v[i+1])+2,h)
		elif is_match(r"[ใ|ไ]",v[i]) == True and is_match(r"[ก-ฮ]",v[i+1]) == True:
			if v[i]=="ใ":
				h="-ใอ"
				bb.insert(bb.index(v[i+1])+2,h)
			elif v[i] == "ไ":
				h="-ไอ"
				bb.insert(bb.index(v[i+1])+2,h)
		i+=1
	if bb[0] == "-":
		del(bb[0])
	return (''.join(bb)).replace("--","-")
print(word("ปลา"))
print(word("อยาก"))
print(word("หนา"))
print(word("รถ"))
print(word("ต้น"))
print(word("หรา"))
print(word("นอน"))
print(word("จ้า"))
print(word("ตอง"))
print(word("ยัง"))
print(word("แข็ง"))
print(word("ผม"))
print(word("ต้น")+"\t"+word("ตาล"))
print(word("กัน"))
print(word("สลับ"))
print(word("มา")+"\t"+word("นะ"))
print(word("ครับ"))
print(word("รถ")+"\t"+word("ไฟ"))
print(word("กำ"))
print(word("เด้อ"))
print(word("คอม"))
print(word("สนาม"))
print(word("ใบ")+"\t"+word("ไม้"))
print(word("ลำ")+"\t"+word("ใย"))
print(word("ขโมย")) #! ขอ-มอ-ยอ-โอะ-ขโมย
print(word("เค็ม"))
print(word("รัก"))
print(word("เพื่อน")) #! เพื่อน สะกดว่า พอ - เอือ -นอ - ไม้เอก - เพื่อน
print(word("นาง"))
print(word("น่า")+"\t"+word("รัก"))