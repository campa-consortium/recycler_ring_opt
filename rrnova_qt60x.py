import numpy as np
import re
# get focussing and defocussing trim quads in the 600 section
# for adjusting tmunes.
# Information from Rob Ainsworth 2016-03-17

# Phase trombone coefficients from Meiqin Xiao 2016-03-18
def get_rr60_trombone_settings(delta_nux, delta_nuy):
    # this is the matrix of coefficients from Meiqin
    trombone_coeffs = np.array([
[-136.992, 1678.1, 144.639, -1696.96, -74.2027, 1786.81, 47.9609, -1762.77, -52.5754], 
[35.2887, 75.3339, -33.5186, -44.1195,37.1867, 42.1706, -35.7823, -14.7396, 37.5639],
[5756.82, -1306.98, -3853.78, 1679.54, 3048.33, -1551.15, -795.505, 1760.18, 268.669],
[-151.905, -22.4222, 164.601, 12.7766, -181.884, -12.9934, 186.623, 6.74839, -192.135],
[2.98716, 15.3422, 2.88162, 14.9116, 3.0027, 15.567, 2.86146, 15.0054, 3.01143],
[-15.6529, -2.77037, -14.7677, -2.94121, -15.5028, -2.74323, -14.9448, -2.96573, -15.3222]])
    b  = np.array([0.00711792, 0.00276458, 0.0249164, 0.00257196, delta_nux, delta_nuy])
    #elements of kcoeff will be k1 values for qt601..qt609
    kcoeff = np.linalg.lstsq(trombone_coeffs, b, rcond=None)
    return kcoeff[0]
    

def adjust_rr60_trim_quads(lattice, delta_nux, delta_nuy):
    # the k coefficients are actually k*L so I have to divide by
    # l(0.3048)
    kcoeff = get_rr60_trombone_settings(delta_nux, delta_nuy)/0.3048
    valid_trim_name_regex = "qt60([1-9])[a-d]"
    trimobj = re.compile(valid_trim_name_regex)
    for elem in lattice.get_elements():
        if elem.get_type_name() == "quadrupole":
            qname = elem.get_name()
            mo = trimobj.match(elem.get_name())
            if mo:
                quadnum = int(mo.group(1))
                elem.set_double_attribute("k1", kcoeff[quadnum-1])


if __name__ == "__main__":
    import synergia
    lattice = synergia.lattice.Mad8_reader().get_lattice("ring605_fodo", "../rrnova_one_bunch/RRNOvAMu2E_04272015_flat_fixed.lat")
    print("read lattice: ", len(lattice.get_elements()), " elements")
    kcoeff = adjust_rr60_trim_quads(lattice, 0.05, 0.05)
    print ("new k coefficients for magnets: ", kcoeff)
