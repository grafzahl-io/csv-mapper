## This script will help to map the csv data of products
## from anywhere to shopify
##
## configure through various .json files, a csv file can be
## easily converted to a gunatic compatible product import file
## Usage:
## csv-static-mappings.json can contain field keys and values that are
## applied to every row in the product csv source file
## csv-field-mappings.json defines the field mappings from the source
## file to the defined destination file for gunatic
## if a field is not defined here (which is present in the dataheader list
## below), it is automatically fetched from the 'csv-static-mappings.json'
## The file 'csv-list-mappings.json' can be used to map list / dictionary 
## values of the source fields. e.g. Artikelkategory in source file with IDs
## are mapped by defining the destination field key (category_id) in this 
## file and adding an object as value and map key=source value=destination.
## destination would be the gunatic category key
##
## Start by executing:
## $> csv-mapper.py sourcefile.csv destinationfilename.csv
##
## Example
## python3 csv-mapper.py source_file.csv destination_file.csv --imagepath="https://yourhost.com/temp/" --imagefield="image"
import csv
import sys
import collections
import json
import argparse
import locale
import os
import random

# change this if the price format is not in german
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

parser=argparse.ArgumentParser(description='example: python3 csv-mapper.py source_file.csv destination_file.csv --imagepath="http://google.de/" --imagefield="image"')
parser.add_argument('sourcefile', help='filepath to the source where the data is mapped from')
parser.add_argument('destinationfile', help='filepath to the destination file')
parser.add_argument("-imgp", "--imagepath", help='Adds this path to all imported image filenames')
parser.add_argument("-imgf", "--imagefield", help='Define the field name (destination key) on which the image filepath is prepend to')

options=parser.parse_args()
sourcefile=options.sourcefile
destinationfile=options.destinationfile
imagepath=options.imagepath
imagefield=options.imagefield

dataheader=[
  "Handle",
  "Title",
  "Body (HTML)",
  "Vendor",
  "Product Category",
  "Type",
  "Tags",
  "Published",
  "Option1 Name",
  "Option1 Value",
  "Option2 Name",
  "Option2 Value",
  "Option3 Name",
  "Option3 Value",
  "Variant SKU",
  "Variant Grams",
  "Variant Inventory Tracker",
  "Variant Inventory Qty",
  "Variant Inventory Policy",
  "Variant Fulfillment Service",
  "Variant Price",
  "Variant Compare At Price",
  "Variant Requires Shipping",
  "Variant Taxable",
  "Variant Barcode",
  "Image Src",
  "Image Position",
  "Image Alt Text",
  "Gift Card",
  "SEO Title",
  "SEO Description",
  "Google Shopping / Google Product Category",
  "Google Shopping / Gender",
  "Google Shopping / Age Group",
  "Google Shopping / MPN",
  "Google Shopping / Condition",
  "Google Shopping / Custom Product",
  "Google Shopping / Custom Label 0",
  "Google Shopping / Custom Label 1",
  "Google Shopping / Custom Label 2",
  "Google Shopping / Custom Label 3",
  "Google Shopping / Custom Label 4",
  "Variant Image",
  "Variant Weight Unit",
  "Variant Tax Code",
  "Cost per item",
  "Included / Deutschland",
  "Price / Deutschland",
  "Compare At Price / Deutschland",
  "Included / International",
  "Price / International",
  "Compare At Price / International",
  "Status"
]

def getMapping():
  # get mapping from json file
  static_file = open('config/csv-field-mappings.json')
  field_mappings = json.load(static_file)
  return field_mappings

def getAvailableStatics():
  # get static data to impelment to current import
  static_file = open("config/csv-static-mappings.json")
  static_fields = json.load(static_file)
  return static_fields

def mapValues():
  static_file = open("config/csv-list-mappings.json")
  value_mappings = json.load(static_file)
  return value_mappings

def applyMapped(new_row, dest_key, source_value, value_mappings, imagefield, imagepath):
  new_row[dest_key] = source_value
  if dest_key in value_mappings:
    if source_value in value_mappings[dest_key]:
      new_row[dest_key] = value_mappings[dest_key][source_value]
      
  if dest_key == imagefield and imagepath:
    new_row[dest_key] = imagepath + new_row[dest_key]

  return new_row

def mapRow(row):
  static_fields = getAvailableStatics()
  mapping = getMapping()
  value_mappings = mapValues()
  new_row = dict.fromkeys(dataheader)

  for statics in static_fields:
    if type(static_fields[statics]) == str and static_fields[statics].startswith('ext:'):
      # load data from related data in linked files
      textdata = open("statics/" + static_fields[statics][4:])
      new_row[statics] = textdata.read()
      textdata.close()
    else:
      new_row[statics] = static_fields[statics]
  try:
    for mapped in mapping:
      source_value = row[mapped]
      dest_key = mapping[mapped]
      if type(dest_key) == str:
        applyMapped(new_row, dest_key, source_value, value_mappings, imagefield, imagepath)
      elif type(dest_key) == list:
        for multi_key in dest_key:
          applyMapped(new_row, multi_key, source_value, value_mappings, imagefield, imagepath)
  except KeyError:
    print("The key from the mapping named does not exist")


  # correct all qty that are below 0 to 0
  if int(new_row['quantity']) <= 0:
    new_row['quantity'] = 0;

  # ONLY USE THIS, IF THE SOURCE PRICE FORMAT IS GERMAN (,)
  # format the prices fields correctly
  #if new_row['start_price']:
  #  new_row['start_price'] = "{:10.2f}".format(locale.atof(new_row['start_price'])).strip()
    
  # ONLY USE THIS, IF THE SOURCE PRICE FORMAT IS GERMAN (,)
  #if new_row['reserve_price']:
  #q  new_row['reserve_price'] = "{:10.2f}".format(locale.atof(new_row['reserve_price'])).strip()

  # do not allow buyout prices at 0
  if not new_row['buyout_price']:
    return False

  # only allow if title is set
  if not new_row['name']:
    return False

  # ONLY USE THIS, IF THE SOURCE PRICE FORMAT IS GERMAN (,)
  #if new_row['buyout_price']:
  #  new_row['buyout_price'] = "{:10.2f}".format(locale.atof(new_row['buyout_price'])).strip()

  # randomly set hp features
  if random.choices([True, False], [0.05, 0.95])[0]:
    new_row['hpfeat'] = 1
  else: 
    new_row['hpfeat'] = 0

  # randomly set cat features
  if random.choices([True, False], [0.05, 0.95])[0]:
    print("is category feature")
    new_row['catfeat'] = 1
  else:
    print("is not category feature")
    new_row['catfeat'] = 0

  # skip if category cannot be found in the mapping
  if new_row['category_id'] and new_row['category_id'] in value_mappings['category_id'].values():
    return new_row
  else:
    return False

  return new_row

def startMapping():
    with open (sourcefile, 'r') as filein, open (destinationfile, 'w', newline='') as fileout:
        csvin = csv.DictReader(filein, skipinitialspace=True)
        
        csvout = csv.DictWriter(fileout, fieldnames = dataheader)
        csvout.writeheader()

        for idx, source_row in enumerate(csvin):
          index = idx

          # format price to german locale (only for starshooter)?
          row = mapRow(source_row)
          if row:
            csvout.writerow(row)

        print("Mapped " + str(index + 1) + " source data items.")
    # rsync /image folder with temp on gunatic folder
    #os.system("rsync -avz ./images/* root@gunatic.com:/var/www/html/temp")
    #split large csv into multople files
    split(open(destinationfile, 'r'), ',', 400)

def split(filehandler, delimiter=',', row_limit=1000,
          output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = next(reader)
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)

startMapping()