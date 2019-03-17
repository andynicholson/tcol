#!/usr/bin/python3

import os
import fnmatch
import random
import datetime
import pickle

# The SOURCE of the video files
dirp="/media/andy/The_Beehive_ACMI/source_files/"

# The DESTINATION of the generated 20mins random videos
output_foldername = "/media/andy/The_Beehive_ACMI/ZANNYBEGG_BEEHIVE/"
#output_foldername = "gentest"

pickle_file = "%s/existing_files.pickle" % output_foldername

###
### BEFORE ROLL OUT
### verify the constraints
### verify how many files to generate per day
###


def walk_Rand(foldername,running_story_index, sub_index):

        randf_str=""
        farray=[]
        outputfile=""
        index = 0
        count=0
        totalbytes=0
        count = 0
        fbytes =0       

        total_size = 1
        
        section_6_CB = False
        section_6_Tyson = False

        #returns a filename, which is a list of randomly chosen video files to merge into one video file
        print("Walking %s " % dirp)

        for r,d,f in os.walk(dirp):
                #avoid the root directory, by skipping the first path
                if count > 0:
                        print("Section:%s , Index = %d\n" % (r, index))
                        options=[]
                        for indf in sorted(f):
                                fbytes=0
                                if fnmatch.fnmatch(indf, '*.mp4'):
                                        #print(indf)    
                                        options.append(indf)
                        print("End Section story index %d, sub index %d " % (running_story_index, sub_index))

                        if index==0:
                            randf=running_story_index

                        if index==1:
                            randf=sub_index

                        if index!=0 and index!=1:
                            randf=random.randrange(0,len(options))


                        if index == 0 and randf == 1:
                            section_6_CB = True

                        if index == 2 and randf == 0:
                            section_6_Tyson = True

                        if index == 5 and section_6_CB == True:
                            randf = 1

                        if index == 5 and (section_6_Tyson == True and section_6_CB == False):
                            randf = 4

                        # Dont use video 1, if index=0 video wasn't also 1
                        if index == 5 and ( (section_6_CB == False and randf == 1) or (section_6_Tyson == False and randf == 4)):
                            while (randf == 1 and section_6_CB == False) or (randf == 4 and section_6_Tyson == False) :
                                print("Rechoosing")
                                randf = random.randrange(0,len(options))

                        absrandf="%s/%s"%(r,options[randf].replace('\'','').strip())
                        print("choosing %d, %s\n" % (randf, absrandf))

                        #store the filename
                        farray.append(absrandf)
                        fbytes=os.path.getsize(absrandf)
                        #store the random number 
                        randf_str+="-%s"%randf

                        index+=1
                        total_size = total_size * len(options)
                        
                count+=1
                totalbytes+=fbytes



        print("total options are %d " % total_size)
        print("total video size is %d. Total GB %d" % (totalbytes , totalbytes/2**30))


        # Calculate TIME
        total_running_time_secs = 0
        for f in farray:
                total_running_time_secs += float(videoDurationInSeconds(f))     

        print("Total running time is %f " % total_running_time_secs)

        LENGTH_IN_SECS = 1200
        if float(total_running_time_secs) > LENGTH_IN_SECS:
                #truncate at LENGTH_IN_SECS
                print ("We have %d seconds to truncate " % (float(total_running_time_secs) - LENGTH_IN_SECS) )

        # We can go ahead.
                
        base_name = "tcol-file%s.txt" % randf_str
        #Put the text file for ffmpeg into a seperate directory
        outputfile="%s/%s"%(foldername,base_name)

        #print("Candidate filename is %s " % outputfile)

        # global array of already existing files, so we dont make a collision
        # 
        existing_files = []
        doesnt_exist = False
        try:
            pickle_file_obj = open(pickle_file,'rb')
            existing_files = pickle.load(pickle_file_obj)
        except FileNotFoundError:
            doesnt_exist = True
            pass
        #print("Existing files is %s " % existing_files)
        if (os.path.isfile(outputfile) or base_name in existing_files):
                pickle_file_obj.close() 
                print("File exists!")   
                return (None,None)
        if doesnt_exist is False:
            pickle_file_obj.close() 


        # Add in filename , so we never re-generate it again.
        #
        pickle_file_obj = open(pickle_file,'wb')
        existing_files.append(base_name)
        pickle.dump(existing_files, pickle_file_obj)
        pickle_file_obj.close() 

        return (outputfile,farray)


def makeRandom(foldername,rsi,subi):

        outputfile = None

        while (outputfile == None):
                outputfile,farray=walk_Rand(foldername, rsi, subi)

        fptr = open(outputfile,"w")
        for strf in farray:
                fptr.write("file '%s'\n"%(strf))                        
        fptr.close()
        return outputfile

def makeVideoFile(tcol_rand_file,outputvideofname):
        os.popen("./concat.sh %s %s" % (tcol_rand_file,outputvideofname)).read()

        #Trunc to 20 mins
        #h,t = os.path.split(outputvideofname)
        #outputvideofname_ = "%s/trunc-%s" % (h,t)
        #os.popen("./trunc.sh %s %s " % ( outputvideofname , outputvideofname_ )).read()

        seconds = videoDurationInSeconds(outputvideofname)
        print(" video duration is %d, minus three minutes is %d" % (float(seconds), float(seconds)-180 ) )

        #os.unlink(outputvideofname)     
        
def videoDurationInSeconds(videofilename):
        cmd = "/usr/bin/ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s " % videofilename
        return os.popen(cmd).read()

def makeDaySchedule(day):

        #make folder name with day
        foldername=day.strftime("%Y%m%d")
        absf = "%s/%s" % (output_foldername, foldername)
        try:
           os.makedirs(absf)
        except FileExistsError:
           pass

        # 3 per hour
        # 8am to 7pm at least == 11 hrs 
        #
        #make 33 video file selections
        #render them

        rsi = 0
        subi = random.randrange(0,6)

        for x in range(24):
                # Get the filename of the text file of pointers to video segments to merge
                newvidlist = makeRandom(absf,rsi, subi)       

                rsi+=1
                subi+=1
                if (rsi > 3):
                        rsi=0   

                if (subi > 5):
                    subi = 0

                # Output filename of merged rendered video
                vidname = "video%02d.mov"%x
                newvidof = "%s/%s" % (absf, vidname)

                # GENERATE THE VIDEO FILE

                makeVideoFile(newvidlist,newvidof)
                
if __name__ == '__main__':
        day_now = datetime.datetime.now()
        #
        # number of days to generate
        #
        for i in range(0,10):
                datex = datetime.timedelta(days=i) + day_now    
                makeDaySchedule(datex)
