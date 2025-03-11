import re

Player.HeadMessage(0x555, "Select an Atlas to Decode")
atlas = Target.PromptTarget("Select an Atlas to Decode")

atlasname = Items.GetPropStringList(atlas)
atlasname = atlasname[len(atlasname)-1]
Items.UseItem(atlas)

Gumps.WaitForGump(0,5000)
gumpid = Gumps.CurrentGump()

fullstring = []
converted = []

for a in range(3):
    for b in range(16):
        Misc.Pause(250)
        Gumps.SendAction(gumpid,a*(16)+b+100)
        Gumps.WaitForGump(0,5000)
        coords = Gumps.GetLine(gumpid,17)
        if not coords:
            Items.UseItem(atlas)
            Gumps.WaitForGump(0,5000)
            gumpid = Gumps.CurrentGump()
            Misc.Pause(250)
            for i in range(a):
                Gumps.SendAction(gumpid,1150)
                Gumps.WaitForGump(0,5000)
                gumpid = Gumps.CurrentGump()
                Misc.Pause(250)
            Misc.Pause(250)
            Gumps.SendAction(gumpid,a*(16)+b+100)
            Gumps.WaitForGump(0,5000)
            Misc.Pause(250)
            coords = Gumps.GetLine(gumpid,17)
        if re.search(r"\d+", coords): #if sextant coords found
            coords = Gumps.GetLine(gumpid,17)
            coords = coords.replace("o","").strip("<center>").strip("/<").replace(",","").replace("'"," ").split(' ')
            
            normalized = [int(coords[0]) + int(coords[1])/60,
                          coords[2],
                          int(coords[3]) + int(coords[4])/60,
                          coords[5]]
            if normalized[1] == "N": #THIS IS Y
                normalized[0] = normalized[0]*-1
            if normalized[3] == "W": #THIS IS X
                normalized[2] = normalized[2]*-1
            converted = [ round(normalized[2]*5120/360 +1323), round(normalized[0]*4096/360 +1624)]
            if converted[0] < 0:
                converted[0] = converted[0] + 5120
            if converted[1] < 0:
                converted[1] = converted[1] + 4096
            Misc.Pause(100)
        else:
            converted = [0,0]
        #i think if charges = 0 it changes the start point of the text entries
        startpoint = len(Gumps.LastGumpGetLineList()) - 18 
        fullstring.append([ atlasname,converted[0],converted[1],0,Gumps.LastGumpGetLine(startpoint + b)])

    data = Gumps.GetGumpRawLayout(gumpid)
    croppedtext_matches = re.findall(r"\{ croppedtext \d+ \d+ \d+ \d+ (\d+) \d+ \}", data)
    for index, items in enumerate(croppedtext_matches):
        if items == '331':
            Gumps.SendAction(gumpid,a*(16)+100)
            Misc.Pause(250)
            data1 = Gumps.GetGumpRawLayout(gumpid)
            items = re.findall(r"\{ croppedtext \d+ \d+ \d+ \d+ (\d+) \d+ \}", data1)[index]
            if items == '331':
                Gumps.SendAction(gumpid,a*(16)+101)
                Misc.Pause(250)
                data2 = Gumps.GetGumpRawLayout(gumpid)
                items = re.findall(r"\{ croppedtext \d+ \d+ \d+ \d+ (\d+) \d+ \}", data2)[index]
        if items == '81': #felucca/green
            fullstring[a*16 + index][3] = "fel"
        elif items == '0': #ilshenar/black
            fullstring[a*16 + index][3] = "ils"
        elif items == '1102': #malas/grey
            fullstring[a*16 + index][3] = "mal"
        elif items == '10': #trammel/purple
            fullstring[a*16 + index][3] = "tra"
        elif items == '1154': #tokuno/darkgreen
            fullstring[a*16 + index][3] = "tok"
        elif items == '1645': #termur/lightred
            fullstring[a*16 + index][3] = "ter"
        else:
            Player.HeadMessage(0x555,"error")
            break
            #0 1102 10 81 
        
    if a < 2:
        Misc.Pause(500)
        Gumps.SendAction(gumpid,1150)
        Gumps.WaitForGump(0,5000)
        gumpid = Gumps.CurrentGump()

print(fullstring)
Items.SetColor(atlas,0x1000)

#Run names are from line 1 to 16
#17 is the sextant coords
#then page must be turned
#all runic atlas' have 3 pages

#my format ["runebookname", x, y, facet, "coordsname"]
