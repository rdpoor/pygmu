import pygmu as pg

ramp_pe = pg.LinearRampPE(20, 25, pg.Extent(0, 6))
print_pe = pg.PrintPE(ramp_pe)

print_pe.render(pg.Extent(-6, 0), 2)
print_pe.render(pg.Extent(-3, 3), 2)
print_pe.render(pg.Extent(0, 6), 2)
print_pe.render(pg.Extent(3, 9), 2)
print_pe.render(pg.Extent(6, 12), 2)
