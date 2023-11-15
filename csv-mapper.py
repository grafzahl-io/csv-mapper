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
##
## Example
## python3 csv-mapper.py source/source_file.csv dsit/destination_file.csv --imagepath="https://yourhost.com/temp/" --imagefield="image"
import csv
import sys
import collections
import json
import argparse
import locale
import os
import random
import re
import glob

# change this if the price format is not in german
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

parser=argparse.ArgumentParser(description='example: python3 csv-mapper.py source/source_file.csv dist/destination_file.csv --imagepath="http://google.de/" --imagefield="image"')
parser.add_argument('sourcefile', help='filepath to the source where the data is mapped from')
parser.add_argument('destinationfile', help='filepath to the destination file')
parser.add_argument("-imgp", "--imagepath", help='Adds this path to all imported image filenames')
parser.add_argument("-imgf", "--imagefield", help='Define the field name (destination key) on which the image filepath is prepend to')

options=parser.parse_args()
sourcefile=options.sourcefile
destinationfile=options.destinationfile
imagepath=options.imagepath
imagefield=options.imagefield

# the dist / target csv header
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
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  field_handle = os.path.join(BASE_DIR, "config/csv-field-mappings.json")
  static_file = open(field_handle)
  field_mappings = json.load(static_file)
  return field_mappings

def getMergeConfig():
  # get merge config
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  merge_config_handle = os.path.join(BASE_DIR, "config/csv-additional-related-mapping.json")
  merge_config_file = open(merge_config_handle)
  merge_config = json.load(merge_config_file)
  return merge_config

def findRowToMerge(row, searchterm, search_in, operator, targetrows):
  # use second csv to find a matching row to merge into
  header = targetrows[0]
  for trow in targetrows[1:]:
    if operator == "contains":
      if re.search(searchterm, trow[header.index(search_in)]):
        return trow
    if operator == "equal":
      if trow[header.index(search_in)] == searchterm:
        return trow

  return False

def getAvailableStatics():
  # get static data to impelment to current import
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  static_mapping_handle = os.path.join(BASE_DIR, "config/csv-static-mappings.json")
  static_file = open(static_mapping_handle)
  static_fields = json.load(static_file)
  return static_fields

def mapValues():
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  static_list_handle = os.path.join(BASE_DIR, "config/csv-list-mappings.json")
  static_file = open(static_list_handle)
  value_mappings = json.load(static_file)
  return value_mappings

def applyMapped(new_row, dest_key, source_value, value_mappings, imagefield, imagepath):
  new_row[dest_key] = source_value

  if bool(value_mappings):
    if dest_key in value_mappings:
      if source_value in value_mappings[dest_key]:
        new_row[dest_key] = value_mappings[dest_key][source_value]

  if dest_key == imagefield and imagepath:
    new_row[dest_key] = imagepath + new_row[dest_key]

  return new_row

def canRowBeImported(row):
  return len(row["Productname"]) > 0

def mapRow(row):
  if not canRowBeImported(row):
    return False

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

  # merge mapped
  merge_config = getMergeConfig()
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  if len(merge_config):
    for merge_c in merge_config:
      relatedfile_fullpath = os.path.join(BASE_DIR,merge_c["related-data-file"])
      merge_file = open(relatedfile_fullpath)
      csv_data = csv.reader(merge_file, delimiter=",")
      merge_data = list(csv_data)

      # search for matching data 
      res = findRowToMerge(row, row[merge_c["matching-rule-in-main"]["column"]], merge_c["related-data-file-id-column"], merge_c["matching-rule-in-main"]["operator"], merge_data)
      # map res and put into new row
      if res:
        header = merge_data[0]
        # @todo mapping through available methods again to inject the related data
        related_row = dict(zip(header, res))
        # print(related_row)
        try:
          for mapped in mapping:
            source_value = related_row[mapped]
            dest_key = mapping[mapped]
            if type(dest_key) == str:
              applyMapped(new_row, dest_key, source_value, value_mappings, imagefield, imagepath)
            elif type(dest_key) == list:
              for multi_key in dest_key:
                applyMapped(new_row, multi_key, source_value, value_mappings, imagefield, imagepath)
        except KeyError:
          print("The key from the mapping named does not exist for related")

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

  # compile for field column
  product_name_parts = row["Productname"].lower().split(" ")
  new_row['Handle'] = product_name_parts[0] + "-" + product_name_parts[1]

  # randomly set hp features
  if row["Productname"]:
    # get the second word of product name to get image name
    base_model_name = row["Productname"].split(" ")[1]
    # find all filenames that exsist in /source/images with the base_model_name
    product_images = []
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(BASE_DIR, "source/images")
    os.chdir(image_dir)
    current_handle = new_row["Handle"]
    new_row["Handle"] = [current_handle]

    for file in glob.glob(base_model_name + '*'):
      product_images.append(imagepath + file)
      # also push the handle again @todo attention this has relations to variable config
      new_row["Handle"].append(current_handle)

    # for output into shopify, every of these images needs to have a separate row in csv
    # @todo this is related to config and hard coded: move this type of compilation fields into a config layer
    new_row['Image Src'] = product_images

  return new_row

def startMapping():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sourcefile_fullpath = os.path.join(BASE_DIR,sourcefile)
    distfile_fullpath = os.path.join(BASE_DIR,destinationfile)

    with open (sourcefile_fullpath, 'r') as filein, open (distfile_fullpath, 'w', newline='') as fileout:
        csvin = csv.DictReader(filein, skipinitialspace=True)
        
        csvout = csv.DictWriter(fileout, fieldnames = dataheader)
        csvout.writeheader()

        for idx, source_row in enumerate(csvin):
          index = idx

          # format price to german locale (only for starshooter)?
          row = mapRow(source_row)
          if row:
            # csvout.writerow(row)

            # check if the any field contains a list, to write a new row by id (handle) for every list item
            ind = 0
            # check longest list in rows
            for col in row.values():
              if type(col) == list:
                if len(col) > ind:
                  ind = len(col)

            print(ind)

            while ind >= 0:
              additional = []
              if ind == 0:
                for col in row.values():
                  if type(col) == list and len(col):
                    additional.append(col[0])
                  else:
                    additional.append(col)
              else:
                for col in row.values():
                  if type(col) == list and len(col) > ind:
                    additional.append(col[ind])
                  else:
                    additional.append("")
              # write
              ind = ind - 1
              fullrow = dict(zip(row.keys(), additional))
              csvout.writerow(fullrow)

                

        print("Mapped " + str(index + 1) + " source data items.")
    #split large csv into multople files
    split(open(distfile_fullpath, 'r'), ',', 400)

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
