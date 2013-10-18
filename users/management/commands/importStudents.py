from django.core.management.base import NoArgsCommand
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, Context
from organizations.models import *
from users.models import *
from django.views.generic.simple import direct_to_template
from django.conf import settings
import csv
from datetime import datetime

from badges.models import *
from users.models import *

class Command(NoArgsCommand):
    help = ""
    
    def handle_noargs(self, **options):
        schoolCodeMap = {}
        for org in Organization.objects.filter(deleted=0):
            schoolCodeMap[org.organization_id] = org.id
        
        gradeLevelMap = {}
        gradeValue = -2
        for grade in GradeLevel.objects.filter(deleted=0).order_by('sort_order'):
            gradeLevelMap[str(gradeValue)] = grade
            gradeValue+=1
            
        gradeLevelMap["80"] = gradeLevelMap["12"]
        
        importReader = csv.reader(open(settings.MEDIA_ROOT+'files/import/Badges_Student_Data.csv',"rU"))
        
        #get all users
        userMap = {}
        for sp in StudentProfile.objects.select_related(depth=1):
            userMap[sp.identifier] = sp.user
        i=0
        firstRow=True
        for row in importReader:
            if firstRow:
                firstRow=False
                continue
            i+=1
            print i
            #print "."
            #0 - School ID
            #1 - Student ID
            #2 - Grade
            #3 - First Name
            #4 - Last Name
            #5 - Birth Date
            #6 - Username
            #7 - password
            
            if (row[0] != "") and (row[1] != "") and (row[2] != "") and (row[3] != "") and (row[4] != "") and (row[5] != "") and (row[6] != "") and (row[7] != ""):
                #try:
                    existing_user = None
                    if row[1] in userMap:
                        existing_user = userMap[row[1]]
                    #existing_user = StudentProfile.find_student(student_id=row[1],username=row[6])
                    
                    date_split= row[5].strip().split("/")
                    if date_split[0] < 10:
                        date_split[0] = '0'+date_split[0]
                    if date_split[1] < 10:
                        date_split[1] = '0'+date_split[1]
                    if len(date_split[2]) == 2:
                        yearEnd = int(date_split[2])
                        if yearEnd > 15:
                            date_split[2] = '19'+date_split[2]
                        else:
                            date_split[2] = '20'+date_split[2]
                    birth_date = date_split[0]+"/"+date_split[1]+"/"+date_split[2]
                    
                    if row[2].strip() not in gradeLevelMap:
                        print "Grade not found"
                        continue
                        
                    if not existing_user:
                        print "new"
                        StudentProfile.create_student(row[6].strip(),
                                      '',
                                      row[7].strip(),
                                      row[3].strip(),
                                      row[4].strip(),
                                      schoolCodeMap[row[0].strip()],
                                      row[1].strip(),
                                      gradeLevelMap[row[2].strip()],
                                      datetime.strptime(birth_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                                      )
                        #print "new student"
                    else:
                        #print "existing user found"
                        #continue
                        print "existing"
                        existing_user.get_profile().get_student_profile().update_student(row[6].strip(),
                                      '',
                                      row[7].strip(),
                                      row[3].strip(),
                                      row[4].strip(),
                                      schoolCodeMap[row[0].strip()],
                                      row[1].strip(),
                                      gradeLevelMap[row[2].strip()],
                                      datetime.strptime(birth_date, '%m/%d/%Y').strftime('%Y-%m-%d'))
            else:
                print "Skipping row"
        