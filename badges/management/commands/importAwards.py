from django.core.management.base import NoArgsCommand
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, Context
from django.views.generic.simple import direct_to_template
from django.conf import settings
import csv
from datetime import datetime

from badges.models import *
from users.models import *

class Command(NoArgsCommand):
    help = ""
    
    def handle_noargs(self, **options):
        badgeIdentifierCache = {}
        
        importReader = csv.reader(open(settings.MEDIA_ROOT+'files/import/Badges_Badge_Data.csv',"rU"))
        firstRow=True
        i = 0
        
        awardMap = {}
        for a in Award.objects.filter():
            awardMap[str(a.external_id)] = True
            
        #get all users
        userMap = {}
        for sp in StudentProfile.objects.select_related(depth=1):
            userMap[sp.identifier] = sp.user
            
        for row in importReader:
            if firstRow:
                firstRow=False
                continue
            i+=1
            print i
            row[0] = row[0].strip()
            row[1] = row[1].strip()
            row[2] = row[2].strip()
            row[3] = row[3].strip()
            if row[0] in awardMap:
                continue
            
            #if row[2] == 'CN0007':
                #continue
            
            user = None
            if row[1] in userMap:
                user = userMap[row[1]]#StudentProfile.find_student(row[1],'')
            
            if user:
                
                    date_split= row[3].strip().split("/")
                    if date_split[0] < 10:
                        date_split[0] = '0'+date_split[0]
                    if date_split[1] < 10:
                        date_split[1] = '0'+date_split[1]
                    issue_date = date_split[0]+"/"+date_split[1]+"/"+date_split[2]
                    badge_id = ''
                    pathwayList = []
                    if row[2] in badgeIdentifierCache:
                        badge_id = badgeIdentifierCache[row[2]]['badge_id']
                        pathwayList = badgeIdentifierCache[row[2]]['pathwayList']
                    else:
                        badge = Badge.get_badge_by_identifier(row[2])
                        if badge:
                            badge_id = badge.id
                            pathwayList = badge.get_mapped_pathway_list()
                            badgeIdentifierCache[row[2]] = {'badge_id':badge_id,
                                                            'pathwayList':pathwayList}
                    
                    if badge_id:
                        award = Award.create_award(user.id,badge_id)
                        award.external_id = row[0]
                        award.date_created = datetime.strptime(issue_date, '%m/%d/%Y').strftime('%Y-%m-%d')
                        award.save()
                        #print pathwayList
                        #for p in Pathway.get_user_pathways(user.id):
                        #    if p.id in pathwayList:
                        #        pathwayList.remove(p.id)
                                
                        for pathway_id in pathwayList:
                            
                            Pathway.add_user_pathway(user.id, pathway_id)
                        
                        print "."
                    else:
                        print "Badge not found: "+row[2]