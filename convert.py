import sys

import numpy as np
import pynbody

# constants
MSUN_GRAM = 2e30
MUNIT = 2.36e+05
MP = 1.7e-27
PCCM = 3.08e21 ** 3
KPC_TO_INCHES = 0.0195
PHYSICAL_WIDTH_KPC = 300
PHYSICAL_WIDTH_INCHES = PHYSICAL_WIDTH_KPC * KPC_TO_INCHES
DEN_TO_AMUCC = (MSUN_GRAM * MUNIT) / (PCCM * MP)


def convert(input_file):
    starlog_file = input_file[:input_file.rfind('.')] + '.starlog'
    simulation = pynbody.load(input_file)
    simulation.physical_units()  # What does this call do exactly --SNC
    stars = simulation.stars
    simulation.read_starlog(starlog_file)

    bhinds, = np.where(simulation.stars['tform'] < 0)
    massform = simulation.stars['massform'][bhinds].in_units('Msol')
    rhoform = simulation.stars['rhoform'][bhinds] * DEN_TO_AMUCC
    # tform = -1.0 * simulation.stars['tform'][bhinds].in_units('Gyr')
    # posform = simulation.stars['posform'][bhinds]
    # tempform = simulation.stars['tempform'][bhinds]
    # velform = simulation.stars['velform'][bhinds]

    print(massform)
    print("formation density = ", rhoform)

    # Finding the center of mass of halo
    if pynbody.__version__ == "1.6.0":
        com = pynbody.analysis.halo.center_of_mass(simulation)
    else:
        com = pynbody.analysis.halo.center(simulation, mode='com',
                                           return_cen=True,
                                           with_velocity=False)
    print("Center of mass for halo: ", com, com.units)

    print("*defined BHs")
    BHfilter = pynbody.filt.LowPass('tform', 0.0)
    BH = simulation.stars[BHfilter]

    print("BHs found in sim: ", len(BH))
    print("BH masses: ", BH['mass'])
    print("BH iords: ", BH['iord'])

    for i in range(len(BH)):
        # This is just to use as a parameter for the following function
        curBH = BH[i]

        print("Black Hole #", i + 1)
        # Rel halo com position:
        pos_ = curBH['pos'][0]
        pos__com = pos_ - com
        print("\t XYZ relative to halo com: ", pos__com, curBH['pos'].units)
        # BH mass:

        mass_ = curBH['mass'][0]
        print("\t Mass of black hole: ", mass_, curBH['mass'].units)
        # BH time of formation:
        print("\t Time of formation: ", curBH['tform'][0] * -1, "gyrs")
        # BH rho (density):
        print("\t Density (rho): ", curBH['rhoform'][0], "amu / ccm")
        # BH temperature:
        print("\t Temperature: ", curBH['tempform'][0], "kelvin")
        # BH simple distance
        # print("\t Distance:" , BHdist_hcom(s) , " kpcs")

    print("there are this many stars: ", len(stars))


# Includes relative hcom position, tform, mass, rho, temp
def main():
    input_file = sys.argv[1]
    convert(input_file)


if __name__ == '__main__':
    main()
