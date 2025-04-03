from treasure_hunter_dict import coordsDICT
from System.Collections.Generic import List
from System import Byte
import math

#special thanks:
#omgarturo for combat idea
#Smaptastic for general format of functions
#Avernal for tracking arrow fix
   
bookname = 0
booktxt = 0
coordstatus = 0
coordsCLOSE = [0]*6
closest = [0]*6
diff = [0]*6
lastserial = 0
n = 0 #this is a "timer" for highlighting benches
N = 1 #this is for changing filters

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
        return "Valley of Eodon",340
    if facet in (4, "Tokuno Islands"):
        return "Tokuno Islands",1267
    if facet in (3, "Malas"):
        return "Malas",1902
    if facet in (2,"Ilshenar"):
        return "Ilshenar",1108
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
    if tchest.ContainerOpened:
        return 3
    if Journal.Search("That appears to be trapped"):
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
            else:
                Items.SetColor(bench.Serial,0x0000)
        return benchList2
    return None


    
def filterstate(toggle):
    global closest
    global bookname
    global booktxt
    global coordsCLOSE
    global diff
    global N
    filterName = ["All Runes","2nd Closest","No Islands","Shrines","Towns"]
    #couldnt figure out how to do with without globals, bad practice
    if toggle == 1:
        N += 1
    if toggle == -1:
        N -= 1
    if N == len(closest):
        N = 1
    if N == 0:
        N = 4
    Player.HeadMessage(980,filterName[N-1])
    closest[0] = closest[N]
    diff[0] = diff[N]
    print(coordsCLOSE[N])
    if coordsCLOSE[N] != (False or None):
        bookname = coordsCLOSE[N]['BOOK']
        booktxt = coordsCLOSE[N]['TEXT']
    else:
        Player.HeadMessage(236,"No Runes found for this filter.")
        
def enemyrange(range):
    enemiesInRange = Mobiles.Filter()
    enemiesInRange.Enabled = True
    enemiesInRange.RangeMin = -1
    enemiesInRange.RangeMax = range
    enemiesInRange.Notorieties = List[Byte](bytes([3,4,5,6]))
    enemiesInRange.Friend = False
    enemiesInRange.IsGhost = False
    enemiesInRange.CheckIgnoreObject = True
    enemiesInRange.CheckLineOfSight = True
    enemiesList = Mobiles.ApplyFilter(enemiesInRange)
    if enemiesList:
        return True
    return False
    
##################################################
######            In-Game Gump              ######


setX = 25 
setY = 50
 
def sendgump(facet,location,emptymap,closest,diff):
    
    status = [""]*2
    color = [0]*5+[0x0000]+[0x555]
    scripts = ["Treasure Hunter",""]
    others = [str(facet),str(location),"Rune: "+str(closest[0])[:-4],"Distance: "+str(diff[0])]
    gd = Gumps.CreateGump(movable=True) 
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, 150, 170, 1579)
    Gumps.AddBackground(gd, 5, 30, 140, 10, 50)
    #Gumps.AddAlphaRegion(gd,0, 0, 150, sizeY)
    for i in range(len(scripts)):
        Gumps.AddLabel(gd,25,5+i*20,31,scripts[i])
    for i in range(len(others)):
        Gumps.AddLabel(gd,25,5+(i+len(scripts))*20,color[i],others[i])
    Gumps.AddButton(gd, -5, 130, 1964, 1973, 1, 1, 0)
    Gumps.AddTooltip(gd, r"Open a map")
    Gumps.AddButton(gd, 135, 35, 1611, 1611, 2, 1, 0) #Next button
    Gumps.AddTooltip(gd, r"Next Filter")
    Gumps.AddButton(gd, -12, 35, 1610, 1610, 3, 1, 0) #Previous button
    Gumps.AddTooltip(gd, r"Previous Filter")
    #Send Gump#
    Gumps.SendGump(987667, Player.Serial, setX, setY, gd.gumpDefinition, gd.gumpStrings)
    buttoncheck() 
   
def buttoncheck():
    Gumps.WaitForGump(987667, 1000) ###### TRY TO KEEP THIS AS THE ONLY PAUSE
                                   ###### SO THAT GUMP IS MORE RESPONSIVE
#    Gumps.CloseGump(987667)
    gd = Gumps.GetGumpData(987667)
    if gd.buttonid == 1: 
        if emptymap:
            Items.UseItem(emptymap)
        else:
            Player.HeadMessage(37,"No more maps!")
    if gd.buttonid == 2:
        filterstate(1)
    if gd.buttonid == 3:
        filterstate(-1)
##################################################

while Player.Connected:
    
    status = 0
    tchest = findTChest()
    lockpick = findLockPick()
    shovel = findShovel()
    location,facet,map = findLocation()
    emptymap = findEmptyMap()
    sendgump(facet,location,emptymap,closest,diff)
    n += 1 #this is a timer to help time certain events
    if n > 10:
        n = 1

    
    if location == 0 and emptymap and n == 10 and coordstatus == 0:
        Player.HeadMessage(0x55,"Open a map!")
        
    
    book = findBook(bookname)
    if coordstatus == 1 and book:
        if findBook(bookname) and not Gumps.HasGump(0x1f2):
            a = 2736
            if n & 1:
                a = 2965
            benchlist = findBench(book.Position.X,book.Position.Y)
            for bench in benchlist:
                Items.SetColor(bench.Serial,a)
            if n == 5:
                Player.HeadMessage(currentFacet(facet)[1],bookname+": "+booktxt)
            if abs(book.Position.X - Player.Position.X) < 3 and abs(book.Position.Y - Player.Position.Y) < 3:
                Items.UseItem(book)
            continue
        while Gumps.HasGump(0x1f2): #while book open
            for bench in benchlist:
                Items.SetColor(bench.Serial,0x0000)
            Player.HeadMessage(currentFacet(facet)[1],booktxt)
            for i in range(13):
                Misc.Pause(250)
                if abs(Player.Position.X - location[0]) <200 and abs(Player.Position.Y - location[1]) <200 and facet == currentFacet(Player.Map)[0]:
                    break
            if not Gumps.HasGump(0x1f2):
                Misc.Pause(1000)

    if coordstatus == 0 and map: #Run this only once per map (the list is BIG)
        diff[1] = 99999
        diff[2] = 99999
        diff[3] = 99999
        diff[4] = 99999
        diff[5] = 99999
        for coords in coordsDICT.keys():
            if coords != ',':
                loclist = coords.split(",")
                newdiff = abs(int(loclist[0])-location[0]) + abs(int(loclist[1])-location[1])
            #Result will be from Towns
            townlist = ['Britain', 'Buccaneer', 'Cove', 'Delucia', 'Heartwood', 'Jhelom', 'Minoc', 'Moonglow', 'New Haven', 'New Magincia', 'Nujel', 'Ocllo', 'Papua', 'Royal City', 'Serpent', 'Skara Brae', 'Trinsic', 'Umbra', 'Vesper', 'Wind', 'Yew',
            'Zento']
            townmatch = any(town in coordsDICT.get(coords)["BOOK"] for town in townlist)
            if newdiff < diff[5] and coordsDICT.get(coords)["FACET"] == facet[:3].lower() and townmatch:
                diff[5] = newdiff
                closest[5] = coords
            #Result will be from NOT island book
            if newdiff < diff[4] and coordsDICT.get(coords)["FACET"] == facet[:3].lower() and 'Shrines' in coordsDICT.get(coords)["BOOK"]:
                diff[4] = newdiff
                closest[4] = coords
            #Result will be from Shrine book
            if newdiff < diff[3] and coordsDICT.get(coords)["FACET"] == facet[:3].lower() and not 'Island' in coordsDICT.get(coords)["BOOK"]:
                diff[3] = newdiff
                closest[3] = coords
            #Result will be from all books. Next Closest Rune.
            if newdiff < diff[2] and newdiff > diff[1] and coordsDICT.get(coords)["FACET"] == facet[:3].lower():
                diff[2] = newdiff
                closest[2] = coords
            #Result will be from all books. Gets stuck on Islands a lot because they are the closest point.
            if newdiff < diff[1] and coordsDICT.get(coords)["FACET"] == facet[:3].lower():
                diff[1] = newdiff
                closest[1] = coords
        coordstatus = 1
        closest[0] = closest[1]
        coordsCLOSE[1] = coordsDICT.get(closest[1])
        coordsCLOSE[2] = coordsDICT.get(closest[2])
        coordsCLOSE[3] = coordsDICT.get(closest[3])
        coordsCLOSE[4] = coordsDICT.get(closest[4])
        coordsCLOSE[5] = coordsDICT.get(closest[5])
        diff[0] = diff[1]
        bookname = coordsCLOSE[1]['BOOK']
        booktxt = coordsCLOSE[1]['TEXT']
        
    if location != 0 and map != 0 and facet == currentFacet(Player.Map)[0]:
        try: #Using try here to help mitigate errors for now.
            tileheight = Statics.GetLandZ(location[0], location[1], Player.Map)
            zoffset = round(tileheight / 10)
            X = location[0] - zoffset
            Y = location[1] - zoffset
            Misc.Pause(1000)
            CUO.GoToMarker(location[0], location[1])
            CUO.FreeView(False)
            Player.TrackingArrow(X, Y, True)
        except:
            print("Waypoint error")
        
    else:
        Player.TrackingArrow(0,0,0,0)
    
    if tchest and tchest.Serial != lastserial:  #this will detect chest state if the script was restarted
        Items.UseItem(tchest)
        lastserial = tchest.Serial
        Misc.Pause(1000)
        status = findChestStatus(tchest)
        
        
    if map and abs(Player.Position.X - location[0]) <3 and abs(Player.Position.Y - location[1]) <3 and status == 0 and not enemyrange(2):
        position1 = Player.Position.X + Player.Position.Y
        Journal.Clear()
        Items.UseItem(shovel)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(map.Serial)
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(map.Serial)
        while not enemyrange(1) and Player.Position.X+Player.Position.Y == position1:
            Misc.Pause(1000)
            tchest = findTChest()
            if tchest:
                if abs(tchest.Position.Z - Player.Position.Z) < 4:
                    status = 1
                    Misc.Pause(1000)
                    print("Chest Dug up, status = 1")
                    break
    Journal.Clear()    
    while tchest and status == 1:
        if enemyrange(2):
            Misc.Pause(1000)
            continue
        if findTChest():
            print("starting lockpick")
            Items.UseItem(lockpick)
            Target.WaitForTarget(1000, False)
            Target.TargetExecute(tchest)
            Misc.Pause(1000)
            if Journal.Search('The lock quickly yields to your skill.') == True or Journal.Search('That appears to be trapped') == True:
                status = 2
                print("lock picked, status = "+str(status))
        Misc.Pause(1000)
        
    while tchest and status == 2:
        Journal.Clear()
        Player.UseSkill("Remove Trap")
        Target.WaitForTarget(1000, False)
        Target.TargetExecute(tchest)
        Misc.Pause(1000)
        while not enemyrange(1) and status == 2:
            if Journal.Search('You successfully') == True or Journal.Search('That doesn') == True:
                status = 3
                break
            if Journal.Search('*Your attempt fails') == True or Journal.Search('*You delicately') == False:
                break
            if Journal.Search('That is locked.') == True:
                status = 1
                break
            Misc.Pause(1000)
        Misc.Pause(1000)
        
    if tchest and status == 3:
        Items.UseItem(tchest)
        Misc.Pause(1000)
        if findBags(tchest):
            for bag in findBags(tchest):
                for a in range(0,3):
                    if not Target.HasTarget():
                        Gumps.SendAction(0xd06eaf, 12)
                        Target.WaitForTarget(1000, False)
                        continue
                    if Target.HasTarget():
                        break
                Target.TargetExecute(bag)
                for item in bag.Contains:
                    Misc.Pause(1500)
                Misc.Pause(2000)
        for a in range(0,3):
            if not Target.HasTarget():
                Gumps.SendAction(0xd06eaf, 12)
                Target.WaitForTarget(1000, False)
                continue
            if Target.HasTarget():
                        break
            Target.TargetExecute(tchest)
        #Reset values to recalculate rune
        status = 0
        coordstatus = 0

Gumps.CloseGump(987667)
    
