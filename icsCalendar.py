import psycopg2
import requests
import io
from ics import Calendar
from pprint import pprint
from datetime import datetime, time, date
from dateutil import tz, parser

class Seance:
    name = None
    classGroup = None
    teacher = None
    startTime = None
    endTime = None

url = "https://ade.parisnanterre.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=8241fc3873200214fa9b65393b3db214e0fa50826f0818af6a6aa2a7155eb5caec7f554d6ed7ba1b8a72a25d105159e842f6b661317fa297"
c = Calendar(requests.get(url).text)

#Boucle qui affiche les donnees filtree du fichier .ics
parsing = False
listSeance = []
name = None
classGroup = None
teacher = None
startTime = None
endTime = None
default_tzinfo = tz.gettz("Europe/Paris")
for line in c:
    seance = Seance()
    field, _, data = line.partition(':')
    if field in ('SUMMARY'):
        parsing = True
        name = data.strip()
    if field in ('DESCRIPTION'):
        parsing = True
        value = data.split('\\n')
        for v in value:
            tmp = v.strip()
            if "MIAGE" in tmp:
                classGroup = tmp
            if "Export" not in tmp and "MIAGE" not in tmp and len(tmp)>0:
                teacher = tmp
            
    if field in ('DTSTART'):
        parsing = True
        tmp = parser.parse(data.strip())
        startTime = tmp.replace(tzinfo=tmp.tzinfo).astimezone(tz=None)
    if field in ('DTEND'):
        parsing = True
        if 'VEVENT' not in data and 'VCALENDAR' not in data:
            tmp = parser.parse(data.strip())
            endTime = tmp.replace(tzinfo=tmp.tzinfo).astimezone(tz=None)
    else:
        parsing = False
    if name != None and classGroup != None and startTime != None and endTime != None:
        seance = Seance()
        seance.name = name
        seance.classGroup = classGroup
        seance.startTime = startTime
        seance.endTime = endTime
        if teacher:
            seance.teacher = teacher
        else:
            seance.teacher = "No teacher"
        listSeance.append(seance)
        name = None
        classGroup = None
        teacher = None
        startTime = None
        endTime = None

#print("Seance from ics:")
#for sea in listSeance:
 #   print(" name: " + sea.name + " classGroup: " + sea.classGroup + " teacher: "+ sea.teacher + " startTime: " + sea.startTime.ctime() + " endTime: " + sea.endTime.ctime())
#print("")

#connection à la base postgres    
connection = psycopg2.connect("host='localhost' port=5432 dbname='heimdall_db' user='heimdall' password='heimdall'")
cursor = connection.cursor()
#print("Profs from db")
cursor.execute("SELECT u.id, u.firstname, u.lastname FROM public.user u WHERE u.id in (SELECT id FROM public.teacher)")
profs = cursor.fetchall()
#for row in profs:
    #print("Id: "+ str(row[0]) + " Firstname: " + row[1] + " LastName: "+row[2])
#print("")

#print("")
cursor.execute("SELECT cg.id, cg.name FROM public.class_group cg")
classGroups = cursor.fetchall()
#for row in classGroups:
 #   print("Id: " + str(row[0]) + "Name: " + row[1])
#print("")


today = date.today()
for seance in listSeance:
    if today == seance.startTime.date():
        #print("date: "+seance.startTime.ctime()+" teacher: "+seance.teacher)
        for group in classGroups:
            if group[1] in seance.classGroup:
                #print("group: "+group[1])
                for prof in profs:
                    if prof[1].lower() in seance.teacher.lower() and prof[2].lower() in seance.teacher.lower():
                        #print("prof: "+prof[1])
                        maxIdQuery = "select max(id) from public.lesson"
                        cursor.execute(maxIdQuery)
                        maxId = cursor.fetchone()
                        if type(maxId[0]) is int:
                            id = maxId[0]+1
                        else:
                            id = 1
                        insert = """ INSERT INTO public.lesson (id, class_group_id, teacher_id, date_start, date_end, name) VALUES (%s,%s,%s,%s,%s, %s)"""
                        params = (id, group[0], prof[0], seance.startTime.isoformat(), seance.endTime.isoformat(), seance.name[:50])
                        cursor.execute(insert, params)
                        connection.commit()
                    #else:
                     #   print("else prof")

cursor.close()
connection.close()
