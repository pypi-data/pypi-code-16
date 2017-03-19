import sys
import argparse
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import json

VERSION = '0.0.2'

class AvroTool:

    def __init__(self):
        pass

    def usage(self):
        print ""
        print "AvroTool v" + VERSION
        print "Usage: avro COMMMAND [schema|extract]"
        print ""

    def extract(self, args):
        input_filename = args.f
        f = open(input_filename, 'rb')
        reader = avro.datafile.DataFileReader(f,avro.io.DatumReader())

        schema = reader.datum_reader.writers_schema
        schema_json = json.loads(str(schema))

        if args.columns is not None:
            # specific columns only
            #schema_json = json.loads(str(schema))
            #fields = schema_json["fields"]
            fields = args.columns.split(",");
            for record in reader:
                #print record
                splits = []
                for field in fields:
                    splits.append(str(record[field]))
                print "\t".join(splits)
        else:
            # all columns
            #reader = DataFileReader(open("users.avro", "rb"), DatumReader())
            schema_json = json.loads(str(schema))
            fields = schema_json["fields"]
            for record in reader:
                #print record
                splits = []
                for field in fields:
                    splits.append(str(record[field["name"]]))
                print "\t".join(splits)

        f.close()

    def schema(self, args):
        input_filename = args.f
        f = open(input_filename, 'rb')
        reader = avro.datafile.DataFileReader(f,avro.io.DatumReader())
        schema = reader.datum_reader.writers_schema
        f.close()
        schema_json = json.loads(str(schema))
        if args.format == 'json':
            print json.dumps(schema_json, indent=4)
        else:
            namespace = schema_json["namespace"]
            name = schema_json["name"]
            fields = schema_json["fields"]
            for field in fields:
                print field["name"]

def main():
    if len(sys.argv) < 2:
        tool = AvroTool()
        tool.usage()
        sys.exit(1)

    action = sys.argv[1]
    a = sys.argv[2:]
    parser = argparse.ArgumentParser(description='AvroTool v' + VERSION, prog="avro", epilog="The epilog")
    parser.add_argument('-f', metavar="INPUT_FILE", required=True, help='The avro file to use')
    parser.add_argument('-columns', required=False, metavar="COLUMNS", help="The columns to extract (comma-separated)")
    parser.add_argument('-format', required=False, choices=['json', 'text', 'avro'], default='json', help="The output format for the schema")
    args, unknown = parser.parse_known_args(a)
    tool = AvroTool()
    if action == "schema":
        tool.schema(args)
    elif action == "extract":
        tool.extract(args)
    else:
        tool.usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
