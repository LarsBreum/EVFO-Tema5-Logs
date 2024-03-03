import re


log_entry = "Sep 26 11:40:11 bridge useradd: new user: name=pcap, uid=77, gid=77, home=/var/arpwatch, shell=/sbin/nologin"
log_entry = "Sep 26 11:40:11 bridge useradd[1937]: new user: name=pcap, uid=77, gid=77, home=/var/arpwatch, shell=/sbin/nologin"

pattern = r'(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}) (\w+) (\w+)\[(\d+)\]: (.*)'
pattern = r'(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}) (\w+) (\w+)(?:\[(\d+)\])?: (.*)'

matches = re.match(pattern, log_entry)

if matches:
    date_time = matches.group(1)
    host = matches.group(2)
    program = matches.group(3)
    process_id = matches.group(4)
    message = matches.group(5)
    
    print("Date & Time:", date_time)
    print("Host:", host)
    print("Program:", program)
    print("Process ID:", process_id)
    print("Message:", message)
else:
    print("No match")
