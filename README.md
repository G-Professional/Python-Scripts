# Python-Scripts
A collection of Python Scripts for the extremely popular Ultima Online.


* atlas_decoder.py  
this scan a runic atlas and output a csv file. It sometimes messes up, probably needs some error correction.


* atlaswaypoints.csv  
Converted original ouput to a more usable format. Possibly we can skip the conversion and just have it output this.


* test12345.csv  
Original output from the atlas_decoder.


* treasure_hunter.py  

This is a very experimental treasure hunter script.
 - Features
      -  Auto-find the closest 2 rune points, reports the point and distance.
      -  Highlights the benches that contain the book you need to open.
      -  Tells you with player.headmessage what rune you need to travel to.
      -  Tracking arrow will show when you travel to the facet.
      -  Auto-Dig, pick, disarm the chest when you are in range
      -  Uses Lootmaster to loot the chest.
 -  Planned Features
      - Would like to use MeesaJarJar's fake item spawner to mark the specific spot.
      - Add more point calculations based on certain filters.
      - Some way to highlight rune in the book (idk if this is possible)
      - Some way to differentiate between islands and land mass. (idk if this is possible)
 - Known Issues
      - Script sometimes does not reset the benches.
      - The auto-dig,pick,disarm seems like it could be better and stop spamming.
      - Sometimes, when looting if you walk away the script error's out.
      - The GUI is depressing.
      - The current code requires Lootmaster, an external dictionary file, and CUO for the trackingarrow. These should all be optional.
      
        
