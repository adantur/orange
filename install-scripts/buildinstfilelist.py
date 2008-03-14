import os, re, sys, md5
import pysvn

basedir = sys.argv[1]
fileprefix = sys.argv[2]
mac = len(sys.argv) > 3 and sys.argv[3] == "mac"

if basedir[-1] != "\\":
    basedir += "\\"
#basedir = "c:\\janez\\orange\\"

print "Constructing file lists for Orange in '%s', prefix is '%s'" % (basedir, fileprefix)

snapshot = fileprefix[:8] == "snapshot"
protoDir = "orange\\orangewidgets\\prototypes\\"

exclude = [x.lower().replace("/", "\\")[:-1] for x in open(basedir+"orange\\exclude.lst", "rt").readlines()]
file_re = re.compile(r'/(?P<fname>.*)/(?P<version>.*)/(?P<date>.*)/[^/]*/')

def computeMD(filename):
    existing = open(filename, "rb")
    currmd = md5.new()
    currmd.update(existing.read())
    existing.close()
    return currmd.hexdigest()

def excluded(fname):
    fname = fname.lower()
    if not snapshot and fname[:len(protoDir)] == protoDir:
        print "Excluded %s (prototype)" % fname
        return 1

    for ex in exclude:
        if ex==fname[:len(ex)]:
            print "Excluded %s (as %s)" % (fname, ex)
            return 1

outfs = ""
hass = ""
down = ""

def buildListLow(root_dir, here_dir, there_dir, regexp, recursive):
    global outfs, hass, down
    
    SVNclient = pysvn.Client()

    if not os.path.exists(root_dir+here_dir):
        return
    
    whatsDownEntries = None
    directories = []
    for fle in os.listdir(root_dir+here_dir):
        tfle = root_dir+here_dir+fle
        if fle == ".svn" or excluded("orange\\"+there_dir+fle):
            continue
        if os.path.isdir(tfle):
            if recursive:
                directories.append((here_dir, there_dir, fle))
        else:
            if not regexp or regexp.match(fle):
                if not whatsDownEntries:
                    if not mac:
                        outfs += '\nSetOutPath "$INSTDIR\\%s"\n' % there_dir
                    if there_dir[:14] == "orangeWidgets\\" and there_dir.count("\\")==2 and there_dir[14:-1]!="icons":
                        if mac:
                            down += there_dir[14:-1] + "\n" 
                        else:
                            hass += 'FileWrite $WhatsDownFile "+%s$\\r$\\n"\n' % there_dir[14:-1]

                    whatsDownEntries = {}
                    for ent in SVNclient.status(root_dir+here_dir, recurse=0):
                        if ent.entry == None or ent.entry.kind <> pysvn.node_kind.file:
                            continue
                        fname, version = ent.entry.name, ent.entry.commit_revision.number
                        whatsDownEntries[fname] = (there_dir+fname, version, computeMD(root_dir+here_dir+fname))

                if whatsDownEntries.has_key(fle):
                    if mac:
                        outfs += tfle + "\n"
                        down += '%s=%s:%s\n' % whatsDownEntries[fle]
                    else:
                        outfs += 'File "%s"\n' % tfle
                        outfs += 'FileWrite $WhatsDownFile "%s=%s:%s$\\r$\\n"\n' % whatsDownEntries[fle]

    for here_dir, there_dir, fle in directories:
        buildListLow(root_dir, here_dir+fle+"\\", there_dir+fle+"\\", regexp, recursive)


def buildList(root, here, there, regexp, fname, recursive=1):
    global outfs, hass
    outfs = hass = ""
    buildListLow(root, here, there, regexp and re.compile(regexp, re.IGNORECASE), recursive)
    open(fileprefix+"_"+fname+".inc", "wt").write(hass+outfs)
    if mac:
        open(fileprefix+"_"+fname+".down", "wt").write(down)

def buildLists(rhter, fname):
    global outfs, hass
    outfs = hass = ""
    for root, here, there, regexp, recursive in rhter:
        buildListLow(root, here, there, regexp and re.compile(regexp, re.IGNORECASE), recursive)
    open(fileprefix+"_"+fname+".inc", "wt").write(hass+outfs)


#def buildPydList(root, here, there, fname, lookinver="25\\"):
#    here = root + here
#    outf = open(fileprefix+"_"+fname+".inc", "wt")
#    outf.write('\nSetOutPath "$INSTDIR\\%s"\n' % there)
#    for fle in os.listdir(here+lookinver):
#        if fle[-4:] == ".pyd":
#            outf.write('File "%s${PYVER}\\%s"\n' % (here, fle))
#            outf.write('FileWrite $WhatsDownFile "%s=1.0:%s$\\r$\\n"\n' % (there+fle, computeMD(here+lookinver+fle)))

buildList(basedir, "orange\\", "", "((.*[.]py)|(ensemble.c)|(COPYING)|(c45.dll))\\Z", "base", 0)
#buildPydList(basedir, "", "", "binaries")

buildList(basedir, "orange\\OrangeWidgets\\", "OrangeWidgets\\", ".*[.]((py)|(png))\\Z", "widgets")
buildList(basedir, "orange\\OrangeCanvas\\", "OrangeCanvas\\", ".*[.]((py)|(pyw)|(png))\\Z", "canvas")

# buildLists([(basedir, "genomics\\", "OrangeWidgets\\Genomics\\", ".*[.]py\\Z", 0),
#            (basedir, "genomics\\GO\\", "OrangeWidgets\\Genomics\\GO\\", "", 0),
#            (basedir, "genomics\\Annotation\\", "OrangeWidgets\\Genomics\\Annotation\\", "", 0),
#            (basedir, "genomics\\Genome Map\\", "OrangeWidgets\\Genomics\\Genome Map\\", "", 0)], "genomics")

buildLists([(basedir, "orange\\doc\\", "doc\\", "", 0), 
            (basedir, "orange\\doc\\datasets\\", "doc\\datasets\\", "", 0),
            (basedir, "orange\\doc\\reference\\", "doc\\reference\\", "", 0),
            (basedir, "orange\\doc\\modules\\", "doc\\modules\\", "", 0),
            (basedir, "orange\\doc\\widgets\\", "doc\\widgets\\", "", 0),
            (basedir, "orange\\doc\\ofb\\", "doc\\ofb\\", "", 0)], "doc")

