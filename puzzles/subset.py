import csv

input_file = 'sudoku.csv'
output_file = 'sudoku_10k.csv'
num_lines = 10000

with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header)

    count = 0
    for row in reader:
        writer.writerow(row)
        count += 1
        if count >= num_lines:
            break

print(f"Successfully created {output_file} with header + {num_lines} data rows")