#!/usr/bin/python3

import os
import fnmatch
import random
import datetime
import pickle

# The SOURCE of the video files
dirp="/media/andy/Citedesdames_backup1/andy/"

# The DESTINATION of the generated 20mins random videos
output_foldername = "/media/andy/TCOL_daily_log_0/MCA/"
#output_foldername = "gentest"

pickle_file = "%s/existing_files.pickle" % output_foldername

###
### BEFORE ROLL OUT
### verify the constraints
### verify how many files to generate per day
###

def walk_Rand(foldername,running_story_index):

        randf_str=""
        farray=[]
        outputfile=""
        index = 0
        count=0
        totalbytes=0
        count = 0
        fbytes =0       

        total_size = 1

        # Constraints
        dont_run_S03Chloe = False
        dont_run_S07Emma = False
        dont_run_S06Manon_S01Ambrose_S02Chloe = False
        dont_run_S01Ambrose = False

        dont_run_interview_06 = False

        first_interview_choice = 0

        #returns a filename, which is a list of randomly chosen video files to merge into one video file
        #print("Walking %s " % dirp)

        for r,d,f in os.walk(dirp):
                #avoid the root directory, by skipping the first path
                if count > 0:
                        print("Section:%s , Index = %d\n" % (r, index))
                        options=[]
                        for indf in f:
                                fbytes=0
                                if fnmatch.fnmatch(indf, '*.mov'):
                                        #print(indf)    
                                        options.append(indf)
                        #print("End Section")

                        if (index != 4):

                                randf=random.randrange(0,len(options))
                                print("choosing %d from %d options \n" % (randf,len(options)))
                        else:
                                print("SEQ:choosing %d from %d options \n" % (running_story_index,len(options)))
                                randf = running_story_index

                        
                        ## exclusions!
                        if (index == 0 and randf == 3):
                                print("------------------> Got dont run S03Chole\n")
                                dont_run_S03Chloe = True

                        if (index == 1 and (randf == 0 or randf==4)):
                                print("------------------> Got dont run S07Emma\n")
                                dont_run_S07Emma = True

                        if (index == 1 and randf == 3):
                                print("------------------> Got dont run Manon/Ambros/S02Chloe\n")
                                dont_run_S06Manon_S01Ambrose_S02Chloe = True

                        if (index == 3 and randf == 0):
                                print("------------------> Got dont run S01Ambrose\n")
                                dont_run_S01Ambrose = True

                        if (index == 3 and randf == 3):
                                print("------------------> Got dont run S07Emma\n")
                                dont_run_S07Emma = True

                        if (index == 4 and randf == 2):
                                print("------------------> Got dont run interview 06 \n")
                                dont_run_interview_06 = True


                        if index == 4:
                                while ( (dont_run_S07Emma == True and randf == 6) or (dont_run_S03Chloe == True and randf == 2) or (dont_run_S06Manon_S01Ambrose_S02Chloe == True and (randf == 0 or randf == 1 or randf == 5)) or (dont_run_S01Ambrose == True and randf == 0) ):
                                        if randf != 6:
                                            randf = 6
                                        else:
                                            randf=random.randrange(0,len(options))
                                        print("Re-choosing %d\n" % randf)

                        if index == 5:
                                while ( dont_run_interview_06 == True and randf == 5):
                                        randf=random.randrange(0,len(options))
                                        print("Re-choosing %d\n" % randf)
                                #store choice
                                first_interview_choice = randf


                        absrandf="%s/%s"%(r,options[randf])
                        #store the filename
                        farray.append(absrandf)
                        fbytes=os.path.getsize(absrandf)
                        #store the random number 
                        randf_str+="-%s"%randf


                        if index == 5:
                                # add another choice
                                randf=random.randrange(0,len(options))
                                print("Extra choice %d\n" % randf)
                                while ( dont_run_interview_06 == True and randf == 5) or (first_interview_choice == randf):
                                        randf=random.randrange(0,len(options))
                                        print("Re-choosing %d\n" % randf)
                                absrandf="%s/%s"%(r,options[randf])
                                #store the filename
                                farray.append(absrandf)
                                fbytes=os.path.getsize(absrandf)
                                #store the random number 
                                randf_str+="-%s"%randf
                                totalbytes+=fbytes

                                
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

        if float(total_running_time_secs)-180 < 1020:
                # more than 3 minutes out.
                # How much could we add?
                # We need at least 73 seconds from ending...
                could_fill_secs = 1200 - ( float(total_running_time_secs) - 107 )
                        
                print("Too short by %d ! Could add in %d " %  (1200 - float(total_running_time_secs), could_fill_secs) )

                # We could try to find another interview which has running time less than could_fill_secs
                #       


                return (None,None)

        if float(total_running_time_secs)-180 > 1020 and float(total_running_time_secs) - 180 < 1127:   
                #truncate at 20 mins
                print ("We have %d seconds to spare " % (float(total_running_time_secs) - 1200) )

        if float(total_running_time_secs)-180 > 1127:
                # longer than our 1 min 13 seconds (73 seconds) minimum
                print ("We have no seconds to spare ")
                return (None,None)

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


def makeRandom(foldername,rsi):

        outputfile = None

        while (outputfile == None):
                outputfile,farray=walk_Rand(foldername, rsi)

        fptr = open(outputfile,"w")
        for strf in farray:
                fptr.write("file '%s'\n"%(strf))                        
        fptr.close()
        return outputfile

def makeVideoFile(tcol_rand_file,outputvideofname):
        os.popen("./concat.sh %s %s" % (tcol_rand_file,outputvideofname)).read()

        #Trunc to 20 mins
        h,t = os.path.split(outputvideofname)
        outputvideofname_ = "%s/trunc-%s" % (h,t)
        os.popen("./trunc.sh %s %s " % ( outputvideofname , outputvideofname_ )).read()

        seconds = videoDurationInSeconds(outputvideofname)
        print(" video duration is %d, minus three minutes is %d" % (float(seconds), float(seconds)-180 ) )

        os.unlink(outputvideofname)     
        
def videoDurationInSeconds(videofilename):
        cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s " % videofilename
        return os.popen(cmd).read()

def makeDaySchedule(day):

        #make folder name with day
        foldername=day.strftime("%m-%d-%A-%B-%Y")
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

        for x in range(21):
                # Get the filename of the text file of pointers to video segments to merge
                newvidlist = makeRandom(absf,rsi)       
                rsi+=1
                if (rsi > 6):
                        rsi=0   

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
        for i in range(1,15):
                datex = datetime.timedelta(days=i) + day_now    
                makeDaySchedule(datex)
