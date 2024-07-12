# AlcoWall

AlcoWall is a project which aims to create a fleet of devices able to measure ethanol 
percentage in breath of a human. Now, there is nothing special about that, but, if 
this device is placed strategicaly in places where there's a highest probabilty of
finding drunk people, maybe, just maybe, someone decides to test himself and doesn't drunk drive (DUI).

# AlcoWall server (backend)
- Offers convinent API to interface with database
- Manages advertisments
- Keeps track of every device within the network

# AlcoWall RPi client
- Is a state machine in charge of measurement of ethanol percentage
- User API provided by the backend to update the database

# AlcoWall service client
- TODO: Android application for a person in charge of servicing an RPi client device

# AlcoWall cashCOllector client
- TODO: Android application for a person in charge of cash collection of an RPi client device