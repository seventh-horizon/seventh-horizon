#!/usr/bin/env python3
"""
Redacts INTERNAL blocks and obvious draft markers from a markdown source.
Usage: redact_public.py <src_md> <dst_md>
"""
import re, sys
if len(sys.argv) != 3:
    print("Usage: redact_public.py <src_md> <dst_md>")
    sys.exit(2)
src, dst = sys.argv[1], sys.argv[2]

email_re = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')
phone_re = re.compile(r'(?<!\d)(\+?\d[\d\-\s]{7,}\d)(?!\d)')

hide = False
with open(src, 'r', encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as o:
    for line in f:
        if '<!-- INTERNAL -->' in line:
            hide = True; continue
        if '<!-- /INTERNAL -->' in line:
            hide = False; continue
        if hide: 
            continue
        # Drop explicit draft flags
        if re.match(r'^\s*Draft:\s*true\s*$', line):
            continue
        # Light PII masking
        line = email_re.sub('[redacted-email]', line)
        line = phone_re.sub('[redacted-phone]', line)
        o.write(line)
