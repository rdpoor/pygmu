import pygmu as pg

tamper67 = pg.WavReaderPE('../samples/TamperClip67.wav')
point_blank = pg.WavReaderPE('../samples/PointBlank_Clip06.wav')

print("tamper16")
pg.Transport(tamper67).play()

print("point_blank")
pg.Transport(point_blank).play()

print("GaneshPE(tamper67, point_blank)")
pg.Transport(pg.GaneshPE(tamper67, point_blank)).play()

print("GaneshPE(point_blank, tamper67)")
pg.Transport(pg.GaneshPE(point_blank, tamper67)).play()



