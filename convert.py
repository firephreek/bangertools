import pynbody
# currently v1.4.2
    # most recent version is v1.6.0 or v2.0.0-beta
import pynbody.analysis.angmom
import numpy as np #max v1.26.4

# constants
msun_gram = 2e30
munit = 2.36e+05
mp = 1.7e-27
pccm = (3.08e21)**3
den_to_amucc = (msun_gram * munit ) / (pccm*mp)

file = '<path to snapshot>'
s = pynbody.load(file) # s is sim
s.physical_units()
stars = s.stars
s.read_starlog('<path to snapshot>.starlog')
bhinds, =  np.where(s.stars['tform']<0)
massform = s.stars['massform'][bhinds].in_units('Msol')
tform = -1.0*s.stars['tform'][bhinds].in_units('Gyr')
rhoform = s.stars['rhoform'][bhinds] * den_to_amucc
posform = s.stars['posform'][bhinds]
tempform = s.stars['tempform'][bhinds]
#velform = s.stars['velform'][bhinds]
print(massform)
print("formation density = ",rhoform)

# Finding the center of mass of halo
com = pynbody.analysis.halo.center_of_mass(s)
#print("Center of mass for halo: " , com , com.units)

# To find black holes
def findBH(s):
    BHfilter = pynbody.filt.LowPass('tform',0.0)
    BH = s.stars[BHfilter]
    print("BHs found in sim: " , len(BH))
    return BH
print("*defined BHs")
BH= findBH(s)
print("BH masses: ",BH['mass'])
print("BH iords: ",BH['iord'])

# the program won't run without this variable defined first
idkwhy = BH['r']

# Includes relative hcom position, tform, mass, rho, temp
def infoBHs(s):



    for i in range(len(BH)):
        # This is just to use as a parameter for the following function
        whichBH = BH[i]


        print("Black Hole #" , i + 1)
        #Rel halo com position:
        print("\t XYZ relative to halo com: " , BH[i]['pos'][0] - com , BH[i]['pos'].units)
        #BH mass:
        print("\t Mass of black hole: " , BH[i]['mass'][0] , BH[i]['mass'].units)
        #BH time of formation:
        print("\t Time of formation: " , BH[i]['tform'][0] * -1 , "gyrs")
        #BH rho (density):
        print("\t Density (rho): " , BH[i]['rhoform'][0] , "amu / ccm")
        #BH temperature:
        print("\t Temperature: " , BH[i]['tempform'][0] , "kelvin")
        #BH simple distance
        #print("\t Distance:" , BHdist_hcom(s) , " kpcs")



infoBHs(s)

print("there are this many stars: ",len(stars))
'''
# halo pic
pynbody.plot.image(s.gas, units="Msol kpc^-2", cmap="BuPu", width = 2)
plt.show()

#Let's take a look-see
def BH_pltcoord(s):
    # halo pic
    start = 0

    kpc_to_inches = 0.0195
    physical_width_kpc = 300
    physical_width_inches = physical_width_kpc * kpc_to_inches
    which_BH = 0

    for BH_len in BH:

        max_runs = len(BH)
        if start >= max_runs:
            break

        BHx = BH['x']
        BHy = BH['y']
        plt.scatter(BHx, BHy, c='black', marker='o' , label='Data Points')
        plt.text(BHx[start] - 0.05,BHy[start] - 0.05,str(start))
        which_BH = which_BH + 1

        start = start + 1

    plt.xlim(-1, 1)
    plt.ylim(-1, 1)
    plt.figure(figsize=(75, 75))
    plt.show()

BH_pltcoord(s)

# Plot the scatter plot with matching size
'''