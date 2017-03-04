import CloudFlare
import json
import re
from optparse import OptionParser

import os

class Cloudflare:

    def __init__(self):
        self.cf = CloudFlare.CloudFlare(email='moshe@egis-software.com',
                                        token=os.environ['CLOUDFLARE_API'],
                                        raw=True)


    def get_zone_id(self):
        # query for the zone name and expect only one value back
        try:
            raw_results = self.cf.zones.get(params = {'name':'papertrail.co.za','per_page':1})
            zones = raw_results['result']
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.get %d %s - api call failed' % (e, e))
        except Exception as e:
            exit('/zones.get - %s - api call failed' % (e))

        if len(zones) == 0:
            exit('No zones found')

        # extract the zone_id which is needed to process that zone
        zone = zones[0]
        return zone['id']


    def list(self):
        zone_id = self.get_zone_id()
        page_number = 0
        records = {}
        while True:
            # request the DNS records from that zone
            try:
                raw_dns_results = self.cf.zones.dns_records.get(zone_id,
                                params = {'per_page':100,'page':page_number})
                dns_records = raw_dns_results['result']
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.get %d %s - api call failed' % (e, e))

            for rec in dns_records:
                try:
                    records[rec['name']] =  rec
                except Exception, e:
                    print str(e)

            total_pages = raw_dns_results['result_info']['total_pages']
            page_number += 1
            if page_number > total_pages:
                break
        return records


    def find(self, host):
        hosts = self.list()
        for rec in hosts:
            try:
                if host == rec:
                    return {
                        "id": hosts[rec]['id'],
                        "name": hosts[rec]['name'],
                        "ip": hosts[rec]['content'],
                        "zone_id": hosts[rec]['zone_id']
                    }
            except Exception, e:
                print str(e)


    def is_valid_ip(self, ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
        return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

    def create_entry(self, ip, host):
        if "papertrail.co.za" not in host:
            host = "%s.papertrail.co.za" % host
        print "Looking up %s" % host
        record = self.find(host)
        if record == None:
            print "adding ip %s -> %s" % (ip, host)
            zone_id = self.get_zone_id()
            try:
                if self.is_valid_ip(ip):
                    raw_dns_results = self.cf.zones.dns_records.post(zone_id,
                                    data = {'type':'A', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
                else:
                    raw_dns_results = self.cf.zones.dns_records.post(zone_id,
                                    data = {'type':'CNAME', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.post %d %s - api call failed' % (e, e))
        else:
   
            try:
                if self.is_valid_ip(ip):
                    print "updating ip %s -> %s" % (ip, host)
                    raw_dns_results = self.cf.zones.dns_records.put(record['zone_id'], record['id'],
                                    data = {'id': record['id'], 'type':'A', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)
                else:
                    print "updating cname %s -> %s" % (ip, host)
                    raw_dns_results = self.cf.zones.dns_records.put(record['zone_id'],record['id'],
                                    data = {'id': record['id'],'type':'CNAME', 'name': host, 'content': ip})
                    print json.dumps(raw_dns_results, indent=5)

            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.put %d %s - api call failed' % (e, e))


    def delete_entry(self, host):
        if "papertrail.co.za" not in host:
            host = "%s.papertrail.co.za" % host
        print "Looking up %s" % host
        record = self.find(host)
        if record == None:
            print "Record not found"
            exit(1)
        else:
            print "deleting %s" % (host)
            try:
                raw_dns_results = self.cf.zones.dns_records.delete(record['zone_id'], record['id'])
                print json.dumps(raw_dns_results, indent=5)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                exit('/zones/dns_records.put %d %s - api call failed' % (e, e))


def main():
    parser = OptionParser()
    parser.add_option(
        "-i", "--ip", dest="ip", help="The IP address of the instance to use")
    parser.add_option("-d", "--dns", dest="dns", help="A dns hostname to name")

    parser.add_option("-l", "--list", dest="list", action="store_true",  help="List all cloudflare entries")

    parser.add_option("--ips", dest="ips", action="store_true",  help="List all cloudflare IP's")
    parser.add_option("--del", dest="del_ent", action="store_true",  help="Delete cloudflare entry")
    (options, args) = parser.parse_args()


    if (options.list):
        hosts = Cloudflare().list()
        for host in hosts:
            print "%s = %s" % (host, hosts[host]['content'])
    elif (options.ips):
        hosts = Cloudflare().list()
        for host in hosts:
            print hosts[host]['content']
    elif (options.del_ent):
        if options.dns != None:
            Cloudflare().delete_entry(options.dns)

    if (options.dns != None and options.ip != None):
        Cloudflare().create_entry(options.ip, options.dns)


if __name__ == "__main__":
    main()
