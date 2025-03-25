"""Script to calculate minimum distance and time from gnss data
NV2022"""

print("(0) Minimun Distance (km), (1) Minimun time (min) ",end="")
cl=int(input())

if cl == 0:
    print("input the time of observation: ",end="")
    time = float(input())
    dsmin=((time-65)/3)+10 #kilometros
    print("minimun distance: "+str(round(dsmin,3))+" km")
else:
    print("input the distance between base: ",end="")
    Dist = float(input())
    timemin=65+(3*(Dist-10)) #minutes
    print("minimun time: "+str(round(timemin,1))+" min" )
    