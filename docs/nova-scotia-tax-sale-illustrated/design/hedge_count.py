#!/usr/bin/env python3
"""Count sentences that hedge with a negative construction. Usage: hedge_count.py FILE..."""
import re, sys
NEG = re.compile(r"\b(not|cannot|can't|doesn't|don't|isn't|aren't|won't|never|neither|nor|no longer)\b", re.I)
for f in sys.argv[1:]:
    t = open(f).read()
    t = re.sub(r"(?s)^---.*?---", "", t)            # front matter
    t = re.sub(r"<!--.*?-->", "", t)                 # figure markers
    t = re.sub(r"(?m)^(:::.*|!\[.*)$", "", t)
    sents = [s for s in re.split(r"(?<=[.?!])\s+", t) if s.strip()]
    neg = [s for s in sents if NEG.search(s)]
    words = len(t.split())
    print(f"{f}: {words} words, {len(sents)} sentences, {len(neg)} with a negative ({100*len(neg)/max(1,len(sents)):.0f}%)")
