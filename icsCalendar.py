from ics import Calendar
import requests
import io

class Seance:
    name = None
    classGroup = None
    teacher = None
    startTime = None
    endTime = None

url = "https://ade.parisnanterre.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=8241fc3873200214ee9811c8ff4751dfbd72d825015315fefd3463ac7f4bdbd3f377b612dec2c5fba5147d40716acb137447844b505a2e3c"
c = Calendar(requests.get(url).text)

#print(c)
#c.events

#Boucle qui affiche les donnee du fichier .ics
#i=0
#for e in c:
#    e = list(c.timeline)[i] 
#    "Event '{}' started {}".format(e.name, e.begin.humanize())
#    print (e)
#    print("\n")
#    i=i+1

#Boucle qui affiche les donnees filtree du fichier .ics
parsing = False
listSeance = []
name = None
classGroup = None
teacher = None
startTime = None
endTime = None
for line in c:
    seance = Seance()
    field, _, data = line.partition(':')
    if field in ('SUMMARY'):
        parsing = True
        name = data
    if field in ('DESCRIPTION'):
        parsing = True
        value = data.split('\\n')
        for v in value:
            if "MIAGE" in v:
                classGroup = v
            if "Export" not in v and "MIAGE" not in v and not v:
                teacher = v
    if field in ('DTSTART'):
        parsing = True
        startTime = data
    if field in ('DTEND'):
        parsing = True
        if data != 'VEVENT':
            endTime = data
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


for sea in listSeance:
    print("name:"+ sea.name)
    print("classGroup:"+ sea.classGroup)
    print("teacher:"+ sea.teacher)
    print("startTime:"+ sea.startTime)
    print("endTime:"+ sea.endTime)
    
