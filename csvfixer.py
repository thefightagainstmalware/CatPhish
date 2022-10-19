import csv
data = []
with open('data.csv', newline='') as csvfile:
   reader = csv.reader(csvfile, delimiter=',', quotechar='|')
   for row in reader:
       if len(row) < 6:
           row.append("no")
       data.append(row)
with open('data.csv', 'w') as f:
    for row in data:
        f.write(','.join(row))
        f.write('\n')