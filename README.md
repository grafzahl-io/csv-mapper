# A csv mapping script

It is build to map any csv to any other
csv format. It comes with useful helper to
fill columns with static files, or map even 
values

## csv-mapper.py

csv-static-mappings.json can contain field keys and values that are
applied to every row in the product csv source file
csv-field-mappings.json defines the field mappings from the source
file to the defined destination file for the destination format

if a field is not defined here (which is present in the dataheader list
below), it is automatically fetched from the 'csv-static-mappings.json'

The file 'csv-list-mappings.json' can be used to map list / dictionary 
values of the source fields. e.g. category in source file with IDs
are mapped by defining the destination field key (category_id) in this 
file and adding an object as value and map key=source value=destination
destination would be the destination category key

quick start:
```
python ./csv-mapper.py source_file.csv destination_file.csv --imagepath="https://yourhost.com/temp/" --imagefield="image"
```