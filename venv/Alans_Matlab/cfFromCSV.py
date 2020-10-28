#input: csv file with two columns, Channel number and Distance

#output: 22 row array consisting of electrode distances.
import csv
def cfFromCSV(file):
    cf = []
    with open(file) as input:
        csv_reader = csv.reader(input, delimiter = ",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                cf.append(row[1])
                line_count += 1

    return cf
