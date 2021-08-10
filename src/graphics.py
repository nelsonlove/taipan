import blessed

term = blessed.Terminal()

logo = term.yellow + """
 _____  _    ___ ____   _    _   _ 
|_   _|/ \  |_ _|  _ \ / \  | \ | |
  | | / _ \  | || |_) / _ \ |  \| |
  | |/ ___ \ | ||  __/ ___ \| |\  |
  |_/_/   \_\___|_| /_/   \_\_| \_|
""".strip('\n')

tagline = term.white + "A game based on the China trade of the 1800s"

pennant = term.red + "~~"

sail = term.white + """
               ,
        , `-._/ 
      .'     /  \\
    .'     ./   `\\
   / `-.  /._     \\
  /     `    ` ;-._\\
  |                \\
 /              __  \\
`-------- `---    `"-``
""".strip('\n')

boat = term.tan2 + """
        |
        |     |
        |    ||
        |    ||
        |    ||
        ||   |      
        ||   ||
        ||   ||
        |    ||
\~~~~~~~'~~~~'~~~~/~~``
 `--------------'~
""".strip('\n')

water = term.blue + """
~^~_-~^~=~^~~^=                     ~^=~^~-~^~_~^~=
 ~=~^~ _~^~ =~                          ~~^~ =_~^=
~ ~^~=~^_~^~ =~                         ~=~^~ ~^=
 ~^=~^~_~-=~^~ ^                 ~^~=~^~_~^=~^~=~
""".strip('\n')

credits = """
====================

 Created by:
         Art Canfil

====================

 Programmed by:
           Jay Link
    jlink@ilbbs.com

====================

 Copyright (c)
        1978 - 2002
         Art Canfil

====================

 Python port by:
        Nelson Love
 nelson@nelson.love

====================
""".strip('\n')

press_any_key = "Press any key to start."

empty = """
         
                 
                 
                 
""".strip('\n')

blast = """
********
********
********
********
""".strip('\n')

ship = """
-|-_|_  
-|-_|_  
_|__|__/
\\_____/ 
""".strip('\n')
