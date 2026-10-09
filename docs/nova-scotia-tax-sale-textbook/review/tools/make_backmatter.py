#!/usr/bin/env python3
"""Generate the textbook's Appendix C (statutes and official sources, by chapter and section) and
the Sources chapter from the chapters' `::: source` notes and the packet's source register.

    .venv/bin/python review/tools/make_backmatter.py          # writes src/chapters/98b-*.md and 99-sources.md

Only sources the chapters cite (by register number) are listed. Every statement printed is either
a provision reference and topic phrase copied from a source note, or a register entry copied from
docs/nova-scotia-tax-sale-book/research/sources.md with its research-snapshot hashes removed.
Rerun after editing source notes; review the output before building.
"""
import collections, os, re

P = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(P, "src", "chapters")
REGISTER = os.path.join(P, "..", "nova-scotia-tax-sale-book", "research", "sources.md")

PROV_RX = re.compile(r"\b(MGA|HRMC|Municipal Government Act|Halifax Regional Municipality Charter|Marketable Titles Act|"
                     r"Mineral Resources Act)\s+(ss?\.\s*[0-9][0-9A-Za-z().–\-]*(?:\s*(?:,|and)\s*[0-9][0-9A-Za-z().–\-]*)*)")
# Statute provisions, curated by hand from the source notes (topics are the notes' own wording).
# (MGA or other Act provision, HRMC provision or "", topic, [section ids])
PROVISIONS = [
    ("MGA s. 109(4)", "", "a tax-sale deed is exempt from municipal deed transfer tax", ["sec-09-build-backward", "sec-12-document"]),
    ("MGA ss. 133–142", "", "the steps before a sale, from tax lien to advertisement", ["sec-01-tax-sale"]),
    ("MGA s. 133", "HRMC s. 147", "tax lien", ["sec-01-first-clock"]),
    ("MGA s. 133(4)", "HRMC s. 147(4)", "a set-aside sale does not discharge the tax lien", ["sec-12-money"]),
    ("MGA s. 134", "", "eligibility and the three-year threshold", ["sec-01-first-clock"]),
    ("MGA ss. 137–140", "HRMC ss. 151–155", "preliminary notice, title search and notice to owner and interest holders; the municipality's title search before sale", ["sec-01-first-clock", "sec-04-baseline"]),
    ("MGA s. 139A", "HRMC s. 154", "a court-directed sale: a treasurer may seek a court order about arrears, interests conveyed, notice and the manner of sale", ["sec-04-four-destinations", "sec-08-deed"]),
    ("MGA s. 141", "HRMC s. 156", "public auction by default, tenders with council's consent, council's acceptable minimum", ["sec-01-notice", "sec-02-fields-pull", "sec-10-two-formats"]),
    ("MGA s. 142", "", "advertisement", ["sec-01-first-clock"]),
    ("MGA s. 142(2A)", "HRMC s. 157(2A)", "the advertised date, time and place", ["sec-10-breaks"]),
    ("MGA ss. 143, 148–149", "HRMC ss. 158–159, 163–164", "no sufficient bidder, municipal purchase and later sale subject to a council minimum; failed immediate payment and immediate re-offer; the missed three-business-day balance", ["sec-02-fields-pull", "sec-10-finish-line", "sec-10-breaks"]),
    ("MGA s. 144", "HRMC s. 159", "people prohibited from buying", ["sec-10-two-formats"]),
    ("MGA ss. 146–147", "HRMC ss. 161–162", "sale proceeds, the tax-sale surplus account and applications for surplus", ["sec-08-deed", "sec-12-money"]),
    ("MGA s. 148", "HRMC s. 163", "statutory payment forms, immediate payment and the three-business-day balance", ["sec-02-fields-pull", "sec-09-build-backward", "sec-10-finish-line"]),
    ("MGA s. 150", "HRMC s. 165", "certificate of sale after full payment, prepared and registered by the treasurer", ["sec-03-certificate", "sec-11-responsibility", "sec-13-record"]),
    ("MGA s. 151", "HRMC s. 166", "the certificate holder's powers and duties", ["sec-03-certificate", "sec-08-possession", "sec-11-responsibility"]),
    ("MGA s. 151(c)", "HRMC s. 166(c)", "insurance duty and deemed insurable interest", ["sec-03-certificate", "sec-11-responsibility"]),
    ("MGA ss. 152(1) and 155", "HRMC ss. 167(1) and 170", "six-month redemption and the older-arrears exception", ["sec-02-fields-pull", "sec-03-certificate", "sec-03-endings", "sec-11-redemption", "sec-12-document", "sec-13-record"]),
    ("MGA s. 152(2)–(4)", "HRMC s. 167(2)–(4)", "redemption categories and the redemption price", ["sec-03-endings", "sec-11-responsibility", "sec-11-redemption"]),
    ("MGA ss. 153–154", "HRMC ss. 168–169", "purchaser repayment and the end of the purchaser's rights", ["sec-03-endings", "sec-11-redemption", "sec-13-record"]),
    ("MGA ss. 155–156", "HRMC ss. 170–171", "deed request after the applicable wait, and the tax deed's effect", ["sec-03-endings", "sec-06-route", "sec-08-deed", "sec-12-document", "sec-13-record"]),
    ("", "HRMC ss. 147–172", "Halifax operates under the Charter rather than the Municipal Government Act's tax-sale division", ["sec-01-halifax", "sec-10-breaks", "sec-11-redemption"]),
    ("Marketable Titles Act s. 6(2)–(6)", "", "the six-year period and its qualifications", ["sec-12-document", "sec-12-money"]),
    ("Mineral Resources Act s. 5", "", "Crown ownership of minerals", ["sec-05-small-find"]),
    ("Mineral Resources Act ss. 25–26", "", "private-land consent and surface-access applications", ["sec-05-small-find"]),
    ("Mineral Resources Act s. 27", "", "mine-connected vesting orders and deemed expropriation", ["sec-05-small-find"]),
]

SHORT = {"Municipal Government Act": "MGA", "Halifax Regional Municipality Charter": "HRMC"}


def notes():
    """(chapter number, section id, section title, note text) for every source note."""
    out = []
    for f in sorted(os.listdir(CH)):
        m = re.match(r"(\d\d)-", f)
        if not m or not (1 <= int(m.group(1)) <= 13):
            continue
        n = int(m.group(1))
        sec = (None, None)
        lines = open(os.path.join(CH, f)).read().split("\n")
        i = 0
        while i < len(lines):
            h = re.match(r"^## (.*?)\s*\{#([\w-]+)\}\s*$", lines[i])
            if h:
                sec = (h.group(2), h.group(1))
            if lines[i].strip() == "::: source":
                j = i + 1
                body = []
                while lines[j].strip() != ":::":
                    body.append(lines[j])
                    j += 1
                out.append((n, sec[0], sec[1], " ".join(" ".join(body).split())))
                i = j
            i += 1
    return out


def numbers(text):
    found = set()
    for grp in re.findall(r"\bnos?\.\s*([0-9][0-9,–\- ]*(?:and [0-9]+)?)", text):
        for part in re.split(r",|and", grp):
            part = part.strip().rstrip("–-")
            if re.fullmatch(r"\d+[–-]\d+", part):
                a, b = map(int, re.split(r"[–-]", part))
                found.update(range(a, b + 1))
            elif part.isdigit():
                found.add(int(part))
    return found


def first_sentence(t):
    """The entry's citation: everything up to the first sentence break outside a link. Later sentences in
    the register describe what a source says; the chapters make those statements where the book needs them."""
    depth = 0
    for i, c in enumerate(t):
        depth += c in "[(" and 1 or (c in "])" and -1 or 0)
        if c == "." and depth == 0 and t[i + 1:i + 3].strip()[:1].isupper() and not re.search(r"\b(no|ss?|pp|Jr|St)$", t[:i]):
            return t[:i + 1]
    return t


def register():
    """{number: (heading, entry text)} from sources.md."""
    heading, out = "", {}
    for line in open(REGISTER).read().split("\n"):
        if line.startswith("## "):
            heading = line[3:].strip()
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            t = m.group(2)
            t = re.sub(r"\s*(?:Research|FAQ) snapshot SHA-256:?\s*`[0-9a-f]+`[^.]*\.?", "", t)
            t = re.sub(r"(especially page \d+):.*$", r"\1.", t)     # the page's figures are given in the chapters
            out[int(m.group(1))] = (heading, first_sentence(t.strip()))
    return out


def where(locs):
    seen, parts = set(), []
    for n, sid, title in sorted(locs, key=lambda x: (x[0], x[1] or "")):
        if (n, sid) in seen:
            continue
        seen.add((n, sid))
        parts.append(f"[{n} · {title}](#{sid})" if sid else f"Chapter {n}")
    return "; ".join(parts)


def provisions(all_notes):
    rows = collections.OrderedDict()
    for n, sid, title, text in all_notes:
        for clause in re.split(r";\s*", text):
            ms = list(PROV_RX.finditer(clause))
            if not ms:
                continue
            refs = " · ".join(f"{SHORT.get(m.group(1), m.group(1))} {m.group(2).strip().rstrip('.,')}" for m in ms)
            topic = clause[:ms[0].start()]
            topic = re.sub(r"^.*?\):\s*", "", topic) if "):" in topic else topic
            topic = topic.strip(" ,:(").strip()
            topic = re.sub(r"\s+", " ", topic)
            key = refs
            if key not in rows:
                rows[key] = {"topic": topic, "locs": set()}
            rows[key]["locs"].add((n, sid, title))
    return rows


def main():
    all_notes = notes()
    reg = register()
    cited = collections.defaultdict(set)
    for n, sid, title, text in all_notes:
        for no in numbers(text):
            cited[no].add((n, sid, title))

    def sortkey(ref):
        m = re.search(r"(MGA|HRMC|Act)\s+ss?\.\s*(\d+)", ref)
        return (0 if ref.startswith(("MGA", "HRMC")) else 1, int(m.group(2)) if m else 0, ref)

    prov = provisions(all_notes)
    out = ["---", "label: C", "kicker: Appendix C", "running_head: C · Statutes and sources", "gloss: acronyms",
           "intro: >-", "  Where each statute provision and official source is used, by chapter and section. Section",
           "  numbers and source numbers come from the source notes that close each section.", "---", "",
           "# Index of Statutes and Official Sources", "",
           "## Statute provisions", "",
           "The Municipal Government Act frame applies outside Halifax; the Halifax Regional Municipality "
           "Charter applies in Halifax. Where a source note gives both, they appear together. The topic is the "
           "source note's own wording.", "",
           "| Provision | Halifax Charter | Topic | Where |", "|---|---|---|---|"]
    titles = {sid: (n, title) for n, sid, title, _ in all_notes}
    for ref, hrmc, topic, sids in PROVISIONS:
        missing = [x for x in sids if x not in titles]
        if missing:
            raise SystemExit(f"unknown section ids {missing} for {ref or hrmc}")
        out.append(f"| {ref or '—'} | {hrmc or '—'} | {topic} | {where([(titles[x][0], x, titles[x][1]) for x in sids])} |")
    out += ["", "## Official sources", "",
            "Numbers match the Sources chapter at the end of the book.", "",
            ]
    for no in sorted(cited):
        if no not in reg:
            print(f"warning: source no. {no} cited but not in the register")
            continue
        name = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", reg[no][1])
        name = re.split(r",\s*(?:consolidated|refreshed|retrieved|including|especially|which|prepared|effective|\d{4}-\d\d-\d\d)|\.\s", name)[0]
        name = name.replace("`", "").rstrip(".")
        out.append(f"{no}. **{name}.** {where(cited[no])}.")
    open(os.path.join(CH, "98b-statutes-and-sources.md"), "w").write("\n".join(out) + "\n")

    src = ["---", "running_head: Sources and credits", "toc: true", "gloss: acronyms", "---", "",
           "# Sources and Credits", "",
           "These are the official and explanatory sources the source notes cite, numbered as in the 2026 "
           "edition's source register. Primary and official sources control; explanatory sources are labelled "
           "separately. Retrieved July 18, 2026 unless noted; the register records later refreshes, made "
           "July 19–22, 2026, beside each entry. Live sale dates, property lists, fees, tax rates and map "
           "services change: check the current source.",
           "",
           "Source notes also give evidence-note identifiers, such as LAW-007 or MAP-001. They refer to the "
           "evidence notes in the 2026 edition's public development packet (docs/nova-scotia-tax-sale-book/"
           "research/evidence-notes.md in the explainer-audiobooks repository), where each claim is tied to "
           "its source and to a boundary note saying what the source does not establish.", ""]
    last = None
    for no in sorted(cited):
        if no not in reg:
            continue
        heading, text = reg[no]
        if heading != last:
            src += ["", f"### {heading}", ""]
            last = heading
        if no == 48:     # the map's source repository is not printed (see book.yaml forbid list)
            text = "NS Marks The Spot, the checked production build of the public map used in Chapter 5: its source receipt and live public map."
        src.append(f"{no}. {text}")
    src += ["", "### Credits", "",
            "- Cover art: *The Packet Lifts*, the cover of the 2026 edition, used unchanged.",
            "- Figures: Appendix D lists every figure, with its credit and, for the kept map screenshots, the "
            "Province of Nova Scotia attribution.",
            "- Type: Source Serif 4 and Atkinson Hyperlegible Next, both under the SIL Open Font License.",
            "- Licence: Creative Commons Attribution 4.0 International, as for the 2026 edition.",
            "- Contains information obtained under license from the Province of Nova Scotia which is provided "
            "without warranty or liability for errors or omissions."]
    open(os.path.join(CH, "99-sources.md"), "w").write("\n".join(src) + "\n")
    print(f"notes: {len(all_notes)}, provisions: {len(PROVISIONS)}, sources cited: {len(cited)}, figures: {dict(figures())}")


def figures():
    """Appendix D: every figure, numbered as the build numbers them, with its title and credit line."""
    out = ["---", "label: D", "kicker: Appendix D", "running_head: D · Figures", "gloss: acronyms",
           "intro: >-", "  Every figure in the book, with its credit. Kept figures are reproduced from the 2026 edition;",
           "  redrawn figures carry the same content as the 2026 edition's figure of that number; new figures",
           "  are drawn from the chapter text.", "---", "", "# List of Figures", ""]
    counts = collections.Counter()
    for f in sorted(os.listdir(CH)):
        m = re.match(r"(\d\d)-", f)
        if not m or not (1 <= int(m.group(1)) <= 13):
            continue
        n = int(m.group(1))
        s = open(os.path.join(CH, f)).read()
        title = re.search(r"^# (.+)$", s, re.M).group(1)
        rows = []
        for k, fm in enumerate(re.finditer(r"!\[(.*?)\]\(([^)]+)\)\{#(fig-[^ }]+)", s, re.S), 1):
            cap, src, fid = fm.groups()
            cap = " ".join(cap.split())
            lead = re.match(r"\*\*(.+?)\*\*", cap)
            name = lead.group(1).rstrip(".") if lead else fid
            credit = re.findall(r"((?:Redrawn|New figure|Illustration from|Screenshot from)[^.]*(?:\.[^.]*?2026 edition[^.]*)?\.)", cap)
            credit = credit[-1] if credit else ""
            kind = "kept" if "/kept/" in src else ("redrawn" if credit.startswith("Redrawn") else "new")
            counts[kind] += 1
            if "Province of Nova Scotia" in cap:
                credit += " Province of Nova Scotia attribution in the caption."
            rows.append(f"| [{n}.{k}](#{fid}) | {name} | {credit.strip()} |")
        if rows:
            out += [f"### Chapter {n} · {title}", "", "| Figure | Title | Credit |", "|---|---|---|"] + rows + [""]
    out.insert(out.index("# List of Figures") + 2,
               f"{sum(counts.values())} figures: {counts['kept']} kept from the 2026 edition, {counts['redrawn']} redrawn "
               f"and {counts['new']} new.\n")
    open(os.path.join(CH, "98c-figures.md"), "w").write("\n".join(out) + "\n")
    return counts


if __name__ == "__main__":
    main()
