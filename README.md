# Python-Scripts
A collection of Python Scripts for the extremely popular Ultima Online.


* atlas_decoder.py  
Scans a runic atlas and output a csv file. It sometimes messes up, probably needs some error correction.


* atlaswaypoints.csv  
Converted original ouput to a more usable format. Possibly we can skip the conversion and just have it output this.


* test12345.csv  
Original output from the atlas_decoder.


* treasure_hunter.py  

I welcome any changes/fixes/improvements from anyone else!

This is an experimental treasure hunter script.
 - Features
      -  Auto-find the closest 2 rune points, reports the point and distance.
      -  Highlights the benches that contain the book you need to open.
      -  Tells you with player.headmessage what rune you need to travel to.
      -  Tracking arrow towards treasure will show when you travel to the facet.
      -  CUO map will set a waypoint to the treasure.
      -  Auto-Dig, pick, disarm the chest when you are in range
      -  Uses Lootmaster to loot the chest.
 -  Planned Features
      - Would like to use MeesaJarJar's fake item spawner to mark the specific spot.
      - Add more point calculations based on certain filters.
      - Some way to highlight rune in the book (idk if this is possible)
      - Some way to differentiate between islands and land mass. (idk if this is possible)
 - Known Issues
      - There is a very west island in Tokuno that doesnt have a rune and it makes me sad.
      - Script sometimes does not reset the benches.
      - The auto-dig,pick,disarm seems like it could be better and stop spamming.
      - Sometimes, when looting if you walk away the script error's out.
      - ~~The GUI is depressing.~~ Not anymore its not!
      - Dictionary is included in the python script... Probably bad.
      - The tracking arrow is off in facets other than fel and tram. Don't know why.
        
