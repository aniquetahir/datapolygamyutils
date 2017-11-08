from datetime import datetime
import sys

if __name__ == "__main__":
    yellowfilename = sys.argv[1]
    newfilename = sys.argv[2]
    yellowfile = open(yellowfilename, 'r')
    newyellowfile = open(newfilename, 'w')

    epoch = datetime.utcfromtimestamp(0)

    for line in yellowfile:
        fields = line.split(',')
        date = datetime.strptime(fields[1], '%Y-%m-%d %X')
        seconds = int((date-epoch).total_seconds())
        fields[1] = str(seconds)
        date = datetime.strptime(fields[2], '%Y-%m-%d %X')
        seconds = int((date - epoch).total_seconds())
        fields[2] = str(seconds)
        fields[-1] = fields[-1].strip() #Remove newline

        total_amount = float(fields[-1])
        tip_amount = float(fields[-4])
        tip_percentage = 0
        if total_amount > 0:
            tip_percentage = tip_amount/total_amount

        fields.append(str(tip_percentage))
        newyellowfile.write(','.join(fields))
        newyellowfile.write("\n")

    newyellowfile.flush()
    newyellowfile.close()
    yellowfile.close()
