import pandas as pd

def srecords_to_df(srec):

    full_lines = []

    def dms_to_dd(dms, direction):
        degrees = int(dms[:2] if direction in 'NS' else dms[:3])
        minutes = int(dms[2:4] if direction in 'NS' else dms[3:5])
        seconds = float(dms[4:] if direction in 'NS' else dms[5:])
        dd = degrees + minutes/60 + seconds/3600
        if direction in ['S', 'W']:
            dd = -dd
        return dd

    if hasattr(srec, 'read'):
        # It's a file-like object (like TemporaryUploadedFile)
        flines = srec.read().decode('utf-8').splitlines()
    else:
        # It's a string path
        with open(srec, 'r') as f:
            flines = f.readlines()

    for k, v in enumerate(flines):
        if v[0] == 'S':
            entry = list()
            line = v.strip('\n')
            line = line.split(',')
            entry.append(line[0][1:11])  # linename
            entry.append(int(line[0][20:25]))  # sp

            # Convert lat and long to decimal degrees
            lat = dms_to_dd(line[0][25:34], line[0][34])
            lon = dms_to_dd(line[0][35:45], line[0][45])
            entry.append(lat)
            entry.append(lon)
            
            entry.append(float(line[0][47:55]))  # east
            entry.append(float(line[0][55:64]))  # north
            entry.append(float(line[0][64:70]))  # depth
            entry.append(int(line[0][70:73]))  # jday
            entry.append(line[0][73:79])  # time

            # Convert Z coordinates to decimal degrees
            for z in [flines[k - 3], flines[k - 2], flines[k - 1]]:
                zline = z.strip('\n').split(',')
                zlat = dms_to_dd(zline[0][25:34], zline[0][34])
                zlon = dms_to_dd(zline[0][35:45], zline[0][45])
                entry.append(zlat)
                entry.append(zlon)

            full_lines.append(entry)

    def ave_x(x1, x2, x3):
        meanx = (float(x1) + float(x2) + float(x3))/3
        return meanx


    df = pd.DataFrame(data=full_lines, columns=[
                                        'linename',
                                        'sp',
                                        'lat',
                                        'long',
                                        'east',
                                        'north',
                                        'depth',
                                        'jday',
                                        'time',
                                        'zlat1',
                                        'zlon1',
                                        'zlat2',
                                        'zlon2',
                                        'zlat3',
                                        'zlon3',
                                        ]
                      )
    df['mean lat'] = df.apply(lambda x: ave_x(x['zlat1'], x['zlat2'], x['zlat3']), axis=1)
    df['mean lon'] = df.apply(lambda x: ave_x(x['zlon1'], x['zlon2'], x['zlon3']), axis=1)
    return df