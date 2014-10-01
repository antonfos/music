# Written by Anton Foster April 2013
# This is to be put in the public domain
# The script is to process a directory of audio file -- First Arugemnt
# getting all files of a particular mask *.mp3 -- second argument
# Standardise the file naming convention and move them to a master repository and file them alpabeticly - third argument
# you need the file from Ned Batchelder, http://nedbatchelder.com/code/modules/id3reader.html -- Thanks Ned !! Notice I named it ID3Reader.py 
# if your on Linux (as i am) it is case sensitive
# I hope you find it usefull, if you improve it ( I know it can be imporoved plenty) please send me acopy of the improved code
# Please ensure tour source and dest dir have the training / ie. mp3sort.py /home/source/ *.mp3 /home/dest/ 
# python mp3sorter.py /home/antonf/Music/Unsorted/ *.mp3 /home/antonf/data/Music/
# Log file is mp3sorter.log
# file with a list of failures is failedfiles.txt
# Added feature to store the data in a MongoDB 
# Version 2


# Import all the modules we need
import fnmatch
import os
import sys 
import ID3Reader
import string
import shutil
import re 
import pymongo
import datetime

# Settings
move = "no"   # Yes or No
failedfiles = "/vol1/failedmusic/"


# ------------------- Database Setup (Mongo) -----------------------
# establish a connection to the database
connection = pymongo.Connection("mongodb://localhost", safe=True)

# get a handle to the Music database
db = connection.music
# Set the collection
collection = db.songs
#-------------- End of Database Setup -------------------

if len(sys.argv) == 3:
    print('no params : useage ||> python mp3sorter.py [source] [mask] [destination]')
    sys.exit(1)

srcdir = sys.argv[1]
mask = sys.argv[2]
dstdir = sys.argv[3]
articles = ['a', 'an', 'of', 'the', 'is']



def writetodb(Artist, Song, Track, Year, location, Album, Genre, NewfIleName):
    # here we will write the data to the database
    # Build a new Insert Statement
    Music = {"title": Song,
             "performer": Artist,
             "album": Album,
             "track": Track,
             "genre":Genre,
             "year": Year,
             "location": location,
             "filename": NewfIleName, 
             "tags": [],
             "comments": [],
             "playlists": [],
             "dateadded": datetime.datetime.utcnow() }

    # now insert the song
    try:
         collection.insert(Music)
         #print "Inserting the song"
    except:
         Writelog( "Error inserting song : "+Music)
         print "Unexpected error:", sys.exc_info()[0]
         Writelog("Unexpected error:"+sys.exc_info()[0])

def RemoveAscii128(tobechecked):
     # Create a string with all single byte characters (only done once)
     nochangetable = str.maketrans('', '')
     # Create a string with the characters you want removed (only done once)
     deletethese = nochangetable[26] + nochangetable[128:]
     # for line in whatever:
     # Strip all the bad characters from line blazingly fast
     tobechecked = tobechecked.translate(nochangetable, deletethese)
     # do stuff with the newly stripped line
     #str.translate 
     #(which is the main worker function here) is doing the same thing as the UNIX tr utility, it's just integrated into Python and coded directly in C. It runs *much* faster than any solution
     #involving hand-coded Python loops, because it processes the whole string at once with no interpreter overhead. In brief tests with timeit, I got a speedup of ~25x versus any of the solutions here.
     # No need for regular expressions, no complicated code. It's been a str builtin forever. In Python 3, the only change is that you'll want to work with bytes, not strs, and the maketrans method is
     # defined directly on the bytes and str classes, not in the string module.
     return tobechecked 

def ensure_dir(mypath):
    # check to see if the directory (mypath) exists, if not create it
    if not os.path.isdir(mypath):
      try:
        os.makedirs(mypath)
        Writelog("Directory created : "+mypath) 
      except:
        Writelog("ERROR - Directory Create failed : "+mypath)
    
     
def Writelog(mlog):
  log.write(mlog+"\n")


def WriteFailedFiles(mfile,  dest,  file):
    f.write(mfile+"\n")
    shutil.move(mfile, dest+file)
  

def CleanFilename(filename):
    Writelog("Dirty Data : "+filename)
    newname = filename.strip(" ")
    newname = newname.replace('&', 'and')
    newname = newname.replace('/', ' ')
    newname = newname.replace('!', ' ')
    newname = newname.replace(',', ' ')
    newname = newname.replace(';', ' ')
    newname = newname.replace('#', ' ')
    newname = newname.replace('$', ' ')
    newname = newname.replace('"', ' ')
    newname = newname.replace('%', ' ')
    newname = newname.replace('^', ' ')
    newname = newname.replace('*', ' ')
    newname = newname.replace('|', ' ')
    newname = newname.replace('{', ' ')
    newname = newname.replace('}', ' ')
    newname = newname.replace('~', ' ')
    newname = newname.replace('<', ' ')
    newname = newname.replace('>', ' ')
    newname = newname.replace('?', ' ')
    newname = newname.replace('@', ' ')
    newname = newname.replace(':', ' ')
    newname = newname.replace('+', ' ')
    newname = newname.replace('=', ' ')
    newname = newname.replace('[', '(')
    newname = newname.replace(']', ')')
    newname = newname.replace('_', ' ')
    Writelog("Clean Data : "+newname)
    return newname

def LocateFile():
    shutil.move(Dir1+file1, Dir2+'/'+file1)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def Alphahead(S):
   x = S[:1]
   if is_number(x):
     return "1"
   else:
     return x.capitalize()
   
def title_except(s, exceptions):
   if (s != None): 
     word_list = re.split(' ', s)       #re.split behaves as expected
     final = [word_list[0].capitalize()]
     for word in word_list[1:]:
       final.append(word in exceptions and word or word.capitalize())
     return " ".join(final)

def main():

  #srcdir = "/home/antonf/Music/Unsorted/"
  print srcdir
  # Declare the counters
  fp = fl = fc = fr = fz = fd = 0
  NewfIleName  = " "
  for file in os.listdir(srcdir):
    if fnmatch.fnmatch(file, mask):
        fp = fp + 1
        Writelog("=======================================================")
        Writelog("Processing : "+file)
        pathfile = srcdir+file
        Writelog("Fill Path of Source : "+pathfile)
        #print pathfile
        # Construct a reader from ( pathfile )
        try: 
            id3r = ID3Reader.Reader(pathfile) 
        except:
            print "Unable to read tag from ", pathfile
            Writelog("Unable to read tag from "+pathfile)
        else:
            # title_except(id3r.getValue('album'), articles)
            Artist = id3r.getValue('performer')
            if ( not Artist is None ) :
                Artist = CleanFilename(Artist)
                Artist = title_except(Artist, articles)
                Writelog("Artist : "+Artist)       # Stored in the Database
            else:
                Writelog("Artist : Not Found")
                Artist = None

            Song = id3r.getValue('title')
            if ( not Song is None ) :
                 Song = CleanFilename(Song)
                 Song = title_except(Song, articles)
                 Writelog("Song Title : "+Song)      # Stored in the Database
            else:
                 Writelog("Song Title : Not Found")
                 Song = None

            Album = id3r.getValue('album')
            if ( not Album is None ) :
                 Album = CleanFilename(Album)
                 Album = title_except(Album, articles)  # Stored in the Database
                 Writelog("Album : "+Album)
            else:
                 Writelog("Album : Not Found")
                 Album = None

            Track = id3r.getValue('track')      # Stored in the Database
            #Track = CleanFilename(Track)
            if not Track is None :
                 if not is_number(Track) or Album is None: 
                      Track = None

            Year = id3r.getValue('year')      # Stored in the Database
            #Year = CleanFilename(Year)
            if not Year is None: 
                 if not is_number(Year) : 
                      Year = None    
          
            Genre = id3r.getValue('genre')
            if not Genre is None:
                  Genre = CleanFilename(Genre)
                  Genre = title_except(Genre, articles)
                  Writelog("Genre : "+Genre)       # Stored in the Database
            else:
                  Writelog("Genre : Not Found")
                  Genre = None

            if (not Artist is None and not Song is None):  # Check that the TAG read was ok
                topdir= Alphahead( Artist )
                location = topdir+"/"+Artist   # Location stored in the Database
                topdir = dstdir+topdir
                Writelog("Top Directory for Song is : "+topdir)
                ensure_dir(topdir)
                artistdir = topdir+"/"+Artist
                Writelog("Artist Diretory is : "+artistdir)
                ensure_dir(artistdir)
                NewfIleName = Artist+" - "+Song+".mp3"  # Create a new filename / Also stored in the Database
            
                FPNewFileName = srcdir+NewfIleName
                Writelog("File to be renamed to  : "+FPNewFileName)
                DstFileName = artistdir+"/"+NewfIleName
                Writelog("New Destination for file is : "+DstFileName)
           
                if (os.path.isfile(FPNewFileName) and pathfile == FPNewFileName) :  # Does the new filename already exsist, is it the same as the Original
                    fc = fc + 1                    
                else: 
                    if pathfile != FPNewFileName: # If not trying to rename file to its same name
                        os.rename(pathfile, FPNewFileName) 
                        Writelog("Renaming file to "+ FPNewFileName)
                        fr = fr + 1

                if os.path.isfile(DstFileName) : # If the file does not already exsist at the destination (No Duplicates)
                      fz = fz + 1
                else:
                      Writelog("Move | "+ FPNewFileName + " to "+ DstFileName)
               
                try :
                     if move == "Yes" :
                         shutil.move(FPNewFileName, DstFileName)
                         writetodb(Artist, Song, Track, Year, location, Album, Genre, NewfIleName)
                         fd = fd +1
                     else:
                         shutil.copyfile(FPNewFileName, DstFileName)
                         writetodb(Artist, Song, Track, Year, location, Album, Genre, NewfIleName)
                         fd = fd +1
                except:
                         Writelog("Move Failed or Write to database failed")
            else:
                Writelog( "ERROR - Failed ID Tag ")
                fl = fl + 1
                WriteFailedFiles(pathfile,  failedfiles,  file)
        if NewfIleName :     
            print "Processed file  # ",fp," | "+file," >> ", NewfIleName
        else:
            print "Processed file  # ",fp," | "+file

  Writelog(  "--------------------------------------------------------------------")
  Writelog(  " Processed Directory   : "+ srcdir+ " for mask : "+  mask)
  Writelog(  " Total Files Processed : "+ str(fp))
  Writelog(  " Total Failed IDs      : "+ str(fl))
  Writelog(  " Total Files Duplicate : "+ str(fc))
  Writelog(  " Total Files Renamed   : "+ str(fr))
  Writelog(  " Total Files Dest-dup  : "+ str(fz))
  Writelog(  " Total Files To Dest   : "+ str(fd))
  Writelog(  "--------------------------------------------------------------------")
      		
  print "--------------------------------------------------------------------"
  print " Processed Directory   : ", srcdir, " for mask : ",  mask
  print " Total Files Processed : ", fp
  print " Total Failed IDs      : ", fl
  print " Total Files Duplicate : ", fc
  print " Total Files Renamed   : ", fr
  print " Total Files Dest-dup  : ", fz
  print " Total Files To Dest   : ", fd
  print "--------------------------------------------------------------------"

  # EOP main()
  
#id3r.getValue('album')
#id3r.getValue('performer')print 
#id3r.getValue('title')
#id3r.getValue('track')
#id3r.getValue('year')


f = open("failedfiles.txt", "w")
log = open("mp3sorter.log", "w")
Writelog("======== Logfile Started ============") 
ensure_dir(dstdir)
print "Searching : ", srcdir, " for : ", mask
main()
f.close()
Writelog("======== Logfile Ended ============") 
log.close()

