#!/usr/bin/env python

from utils_print import my_print, print_list
from utils_requests import vulnerable_storage
from utils_cloudflare import list_zones, list_dns_records


vulnerable_domains = []

if __name__ == "__main__":

    print("Searching for vulnerable subdomains with missing storage buckets")
    i = 0
    zones = list_zones()

    for zone in zones:
        records = list_dns_records(zone["Id"], zone["Name"])

        cname_records = [
            r
            for r in records
            if r["Type"] in ["CNAME"]
            and (
                ("amazonaws.com" in r["Value"] and ".s3" in r["Value"])
                or "cloudfront.net" in r["Value"]
                or "c.storage.googleapis.com" in r["Value"]
            )
        ]

        for record in cname_records:
            i = i + 1
            result = vulnerable_storage(record["Name"])

            if result:
                vulnerable_domains.append(record["Name"])
                my_print(f"{str(i)}. {record['Name']}", "ERROR")
            else:
                my_print(f"{str(i)}. {record['Name']}", "SECURE")

    count = len(vulnerable_domains)
    my_print("\nTotal vulnerable subdomains with missing storage buckets: " + str(count), "INFOB")

    if count > 0:
        my_print("Vulnerable subdomains with missing storage buckets:", "INFOB")
        print_list(vulnerable_domains)
