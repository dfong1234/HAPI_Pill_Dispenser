import datetime
pills = {
	1 : {'name' : 'Cocaine', 'time' : '6:58PM'},
	2 : {'name' : 'More Cocaine', 'time' : '8:30PM'}
	}


def timeToDispense():
	for pillNum in pills:
		temp1 = pills[pillNum]['time']
		temp2 = ''.join(ch for ch in temp1 if not ch.isalpha())
		hours = int(temp2.split(':')[0])
		minutes = int(temp2.split(':')[1])
		if temp1.endswith('PM'):
			hours += 12
		now = datetime.datetime.now()
		if (hours == now.hour ) and (minutes == now.minute):
			return True

	return False


if timeToDispense():
	print("WHAT")
else:
	print("NOOO")