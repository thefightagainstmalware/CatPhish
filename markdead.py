import csv
import sys
if len(sys.argv) < 2:
    print("usage: python markdead.py <item to mark as dead>")
    sys.exit(1)
data = []
with open('data.csv', newline='') as csvfile:
   reader = csv.reader(csvfile, delimiter=',', quotechar='|')
   for row in reader:
       data.append(row)
with open('data.csv', 'w') as f:
   for row in data:
       if row[3] == sys.argv[1]:
           row[5] = "no"
       f.write(f"{','.join(row)}\n")