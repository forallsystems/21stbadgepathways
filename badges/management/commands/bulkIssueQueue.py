from django.core.management.base import NoArgsCommand
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, Context
from django.conf import settings
import csv
from datetime import datetime
from django.core.mail import send_mail
from badges.models import *
from users.models import *

class Command(NoArgsCommand):
    help = ""
    
    def handle_noargs(self, **options):
        
        #See if there is something to process
        for bulk in BulkIssueQueue.objects.filter(deleted=0):
            badgeIdentifierCache = {}
            print settings.MEDIA_ROOT+bulk.file.name
            importReader = csv.reader(open(settings.MEDIA_ROOT+bulk.file.name,"rU"))
            firstRow=True
            i = 0
            
            print "B"
                
            for row in importReader:
                if firstRow:
                    firstRow=False
                    continue
                i+=1
                print i
                studentId = row[0].strip()
                firstName = row[1].strip()
                lastName = row[2].strip()
                email = row[3].strip()
                badgeId = row[4].strip()
                issueDate = row[5].strip()

                
                user = None
               
                user = StudentProfile.find_student(studentId,email,email)
                
                if not user and email!="":
                    print "Making Student"
                    user  = StudentProfile.create_student(email, email, "3A38#**939", firstName, lastName, bulk.organization_id, studentId, None,None)
                
                if user:
                    
                        date_split= issueDate.strip().split("/")
                        if len(date_split) == 3:
                            if date_split[0] < 10:
                                date_split[0] = '0'+date_split[0]
                            if date_split[1] < 10:
                                date_split[1] = '0'+date_split[1]
                                
                            if len(date_split[2])  == 2:
                                date_split[2] = "20"+date_split[2]   
                            issue_date = date_split[0]+"/"+date_split[1]+"/"+date_split[2]
                        else:
                            issue_date = ""
                        badge_id = ''
                        pathwayList = []
                        if badgeId in badgeIdentifierCache:
                            badge_id = badgeIdentifierCache[badgeId]['badge_id']
                            pathwayList = badgeIdentifierCache[badgeId]['pathwayList']
                        else:
                            badge = Badge.get_badge_by_identifier(badgeId)
                            if badge:
                                badge_id = badge.id
                                pathwayList = badge.get_mapped_pathway_list()
                                badgeIdentifierCache[badgeId] = {'badge_id':badge_id,
                                                                'pathwayList':pathwayList}
                        
                        if badge_id:
                            award = Award.create_award(user.id,badge_id)
                            #award.external_id = row[0]
                            if issue_date:
                                award.date_created = datetime.strptime(issue_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                            award.created_by = bulk.created_by
                            award.save()
                            
                            for pathway_id in pathwayList:
                                
                                Pathway.add_user_pathway(user.id, pathway_id)
                            
                            print "."
                        else:
                            print "Badge not found: "+badgeId
                            
            #All DONE
            print "DONE"
         
            send_mail("P2S Badge Issue Complete", "Your request to issue badges has been processed.  Visit www.cnusdp2s.com for more information.", "notice@cnusdp2s.com",
                  [bulk.email], fail_silently=True)
            
            bulk.deleted=1
            bulk.save()
            
                