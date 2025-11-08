import API
import math
import configparser 
from pathlib import Path
from treasure_hunter_dict import coordsDICT


# Toggle debug output
DEBUG = False

#special thanks:
#omgarturo for combat idea
#Smaptastic for general format of functions AND ideas for more complex settings
#Avernal for tracking arrow fix

book = None
bookname = 0
booktxt = 0
coordstatus = 0
coordsCLOSE = [0]*6
closest = [0]*6
diff = [0]*6
lastserial = 0
n = 0 #this is a "timer" for highlighting benches
N = 1 #this is for changing filters

##################################################
######            Import Settings           ######
##################################################

SETTINGS_FILE = "TreasureHunter.ini"
SECTION = "Settings"

DEFAULTS = {
    "gumpX": "0",
    "gumpY": "0",
    "use_lootmaster": "False",
    "loot_gold": "False",
    "loot_insanetokens": "False",
    "gold1x1": "False",
    "use_bagofsending": "False"
}

config = configparser.ConfigParser()

# Seed file/section with defaults if missing
config.read(SETTINGS_FILE)
if SECTION not in config:
    config[SECTION] = DEFAULTS
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        config.write(f)

# Read values (typed)
gumpX = config.getint(SECTION, "gumpX", fallback=0)
gumpY = config.getint(SECTION, "gumpY", fallback=0)
use_lootmaster = config.getboolean(SECTION, "use_lootmaster", fallback=False)
loot_gold = config.getboolean(SECTION, "loot_gold", fallback=False)
loot_insanetokens = config.getboolean(SECTION, "loot_insanetokens", fallback=False)
gold1x1 = config.getboolean(SECTION, "gold1x1", fallback=False)
use_bagofsending = config.getboolean(SECTION, "use_bagofsending", fallback=False)

##################################################

def save():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        config.write(f)

def findLocation():
    maps = API.FindTypeAll(0x14EC, API.Backpack)
    a,b = None,None
    for map_item in maps:
        itemprops = API.ItemNameAndProps(map_item, True).splitlines() # It is slower to call this a bunch of times. 
        if any("Completed" in s for s in itemprops): #This is how you check for Completed in any of the lines
             continue
        if all("X:" not in s for s in itemprops): #This is how you check for no X: in all the lines
            continue
        for line in itemprops:
            if "X:" in line or "Y:" in line:
                a = tuple(line.replace("X:", "").replace(" Y:", "").split(" "))
                a = int(a[0]),int(a[1])
            if "For Somewhere In " in line:
                b = line.replace("For Somewhere In ","")
                if b == "Eodon":
                    b = "Ter Mur"
        return a,b,map_item
    return None,None,None

def findEmptyMap():
    maps = API.FindTypeAll(0x14EC, API.Backpack)
    for map in maps:
        if "X:" in API.ItemNameAndProps(map):
            continue
        return map

def findTChest():
    if DEBUG: API.SysMsg("Searching for Treasure Chest...")
    tchestList = (API.FindTypeAll(0xA304)+
                       API.FindTypeAll(0xA305)+
                       API.FindTypeAll(0xA306)+
                       API.FindTypeAll(0xA307)+
                       API.FindTypeAll(0xA308)+
                       API.FindTypeAll(0xA309)+
                       API.FindTypeAll(0xA30A)+
                       API.FindTypeAll(0xA30B))
    if DEBUG: API.SysMsg(f"Found {len(tchestList)} chests.")
    for chest in tchestList:
        if "Treasure Chest" not in API.ItemNameAndProps(chest):
            tchestList = [chest for chest in tchestList if API.ItemNameAndProps(chest) == "Treasure Chest"]  # Remove any chest that does not have the name "Treasure Chest"  

    if tchestList:
        return tchestList[0]
    return None

def currentFacet(facet):
    if facet in (5,"Valley of Eodon","Ter Mur"):
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
    
def facettoint(facet):
    if facet in ("Valley of Eodon","Ter Mur",1276,5):
        return 5
    if facet in ("Tokuno Islands",1267,4):
        return 4
    if facet in ("Malas",2949,3):
        return 3
    if facet in ("Ilshenar",2055,2):
        return 2
    if facet in ("Trammel",10,1):
        return 1
    if facet in ("Felucca",379,0):
        return 0
    
def findBook(bookname):
    if bookname == 0:
        return None
    bookname = bookname.title()
    if DEBUG: API.SysMsg(f"Searching for book: {bookname}")
    bookList = (API.FindTypeAll(0X9C16) 
                + API.FindTypeAll(0X9C17))  # Adding the new book type 0x39959
                                            #39959
    if DEBUG: API.SysMsg(f"Found {len(bookList)} books.")
    if bookList:
        for book in bookList:
            for line in API.ItemNameAndProps(book).splitlines():
                if bookname == line:
                    return book
    return None

def findBags(tchest):
    bagsList = []
    if API.FindType(0xA331,tchest.Serial) != None:
        bagsList.append(API.FindType(0xA331,tchest.Serial))
    if API.FindType(0xA32F,tchest.Serial) != None:
        bagsList.append(API.FindType(0xA32F,tchest.Serial))
    if API.FindType(0xA333,tchest.Serial) != None:
        bagsList.append(API.FindType(0xA333,tchest.Serial))
    if bagsList:
        return bagsList
    return None

def findLockPick():
    lockpick = API.FindTypeAll(0x14FC,API.Backpack)
    if len(lockpick) > 0:
        return lockpick[0]

def findShovel():
    shovel = API.FindTypeAll(0x0F39,API.Backpack)
    if len(shovel) > 0:
        return shovel[0]

def findChestStatus(tchest):
    if API.InJournal("That appears to be trapped"):
        return 2
    if API.Contents(tchest.Serial) == 0: #Chest is locked OR empty
        return 1
    return 3

def findBench(x,y):
    benchList = (API.FindTypeAll(0x0B2C) #wooden bench
        + API.FindTypeAll(0x0B2D) #wooden bench
        + API.FindTypeAll(0x0B35) #table hue 1194
    )

    if benchList:
        benchList2 = []
        for bench in benchList:
            
            if bench.X == x and bench.Y == y:
                benchList2.append(bench)
            if bench.Graphic == 0x0B2C or bench.Graphic == 0x0B2D:
                bench.SetHue(0x0000) # Set the hue to 0
            if bench.Graphic == 0x0B35:
                bench.SetHue(0x04AA) # Set the hue to 1194
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
        if N < len(filterName)+1:
            N += 1
        if N == len(filterName)+1:
            N = 1
    if toggle == -1:
        if N > 0:
            N -= 1
        if N == 0:
            N = len(filterName)
    API.HeadMsg(filterName[N-1],API.Player)
    closest[0] = closest[N]
    diff[0] = diff[N]
    if coordsCLOSE[N] != None:
        bookname = coordsCLOSE[N]['BOOK']
        if DEBUG: API.SysMsg(f"Bookname set to: {bookname}")
        booktxt = coordsCLOSE[N]['TEXT']
    else:
        API.HeadMsg("No Runes found for this filter.",API.Player)
    return filterName[N-1]
    
def enemyrange(range):
    enemiesList = API.NearestMobiles([API.Notoriety.Enemy, API.Notoriety.Gray, API.Notoriety.Criminal], range)
    # enemiesInRange = Mobiles.Filter()
    # enemiesInRange.Enabled = True
    # enemiesInRange.RangeMin = -1
    # enemiesInRange.RangeMax = range
    # enemiesInRange.Notorieties = List[Byte](bytes([3,4,5,6]))
    # enemiesInRange.Friend = False
    # enemiesInRange.IsGhost = False
    # enemiesInRange.CheckIgnoreObject = True
    # enemiesInRange.CheckLineOfSight = True
    # enemiesList = Mobiles.ApplyFilter(enemiesInRange)
    if enemiesList:
        return True
    return False


##################################################
######            In-Game Gump              ######
##################################################
w = 150
h = 200

gump = API.CreateGump(True, True)
gump.SetRect(gumpX, gumpY, w, h)

# Background
bg = API.CreateGumpColorBox(1, "#b19577")
bg.SetWidth(w)
bg.SetHeight(h)
gump.Add(bg)

# Labels
title = API.CreateGumpLabel("Treasure Hunter", 0)
title.SetX(25)
title.SetY(0)
gump.Add(title)

title = API.CreateGumpLabel("Zone", 0)
title.SetX(10)
title.SetY(30)
gump.Add(title)

zone = API.CreateGumpLabel("", 0) #Zone
zone.SetX(50)
zone.SetY(30)
gump.Add(zone)

title = API.CreateGumpLabel("Map XY", 0)
title.SetX(10)
title.SetY(50)
gump.Add(title)

mapcoords = API.CreateGumpLabel("", 0) #Map Coords
mapcoords.SetX(65)
mapcoords.SetY(50)
gump.Add(mapcoords)

title = API.CreateGumpLabel("Rune XY", 0)
title.SetX(10)
title.SetY(70)
gump.Add(title)

runecoords = API.CreateGumpLabel("", 0) #Rune Coords
runecoords.SetX(65)
runecoords.SetY(70)
gump.Add(runecoords)

title = API.CreateGumpLabel("Distance", 0)
title.SetX(10)
title.SetY(90)
gump.Add(title)

distance = API.CreateGumpLabel("", 0) #DISTANCE
distance.SetX(70)
distance.SetY(90)
gump.Add(distance)

title = API.CreateGumpLabel("Rune Filter", 0)
title.SetX(35)
title.SetY(110)
gump.Add(title)

runefilter = API.CreateGumpLabel("All Runes", 0) #Rune Filter
runefilter.SetX(35)
runefilter.SetY(130)
gump.Add(runefilter)

# Buttons
button1 = API.CreateGumpButton("",0,9903,9905,9904)
button1.SetX(129)
button1.SetY(130)
gump.Add(button1)

button2 = API.CreateGumpButton("",0,9909,9911,9910)
button2.SetY(130)
gump.Add(button2)

button3 = API.CreateGumpButton("Open Map",0,40298,40298,40297)
button3.SetY(170)
button3.SetWidth(80)
gump.Add(button3)

button4 = API.CreateGumpButton("O",0,40298,40298,40297)
button4.SetY(5)
button4.SetX(5)
button4.SetWidth(15)
gump.Add(button4)
# Assign buttons as attributes

# Borders
frameColor = "#5D3C16"
for x, y, w, h in [
    (-5, -5, w+10, 5), #top
    (-5, h, w+10, 5),  #bottom
    (-5, -5, 5, h+10), #left
    (w, -5, 5, h+10),     #right
]:
    border = API.CreateGumpColorBox(1, frameColor)
    border.SetX(x)
    border.SetY(y)
    border.SetWidth(w)
    border.SetHeight(h)
    gump.Add(border)

API.AddGump(gump) # Add the gump to the game
##################################################
######            Options Gump              ######
##################################################
gumpoptions = API.CreateGump(True, True)
w=500
h=500
gumpoptions.SetRect( 0, 0, w, h)
gumpoptions.CenterXInViewPort()
gumpoptions.CenterYInViewPort()
gumpoptions.IsVisible = False
gumpoptions.CanCloseWithRightClick = False

#background
bg = API.CreateGumpColorBox(1, "#b19577")
bg.SetWidth(w)
bg.SetHeight(h)
gumpoptions.Add(bg)

#borders
frameColor = "#5D3C16"
for x, y, w, h in [
    (-5, -5, w+10, 5), #top
    (-5, h, w+10, 5),  #bottom
    (-5, -5, 5, h+10), #left
    (w, -5, 5, h+10),     #right
]:
    border = API.CreateGumpColorBox(1, frameColor)
    border.SetX(x)
    border.SetY(y)
    border.SetWidth(w)
    border.SetHeight(h)
    gumpoptions.Add(border)

# Labels
title = API.CreateGumpLabel("Options", 0)
title.SetX(200)
title.SetY(0)
gumpoptions.Add(title)

rb1 = API.CreateGumpRadioButton("Use Lootmaster", 1, isChecked = use_lootmaster)
rb1.SetX(10)
rb1.SetY(30)
gumpoptions.Add(rb1)

rb2 = API.CreateGumpRadioButton("Loot Gold", 1, isChecked = loot_gold)
rb2.SetX(10)
rb2.SetY(50)
gumpoptions.Add(rb2)

rb3 = API.CreateGumpRadioButton("Loot Insane Tokens", 2, isChecked = loot_insanetokens)
rb3.SetX(10)
rb3.SetY(70)
gumpoptions.Add(rb3)

rb4 = API.CreateGumpRadioButton("gold1x1", 3, isChecked = gold1x1)
rb4.SetX(10)
rb4.SetY(90)
gumpoptions.Add(rb4)

rb5 = API.CreateGumpRadioButton("use_bagofsending", 4, isChecked = use_bagofsending)
rb5.SetX(10)
rb5.SetY(110)
gumpoptions.Add(rb5)

API.AddGump(gumpoptions) # Add the gump to the game

##################################################
######            Compass Gump              ######
##################################################
gump1 = API.CreateGump(False, False, False)
gump1.Add(API.CreateGumpLabel("center"))
gump1.CenterXInViewPort()
gump1.CenterYInViewPort()
API.AddGump(gump1)

X = gump1.GetX()
Y = gump1.GetY()

gump2 = API.CreateGump(False, False, False) #UP RIGHT (NORTH)
gump2.Add(API.CreateGumpPic(0x1195))
gump2.SetX(X + 37)
gump2.SetY(Y - 130)
gump2.CanCloseWithRightClick = False
API.AddGump(gump2)

gump3 = API.CreateGump(False, False, False) #RIGHT
gump3.Add(API.CreateGumpPic(0x1196))
gump3.SetX(X + 88)
gump3.SetY(Y - 70)
gump3.CanCloseWithRightClick = False
API.AddGump(gump3)

gump4 = API.CreateGump(False, False, False) #DOWN RIGHT
gump4.Add(API.CreateGumpPic(0x1197))
gump4.SetX(X + 36)
gump4.SetY(Y - 8)
gump4.CanCloseWithRightClick = False
API.AddGump(gump4)

gump5 = API.CreateGump(False, False, False) #DOWN
gump5.Add(API.CreateGumpPic(0x1198))
gump5.SetX(X - 25)
gump5.SetY(Y + 45)
gump5.CanCloseWithRightClick = False
API.AddGump(gump5)

gump6 = API.CreateGump(False, False, False) #DOWN LEFT
gump6.Add(API.CreateGumpPic(0x1199))
gump6.SetX(X - 84)
gump6.SetY(Y - 6)
gump6.CanCloseWithRightClick = False
API.AddGump(gump6)

gump7 = API.CreateGump(False, False, False) #LEFT
gump7.Add(API.CreateGumpPic(0x119A))
gump7.SetX(X - 135)
gump7.SetY(Y - 70)
gump7.CanCloseWithRightClick = False
API.AddGump(gump7)

gump8 = API.CreateGump(False, False, False) #UP LEFT
gump8.Add(API.CreateGumpPic(0x119B))
gump8.SetX(X - 86)
gump8.SetY(Y - 132)
gump8.CanCloseWithRightClick = False
API.AddGump(gump8)

gump9 = API.CreateGump(False, False, False) #UP
gump9.Add(API.CreateGumpPic(0x1194))
gump9.SetX(X - 24)
gump9.SetY(Y - 183)
gump9.CanCloseWithRightClick = False
API.AddGump(gump9)

# Matches gump numbering/names in compass.py
DIRECTION_ORDER = [
    'center',     # gump1
    'up_right',   # gump2 North
    'right',      # gump3
    'down_right', # gump4
    'down',       # gump5
    'down_left',  # gump6
    'left',       # gump7
    'up_left',    # gump8
    'up',         # gump9  
]

def _angle_to_octant(angle_deg):
    # angle_deg: 0 = right/east, 90 = up/north (we use atan2(-dy,dx) below)
    # octants centered on: 0,45,90,135,180,225,270,315
    sector = int(((angle_deg + 22.5) % 360) // 45)
    # Map sector index to direction name (starting at east/right)
    mapping = ['down_right', 'right', 'up_right', 'up', 'up_left', 'left', 'down_left', 'down']
    return mapping[sector]

def direction_and_distance(cx, cy, tx, ty, center_threshold):
    """
    Compute discrete 8-way direction (strings matching DIRECTION_ORDER) from center (cx,cy)
    towards target (tx,ty), plus distance.

    - uses euclidean distance
    """
    if cx is None or cy is None or tx is None or ty is None:
        return None, None
    dx = tx - cx
    dy = ty - cy
    # For screen coordinates where y increases downward we invert dy when computing angle
    angle = math.degrees(math.atan2(-dy, dx)) % 360
    dist = math.hypot(dx, dy)

    if dist <= center_threshold:
        return 'center', dist

    dir_name = _angle_to_octant(angle)
    return dir_name, dist

def compass_update(x,y): # This loop will need to be setup somewhere else
    gumps = [gump1, gump2, gump3, gump4, gump5, gump6, gump7, gump8, gump9]
    direction, distance = direction_and_distance(API.Player.X, API.Player.Y, x, y, center_threshold=0)
    if x == None and y == None:
        for i in range(len(gumps)):
            if direction == DIRECTION_ORDER[i]:
                gumps[i].IsVisible = False

    for i in range(len(gumps)):
        if direction == DIRECTION_ORDER[i]:
            gumps[i].IsVisible = True
        else:
            gumps[i].IsVisible = False
compass_update(None,None) # Initialize compass to hide all arrows

#################################################

while not gump.IsDisposed: #Stop the script if the gump is closed
    if DEBUG: API.SysMsg("[DEBUG] Loop Start")
    config[SECTION]["gumpX"] = str(gump.GetX())
    config[SECTION]["gumpY"] = str(gump.GetY())
    # While recreating the script, I want to be able to
    # access the menu while the script is running. This
    # will allow me to do things like resetting the gump,
    # changing the filter, cancelling map if it is bugged.

    # Also, I would like to have an options menu that
    # will have options like loot settings, map settings,
    # and enabling of other features.
    API.Pause(0.1)
    API.ProcessCallbacks()



    if button1.HasBeenClicked() == True: #Filter Right Button
        if DEBUG: API.SysMsg("[DEBUG] Button1 Clicked")
        API.SysMsg("Next Filter")
        runefilter.Text = str(filterstate(1))
        book = findBook(bookname)
    if button2.HasBeenClicked() == True: #Filter Left Button
        if DEBUG: API.SysMsg("[DEBUG] Button2 Clicked")
        API.SysMsg("Previous Filter")
        runefilter.Text = str(filterstate(-1))
        book = findBook(bookname)
    if button3.HasBeenClicked() == True: #Open Map Button
        if DEBUG: API.SysMsg("[DEBUG] Button3 Clicked")
        API.SysMsg("Opening Map...")
        map = findEmptyMap()
        if map:
            API.UseObject(map)
        else:
            API.SysMsg("No empty map found in backpack.")
    if button4.HasBeenClicked() == True: #Open Options Button
        if DEBUG: API.SysMsg("[DEBUG] Button4 Clicked")
        API.SysMsg("Opening Options...")
        gumpoptions.IsVisible = not gumpoptions.IsVisible
    if rb1.IsChecked != use_lootmaster:
        use_lootmaster = rb1.IsChecked
        if rb1.IsChecked:
            rb3.IsChecked = False
            rb4.IsChecked = False
            rb5.IsChecked = False
        config[SECTION]["use_lootmaster"] = str(use_lootmaster)
        save()
    if rb2.IsChecked != loot_gold:
        loot_gold = rb2.IsChecked
        # if rb2.IsChecked:
        #     rb1.IsChecked = False
        config[SECTION]["loot_gold"] = str(loot_gold)
        save()
    if rb3.IsChecked != loot_insanetokens:
        loot_insanetokens = rb3.IsChecked
        # if rb3.IsChecked:
        #     rb1.IsChecked = False
        config[SECTION]["loot_insanetokens"] = str(loot_insanetokens)
        save()
    if rb4.IsChecked != gold1x1:
        gold1x1 = rb4.IsChecked
        # if rb3.IsChecked:
        #     rb1.IsChecked = False
        config[SECTION]["gold1x1"] = str(gold1x1)
        save()
    if rb5.IsChecked != use_bagofsending:
        use_bagofsending = rb5.IsChecked
        # if rb3.IsChecked:
        #     rb1.IsChecked = False
        config[SECTION]["use_bagofsending"] = str(use_bagofsending)
        save()
    

    status = 0
    if DEBUG: API.SysMsg("[DEBUG] Status Reset")
    tchest = findTChest()
    if DEBUG: API.SysMsg(f"[DEBUG] tchest: {tchest}")
    lockpick = findLockPick()
    if DEBUG: API.SysMsg(f"[DEBUG] lockpick: {lockpick}")
    shovel = findShovel()
    if DEBUG: API.SysMsg(f"[DEBUG] shovel: {shovel}")
    location,facet,map = findLocation()
    if DEBUG: API.SysMsg(f"[DEBUG] location: {location}, facet: {facet}, map: {map}")
    emptymap = findEmptyMap()
    if DEBUG: API.SysMsg(f"[DEBUG] emptymap: {emptymap}")

    n += 1 #this is a timer to help time certain events
    if DEBUG: API.SysMsg(f"[DEBUG] n: {n}")
    if n > 50:
        n = 1


    if location == None and map == None and coordstatus == 0 and tchest == None: #No map open, no coords found, no chest found: #First state. Used when starting
        #if location == None and map == None and coordstatus == 0 and tchest == None: #No map open, no coords found, no chest found
        try:
            if DEBUG: API.SysMsg("[DEBUG] Prompting to open a map")
            if tchest:
                status = 6
            if map:
                status = 1
            if n == 10:
                if emptymap != None:
                    API.HeadMsg("Open a map!", API.Player, 33)
                if emptymap == None:
                    API.HeadMsg("No empty map found!", API.Player, 33)
            continue
        except:
            API.SysMsg("Error encountered in state 0, restarting.", 33)
            API.HeadMsg("Error encountered in state 0, restarting.", API.Player, 33)
            status == None

    ##state = 1
    if coordstatus == 0 and location != None and map != None: #Run this only once per map (the list is BIG)
        try:
            #if coordstatus == 0 and location != None and map != None: #Run this only once per map (the list is BIG)
            if DEBUG: API.SysMsg("[DEBUG] Calculating closest runes")
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
            if DEBUG: API.SysMsg(f"Closest rune: {coordsCLOSE[1]}")
            coordsCLOSE[2] = coordsDICT.get(closest[2])
            if DEBUG: API.SysMsg(f"2nd Closest rune: {coordsCLOSE[2]}")
            coordsCLOSE[3] = coordsDICT.get(closest[3])
            if DEBUG: API.SysMsg(f"Closest non-island rune: {coordsCLOSE[3]}")
            coordsCLOSE[4] = coordsDICT.get(closest[4])
            if DEBUG: API.SysMsg(f"Closest shrine rune: {coordsCLOSE[4]}")
            coordsCLOSE[5] = coordsDICT.get(closest[5])
            if DEBUG: API.SysMsg(f"Closest town rune: {coordsCLOSE[5]}")
            diff[0] = diff[1]
            bookname = coordsCLOSE[1]['BOOK']
            if DEBUG: API.SysMsg(f"Bookname set to: {bookname}")
            booktxt = coordsCLOSE[1]['TEXT']
            book = findBook(bookname)
        
            zone.Text = str(facet)
            if DEBUG: API.SysMsg(f"[DEBUG] zone.Text: {zone.Text}")
            mapcoords.Text = (str(location[0]) + "," + str(location[1]))
            if DEBUG: API.SysMsg(f"[DEBUG] mapcoords.Text: {mapcoords.Text}")
            runecoords.Text = str(closest[0])[:-4]
            if DEBUG: API.SysMsg(f"[DEBUG] runecoords.Text: {runecoords.Text}")
            distance.Text = str(diff[0])
            if DEBUG: API.SysMsg(f"[DEBUG] distance.Text: {distance.Text}")
            status = 1
        except:
            API.SysMsg("Error encountered in state 1, restarting.", 33)
            API.HeadMsg("Error encountered in state 1, restarting.", API.Player, 33)
            status = None
    
    # STATE 2 Map opened, Coords calculated, now waiting to find book in CRL
    if coordstatus == 1 and not book:
        if n == 10:
            API.SysMsg("Book not found, go to [CRL.",33)
        book = findBook(bookname)
    # STATE 3
    if coordstatus == 1 and book:
        if DEBUG: API.SysMsg("[DEBUG] coordstatus==1 and book found")
        if bookname and not API.HasGump(0x1f2):
            a = 1177
            if n & 1:
                a = 1170
            benchlist = findBench(book.X,book.Y)
            if benchlist:
                for bench in benchlist:
                    bench.SetHue(a)
                if n == 5:
                    API.HeadMsg(bookname+": "+booktxt,API.Player)
                if abs(book.X - API.Player.X) < 3 and abs(book.Y - API.Player.Y) < 3:
                    API.UseObject(book)
                continue
        while API.HasGump(0x1f2): #while book open
            for bench in benchlist:
                if bench.Graphic == 0x0B2C or 0x0B2D: 
                    bench.SetHue(0x0000) # Set bench hue to 0
                if bench.Graphic == 0x0B35:
                    bench.SetHue(0x04AA) # Set table hue to 1194
            API.HeadMsg(booktxt,API.Player)
            for i in range(30):
                API.Pause(.25)
                if abs(API.Player.X - location[0]) <200 and abs(API.Player.Y - location[1]) <200 and currentFacet(facet)[1] == currentFacet(API.GetMap())[1]:
                        coordstatus = 2
                        break
            if not API.HasGump(0x1f2):
                API.Pause(1)
    #STATE 4
    if location != None and map != None and currentFacet(facet)[1] == currentFacet(API.GetMap())[1]:
        if DEBUG: API.SysMsg("[DEBUG] About to calculate tileheight and tracking arrow")
        try: 
            #tileheight = API.GetTile(location[0], location[1]).Z This is not needed in TazUO
            #zoffset = round(tileheight / 10)
            #X = location[0] - zoffset
            #Y = location[1] - zoffset
            #if DEBUG: API.SysMsg(f"Map X:{location[0]} Y:{location[1]} Z:{tileheight} -> Tracking X:{X} Y:{Y} Zoffset:{zoffset}")
            compass_update(location[0], location[1])
            API.RemoveMapMarker('Treasure')
            API.AddMapMarker('Treasure', location[0], location[1], facettoint(facet), color="yellow")
            API.RemoveMarkedTile(location[0], location[1], facettoint(facet))
            API.MarkTile(location[0], location[1], 1177, facettoint(facet))
            if n & 1:
                API.RemoveMapMarker('Treasure')
                API.AddMapMarker('Treasure', location[0], location[1], facettoint(facet), color="purple")
                API.RemoveMarkedTile(location[0], location[1], facettoint(facet))
                API.MarkTile(location[0], location[1], 1170, facettoint(facet))
        except Exception as e:
            API.SysMsg(f"Waypoint error: {e}",33)
    #STATE 5
    if coordstatus == 2 and status == 0:
        if currentFacet(facet)[1] != currentFacet(API.GetMap())[1]:
            coordstatus = 1 #This will reset if we leave the correct facet (go to CRL for instance)
            API.RemoveMapMarker('Treasure')
            API.RemoveMarkedTile(location[0], location[1], facettoint(facet))
            compass_update(None, None)
    #STATE 6
    if tchest and tchest.Serial != lastserial:  #this will detect chest state if the script was restarted
        if DEBUG: API.SysMsg("[DEBUG] New chest detected")
        API.UseObject(tchest)
        lastserial = tchest.Serial
        API.Pause(1)
        status = findChestStatus(tchest)
    #STATE 7
    if location != None:    
        if map != 0 and abs(API.Player.X - location[0]) <2 and abs(API.Player.Y - location[1]) <2 and status == 0:
            tilez = API.GetTile(location[0], location[1]).Z #This needs to be at the beginning because the GetTile will grab the chest tile if we wait.
            API.SysMsg("Digging for chest..", 33)
            position1 = API.Player.X + API.Player.Y
            API.ClearJournal()
            API.UseObject(shovel)
            API.WaitForTarget("any",1)
            API.Target(map)
            API.WaitForTarget("any",1)
            API.Target(map)
            digging = True
            while digging == True:
                if enemyrange(2) or (API.Player.X + API.Player.Y) != position1:
                    API.SysMsg("Digging Canceled", 33)
                    digging = False
                API.Pause(1)
                tchest = findTChest()
                if tchest:
                    lastserial = tchest.Serial
                    if tchest.Z == tilez:
                        status = 1
                        API.Pause(1)
                        API.RemoveMapMarker('Treasure')
                        API.RemoveMarkedTile(location[0], location[1], facettoint(facet))
                        compass_update(None, None)
                        API.SysMsg("Chest Dug up, status = 1", 33)
                        digging = False
                        break
    API.ClearJournal()    
    while tchest != lastserial and status == 1:
        if DEBUG: API.SysMsg("[DEBUG] Chest status == 1 (locked)")
        if enemyrange(2):
            API.Pause(1)
            continue
        if findTChest():
            API.SysMsg("starting lockpick")
            API.UseObject(lockpick)
            API.WaitForTarget("any",2)
            API.Target(tchest.Serial)
            API.Pause(1)
            if API.InJournal('The lock quickly yields to your skill.') == True or API.InJournal('That appears to be trapped') == True:
                status = 2
                API.SysMsg("lock picked, status = "+str(status))
        API.Pause(1)
    #STATE 8
    while tchest != lastserial and status == 2:
        if DEBUG: API.SysMsg("[DEBUG] Chest status == 2 (trap)")
        API.ClearJournal()
        API.UseSkill("Remove Trap")
        API.WaitForTarget("any",1)
        API.Target(tchest)
        API.Pause(1)
        while not enemyrange(1) and status == 2:
            if API.InJournal('You successfully') == True or API.InJournal('That doesn') == True:
                status = 3
                break
            if API.InJournal('*Your attempt fails') == True or API.InJournal('*You delicately') == False:
                break
            if API.InJournal('That is locked.') == True:
                status = 1
                break
            API.Pause(1)
        API.Pause(1)
    #STATE 9
    if tchest != lastserial and status == 3:
                #Reset values to recalculate rune
        status = 0
        coordstatus = 0
        lastserial = tchest.Serial
        compass_update(None,None)
        try:
            API.RemoveMapMarker('Treasure')
            API.RemoveMarkedTile(tchest.X, tchest.Y, API.GetMap())
        except:
            pass
        if DEBUG: API.SysMsg("[DEBUG] Chest status == 3 (loot)")
        API.UseObject(tchest)
        API.Pause(1)
        

        if findBags(tchest):
            for bag in findBags(tchest):
                if API.Player.Weight/API.Player.WeightMax > 1:
                    API.SysMsg("Inventory full, offload some weight.", 33)
                    API.Pause(3)
                    if use_bagofsending:
                        API.SysMsg("Using Bag of Sending.",33)
                        API.SysMsg(API.ItemNameAndProps(API.FindType(3702,API.Backpack,hue=2213),True,2).splitlines()[2],33)
                        API.UseObject(API.FindType(3702,API.Backpack,hue=2213))
                        API.WaitForTarget("any",1)
                        API.Target(API.FindType(3821,API.Backpack))
                        API.Pause(.5)
                API.UseObject(bag)
                API.Pause(.2) #Pause is necessary here otherwise items will not load into the Find function
                if loot_gold:
                    grounditems = API.GetItemsOnGround(2)
                    API.HeadMsg(str(len(grounditems)),API.Player)
                    while API.FindTypeAll(3821,bag):
                        if gold1x1:
                            gold = API.FindType(3821,bag)
                            newgrounditems = API.GetItemsOnGround(2)
                            if len(newgrounditems) != len(grounditems): #This is to check for new corpses because API.IsGlobal is slow
                                if len(newgrounditems) > len(grounditems):
                                    base_ids = {getattr(it, "Serial", it) for it in grounditems}
                                    for item in newgrounditems:
                                        item_id = getattr(item, "Serial", item)
                                        if item_id not in base_ids:
                                            API.UseObject(item)
                                            API.HeadMsg("Found New Corpse, Pausing..."+str(len(newgrounditems)),API.Player)
                                            API.Pause(1)
                                            while API.IsGlobalCooldownActive():
                                                API.Pause(.1)
                                grounditems = newgrounditems
                                #Corpse check instead of globalcooldown?
                            if gold != None:
                                API.MoveItem(gold,API.Backpack,1)
                                if API.Player.Weight/API.Player.WeightMax > 1:
                                    API.SysMsg("Inventory full, offload some weight.", 33)
                                    if use_bagofsending:
                                        API.SysMsg("Using Bag of Sending.",33)
                                        API.SysMsg(API.ItemNameAndProps(API.FindType(3702,API.Backpack,hue=2213),True,2).splitlines()[2],33)
                                        API.UseObject(API.FindType(3702,API.Backpack,hue=2213))
                                        API.WaitForTarget("any",1)
                                        API.Target(API.FindType(3821,API.Backpack))
                                        API.Pause(.5)
                            API.Pause(0.6)
                            continue
                        golds = API.FindTypeAll(3821,bag)
                        for gold in golds:
                            API.MoveItem(gold.Serial,API.Backpack)
                            while API.Player.Weight/API.Player.WeightMax > 1:
                                API.SysMsg("Inventory full, offload some weight.", 33)
                                API.Pause(3)
                                if use_bagofsending:
                                    API.SysMsg("Using Bag of Sending.",33)
                                    API.SysMsg(API.ItemNameAndProps(API.FindType(3702,API.Backpack,hue=2213),True,2).splitlines()[2],33)
                                    API.UseObject(API.FindType(3702,API.Backpack,hue=2213))
                                    API.WaitForTarget("any",1)
                                    API.Target(API.FindType(3821,API.Backpack))
                                    API.Pause(.5)
                            API.Pause(2)
                    API.Pause(2)
                if use_lootmaster:
                    API.MoveItemOffset(bag.Serial,0,1,0,0)
                    API.Pause(1)
                    API.AutoLootContainer(bag.Serial)
                    API.Pause(1.1)
                    while API.IsGlobalCooldownActive():
                        API.Pause(1.1)
                    while API.Player.Weight/API.Player.WeightMax > 1:
                        API.SysMsg("Inventory full, offload some weight.", 33)
                        API.Pause(3)
                        if use_bagofsending:
                            API.SysMsg("Using Bag of Sending.",33)
                            API.SysMsg(API.ItemNameAndProps(API.FindType(3702,API.Backpack,hue=2213),True,2).splitlines()[2],33)
                            API.UseObject(API.FindType(3702,API.Backpack,hue=2213))
                            API.WaitForTarget("any",1)
                            API.Target(API.FindType(3821,API.Backpack))
                            API.Pause(.5)
        if use_lootmaster:
            API.AutoLootContainer(tchest.Serial)
            #     if use_lootmaster: #lootmaster logic is still wonky. Keeps getting stuck in loop if mobs show up.
            #         for a in range(0,6):
            #             if not API.HasTarget():
            #                 API.ReplyGump(12, 0xD06EAF) #This is the "Open" button on the chest gump
            #                 API.WaitForTarget("any",1)
            #                 continue
            #             if API.HasTarget():
            #                 break
            #         if bag != None: #This is the pause for item looting
            #             API.Target(bag)
            #             for i in range(API.Contents(bag)):
            #                 API.Pause(2.5)
            # if use_lootmaster:
            #     for a in range(0,6):
            #         if not API.HasTarget():
            #             API.ReplyGump(12, 0xd06eaf)
            #             API.WaitForTarget("any",1)
            #             continue
            #         if API.HasTarget():
            #                     API.Target(tchest.Serial)
            #                     break

        if loot_insanetokens:
            while API.FindType(3824,tchest) != None:
                tokens = API.FindTypeAll(3824,tchest)
                for token in tokens:
                    API.MoveItem(token.Serial,API.Backpack)
                    API.Pause(2)
                
        #Reset values to recalculate rune
        coordstatus = 0
        status = 0
        compass_update(None,None)
        try:
            API.RemoveMapMarker('Treasure')
            API.RemoveMarkedTile(location[0], location[1], facettoint(facet)) # We want this because otherwise TazUO permasaves the marked tile.
        except:
            pass


#ON EXIT:
compass_update(None,None)
try:
    API.RemoveMapMarker('Treasure')
    API.RemoveMarkedTile(location[0], location[1], facettoint(facet)) # We want this because otherwise TazUO permasaves the marked tile.
except:
    pass
#Update + Save
save()
