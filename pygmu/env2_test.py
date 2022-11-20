import pygmu as pg
import numpy as np

a = pg.CropPE(pg.ConstPE(6.0), pg.Extent(10, 20))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(0, 10))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(5, 15))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(10, 20))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(15, 25))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(20, 30))
pg.PrintPE(pg.Env2PE(a, 2, 3)).render(pg.Extent(5, 25))
