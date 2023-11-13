# Getting started
In order to start a mapping, you need
to setup the configuration to tell the script
what to do

## setup your configuration
create the following files in `/config`
- `csv-additional-related-mapping.json`
  used to merge related data row-wise from another csv file

- `csv-field-mappings.json`
  used to map 1 to 1 fields from source to destination

- `csv-list-mappings.json`
  used to map values by a list for a specific field

- `csv-static-mappings.json`
  used to insert static data that is static for an import for every row