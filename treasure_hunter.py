import time
import math
from tresure_hunter_dict import coordsDICT
    
coordstatus = 0
status = 0
lastserial = 0
closest = ""
diff = []
coordsCLOSE1 = 0
coordsCLOSE2 = 0
book = 0
bookname = 0
booktxt = 0
closest = [0]*3
benchlist = []
n = 0
##################################################
######         Importing Dictionary         ######

#import is unable to handle duplicate keys, so we use X,Y,FACET as keys. Im a little confused 
#with how dictionaries work, but these are the values we search for, so I think they are the 
#only keys we need.
#Eventually I would like to have the dictionary as a one-line at the top of the file.
#def csv_to_dict(filename):
#    data = {}
#    with open(filename, 'r', newline='') as file:
#        csv_reader = csv.DictReader(file)
#        for row in csv_reader:
#            key = f"{row['X']},{row['Y']},{row['FACET']}"  #defining the search keys.
#            data[key] = row
#            
#    return data
#
#filename = 'atlaswaypoints.csv'
#coordsDICT = csv_to_dict(filename)
#print(coordsDICT)
##################################################

def findLocation():
    maps = Items.FindAllByID(0x14EC,0x0000,Player.Backpack.Serial,0)
    for map in maps:
        if "completed" in Items.GetPropStringByIndex(map,6):
            continue
        if "X:" in Items.GetPropStringByIndex(map,5):
            a = Items.GetPropStringByIndex(map,5)
            a = a.replace("X:", "")
            a = a.replace(" Y:", "")
            a = a.split(" ")
            a = int(a[0]),int(a[1])
            b = Items.GetPropStringByIndex(map,4)
            b = b.replace("for somewhere in ","")
            return a,b,map
    return 0,0,0
    
def findEmptyMap():
    maps = Items.FindAllByID(0x14EC,0x0000,Player.Backpack.Serial,0)
    for map in maps:
        if "X:" in Items.GetPropStringByIndex(map,5):
            continue
        return map
 
def findTChest():
    tchestFilter = Items.Filter()
    tchestFilter.IsContainer = 1
    tchestFilter.OnGround = 1
    tchestFilter.RangeMax = 1
    tchestFilter.Name = "Treasure Chest"
    tchestList = Items.ApplyFilter(tchestFilter)
    if tchestList:
        return tchestList[0]
    return None

def currentFacet(a):
    facet = a
    if facet in (5,"Valley of Eodon"):
        return "Valley of Eodon",1276
    if facet in (4, "Tokuno Islands"):
        return "Tokuno Islands",1267
    if facet in (3, "Malas"):
        return "Malas",2949
    if facet in (2,"Ilshenar"):
        return "Ilshenar",2055
    if facet in (1, "Trammel"):
        return "Trammel",10
    if facet in (0,"Felucca"):
        return "Felucca",379
  
def findBook(bookname):
    bookFilter = Items.Filter()
    bookFilter.OnGround = 1
    bookFilter.IsContainer = 0
    bookFilter.RangeMax = 50
    bookFilter.Name = "Runic Atlas"
    bookList = Items.ApplyFilter(bookFilter)
    if bookList:
        for book in bookList:
            if bookname in Items.GetPropStringList(book.Serial):
                return book
    return None
    
def findBags(tchest):
    bagsList = Items.FindAllByID(0xA331,0x0000,tchest.Serial,0)
    bagsList = bagsList + Items.FindAllByID(0xA32F,0x0000,tchest.Serial,0)
    bagsList = bagsList + Items.FindAllByID(0xA333,0x0000,tchest.Serial,0)
    if bagsList:
        return bagsList
    return None
    
    
def findLockPick():
    lockpick = Items.FindAllByID(0x14FC,0x0000,Player.Backpack.Serial,0)
    if len(lockpick) > 0:
        return lockpick[0]

def findShovel():
    shovel = Items.FindAllByID(0x0F39,0x0000,Player.Backpack.Serial,0)
    if len(shovel) > 0:
        return shovel[0]
        
def findChestStatus(tchest):
    jlist = Journal.GetJournalEntry(time.time() -5) 
    if tchest.ContainerOpened:
        return 3
    for line in jlist:
        if "That appears to be trapped" in line.Text:
            return 2
    return 1

def findBench(x,y):
    benchFilter = Items.Filter()
    benchFilter.OnGround = 1
    benchFilter.IsContainer = 0
    benchFilter.RangeMax = 50
    benchFilter.Name = "wooden bench"
    benchList = Items.ApplyFilter(benchFilter)
    if benchList:
        benchList2 = []
        for bench in reversed(benchList):
            if bench.Position.X == x and bench.Position.Y == y:
                benchList2.append(bench)
        return benchList2
    return None
    

##################################################
######            In-Game Gump              ######


setX = 25 
setY = 50
 
def sendgump(facet,location,emptymap,closest,diff):
    
    status = [""]*2
    color = [0x555]*5+[0x0000]+[0x555]
    scripts = ["Treasure Hunter","---------------"]
    others = [str(facet),str(location),"Rune: "+str(closest[0])[:-4],"Distance: "+str(diff),"","  Open a Map"]
    sizeY = 50 + (len(scripts)+len(others))*15
    gd = Gumps.CreateGump(movable=True) 
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 150, sizeY, 1579)
    #Gumps.AddAlphaRegion(gd,0, 0, 150, sizeY)
    for i in range(len(scripts)):
        Gumps.AddLabel(gd,25,5+i*20,0x555,scripts[i])
    for i in range(len(others)):
        Gumps.AddLabel(gd,25,5+(i+len(scripts))*20,color[i],others[i])
    Gumps.AddButton(gd, 10, 130, 5831, 5832, 1, 1, 0)
    Gumps.AddButton(gd, 135, 35, 1611, 1611, 2, 1, 0) #Next button
    Gumps.AddButton(gd, -12, 35, 1610, 1610, 3, 1, 0) #Previous button
    #Send Gump#
    Gumps.SendGump(987667, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)
    buttoncheck() 
   
def buttoncheck():
    #couldnt figure out how to do this without globals
    global bookname
    global booktxt
    global closest
    Gumps.WaitForGump(987667, 250) ###### TRY TO KEEP THIS AS THE ONLY PAUSE
                                   ###### SO THAT GUMP IS MORE RESPONSIVE
#    Gumps.CloseGump(987654)
    gd = Gumps.GetGumpData(987667)
    if gd.buttonid == 1: 
        if emptymap:
            Items.UseItem(emptymap)
        else:
            Player.HeadMessage(37,"No more maps!")
    if gd.buttonid == 2:
        print("button pressed")
        if closest[0] == closest[1]:
            if benchlist:
                for bench in benchlist:
                    Items.SetColor(bench.Serial,0x0000)
            if closest[2]:
                bookname = coordsCLOSE2['BOOK']
                booktxt = coordsCLOSE2['TEXT']
                closest[0] = closest[2]
            return
        else:
            for bench in benchlist:
                Items.SetColor(bench.Serial,0x0000)
            bookname = coordsCLOSE1['BOOK']
            booktxt = coordsCLOSE1['TEXT']
            closest[0] = closest[1]
            
##################################################

while True:
    tchest = findTChest()
    lockpick = findLockPick()
    shovel = findShovel()
    location,facet,map = findLocation()
    emptymap = findEmptyMap()
    sendgump(facet,location,emptymap,closest,diff)
    n += 1 #this is a timer to help time certain events
    if n > 100:
        n = 0
    if location == 0 and emptymap and n%10 == 0 and coordstatus == 0:
        Player.HeadMessage(0x55,"Open a map!")
    
    
    if coordstatus == 0 and map: #Run this only once per map (the list is BIG)
        diff = 99999
        diff2 = 99999
        for coords in coordsDICT.keys():
            if coords != ',':
                loclist = coords.split(",")
                newdiff = abs(int(loclist[0])-location[0]) + abs(int(loclist[1])-location[1])
            #Result will be from Shrine book
            if newdiff < diff2 and coordsDICT.get(coords)["FACET"] == facet[:3].lower() and 'Shrines' in coordsDICT.get(coords)["BOOK"]:
                diff2 = newdiff
                closest[2] = coords
                print(closest[2])
            #Result will be from all books. Gets stuck on Islands a lot because they are the closest point.
            if newdiff < diff and coordsDICT.get(coords)["FACET"] == facet[:3].lower():
                diff2 = diff
                diff = newdiff
                closest[1] = coords
        coordstatus = 1
        closest[0] = closest[1]
        coordsCLOSE1 = coordsDICT.get(closest[1])
        coordsCLOSE2 = coordsDICT.get(closest[2])
        bookname = coordsCLOSE1['BOOK']
        booktxt = coordsCLOSE1['TEXT']
        
        
    
    book = findBook(bookname)
    if coordstatus == 1 and book:
        benchlist = findBench(book.Position.X,book.Position.Y)
        if findBook(bookname) and not Gumps.HasGump(0x1f2):
            if n % 2 ==0:
                a = 62
            else:
                a = 32
            for bench in benchlist:
                Items.SetColor(bench.Serial,a)
            if n % 10 == 0:
                Player.HeadMessage(currentFacet(facet)[1],bookname+": "+booktxt)
            if abs(book.Position.X - Player.Position.X) < 3 and abs(book.Position.Y - Player.Position.Y) < 3:
                Items.UseItem(book)
        while Gumps.HasGump(0x1f2): #while book open
            for bench in benchlist:
                Items.SetColor(bench.Serial,0x0000)
            Player.HeadMessage(currentFacet(facet)[1],booktxt)
            if not Gumps.HasGump(0x1f2):
                Misc.Pause(3000)
                break
            Misc.Pause(2500)
    

    if location != 0 and map != 0 and facet == currentFacet(Player.Map)[0]:
        try: #Using try here to help mitigate errors for now.
            if facet == "Tokuno Islands": #Trackingarrow is different in tokuno
                Player.TrackingArrow(location[0]-3,location[1]-3,1,0)
            elif facet == "Ilshenar":
                Player.TrackingArrow(location[0]+8,location[1]+7,1,0)
            else:
                Player.TrackingArrow(location[0],location[1],1,0)
            CUO.GoToMarker(location[0],location[1])
            CUO.FreeView(False)
        except:
            print("Waypoint error")
        
    else:
        Player.TrackingArrow(0,0,0,0)
        
    if tchest and tchest.Serial != lastserial:
        Items.UseItem(tchest)
        lastserial = tchest.Serial
        Misc.Pause(1000)
        status = findChestStatus(tchest)
        
        
    if map and abs(Player.Position.X - location[0]) <3 and abs(Player.Position.Y - location[1]) <3 and status == 0:
        Journal.Clear()
        Items.UseItem(shovel)
        Target.WaitForTarget(5000, False)
        Target.TargetExecute(map.Serial)
        Target.WaitForTarget(5000, False)
        Target.TargetExecute(map.Serial)
        Misc.Pause(2000)
        if tchest:
            if tchest.Position.Z == Player.Position.Z:
                status = 1
        
    while tchest and status == 1:
        Journal.Clear()
        Items.UseItem(lockpick)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(tchest)
        if Journal.WaitJournal("The lock quickly yields to your skill.", 5000):
            status = 2
        Misc.Pause(1000)
        
    while tchest and status == 2:
        Journal.Clear()
        Player.UseSkill("Remove Trap")
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(tchest)
        if Journal.WaitJournal("You successfully disarm the trap!", 5000):
            status = 3
        Misc.Pause(1000)
        
    if tchest and status == 3:
        Items.UseItem(tchest)
        Misc.Pause(1000)
        for bag in findBags(tchest):
            Gumps.SendAction(0xd06eaf, 12)
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(bag)
            for item in range(len(bag.Contains)):
                Misc.Pause(1000)
            Misc.Pause(2000)
        Gumps.SendAction(0xd06eaf, 12)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(tchest)
        for item in range(len(tchest.Contains)):
                Misc.Pause(1000)
        #Reset values to recalculate rune
        status = 0
        coordstatus = 0
    
