#!/usr/bin/env python
from optparse import OptionParser
from glob import glob
from json import load
from categories_map import CMSSW_CATEGORIES
from sys import exit

STATES = {
  "pending": "P",
  "approved": "A",
  "rejected": "R",
  "started": "S",
  "hold": "H",
}

POSITIONS = {}
pindex = 0
for cat in sorted(CMSSW_CATEGORIES.keys()):
  POSITIONS[cat]=pindex
  pindex+=1

def dumpCategoriesJS():
  cats= "var categories = {"
  pindex = 0
  for cat in sorted(CMSSW_CATEGORIES.keys()):
    cats+='\n  %s : "%s",' % (pindex, cat)
    pindex+=1
  return cats.strip(",")+"\n};"
  
def labelsToState(labels):
  allParts = [x.split("-", 1) for x in labels if "-" in x]
  validParts = [x for x in allParts if x[0] in POSITIONS.keys()]
  states = [(STATES[x[1]], POSITIONS[x[0]]) for x in validParts]
  iniValue = ["N" for i in xrange(len(POSITIONS))]
  for x in states: iniValue[x[1]] = x[0]
  return "".join(iniValue)

if __name__ == "__main__":
  parser = OptionParser(usage="%prog")
  parser.add_option("-p", "--prs", dest="prs_dir", help="Directory with Pull requests stats", type=str, default=None)
  parser.add_option("-c", "--categories", dest="categories", help="Dump Categories JS", action="store_true", default=False)
  opts, args = parser.parse_args()

  if opts.categories:
    print dumpCategoriesJS()
    exit(0)
  # This is the header of the files and will force a rewrite of the file
  # if a mismatching is found.
  schema= "Creation,MergeTime,id,isPr,N. of Comments,Closed,N. Labels,author, labelStatus, lastUpdateTime, milestoneTitle"

  prs = {}
  for pr_json in glob(opts.prs_dir+"/*/*.json"):
    issue = load(open(pr_json))
    if not 'number' in issue: continue
    labels = issue['labels']
    decodedLabels = labelsToState(labels)
    createdAt = int(issue['created_at'])
    closedAt = ('closed_at' in issue and issue['closed_at']) and int(issue['closed_at']) or "NA"
    isClosed = ('closed_at' in issue and issue['closed_at']) and 1 or 0
    isPr = 1
    updateAt = int(issue['updated_at'])
    if ('milestone' in issue and issue['milestone']):
      milestone = issue['milestone']
    else:
      milestone = "-"

    prs[createdAt] = [createdAt, closedAt, issue['number'], isPr, issue['comments'], isClosed, len(labels), issue['user'], decodedLabels, updateAt, milestone]

  print schema
  for c in reversed(sorted(prs.keys())):
    print ",".join(str(x) for x in prs[c])

