import xarray as xr
import os
import numpy as np
import json
import yaml


def net_rating(net):
    net = int(net)
    conditions = [
        net >= 39,
        net <= -6,
        ((-1 <= net) & (net <= -5)) | ((37 <= net) & (net <= 39)),
        (0 <= net) & (net <= 6),
        ((7 <= net) & (net <= 10)) | ((35 <= net) & (net <= 36)),
        ((11 <= net) & (net <= 14)) | ((33 <= net) & (net <= 34)),
        ((15 <= net) & (net <= 17)) | ((31 <= net) & (net <= 32)),
        ((18 <= net) & (net <= 19)) | ((29 <= net) & (net <= 30)),
        (27 <= net) & (net <= 28),
        ((20 <= net) & (net <= 22)) | (net == 26),
        (23 <= net) & (net <= 25)
    ]

    choices = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    ]

    return np.select(conditions, choices, default=np.nan)


def cc_rating(cc):
    cc = int(cc)
    conditions = [
        cc == 100,
        (cc >= 91) & (cc <= 99),
        (cc >= 81) & (cc <= 90),
        (cc >= 71) & (cc <= 80),
        (cc >= 61) & (cc <= 70),
        (cc >= 51) & (cc <= 60),
        (cc >= 41) & (cc <= 50),
        (cc >= 31) & (cc <= 40),
        (cc >= 11) & (cc <= 30),
        (cc >= 0) & (cc < 1),
        (cc >= 1) & (cc <= 10)
    ]

    choices = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10
    ]

    return np.select(conditions, choices, default=np.nan)


def tp_rating(tp):
    conditions = [
        tp > 25,
        (tp > 12) & (tp <= 25),
        (tp >= 9) & (tp <= 12),
        (tp >= 6) & (tp < 9),
        (tp >= 3) & (tp < 6),
        (tp > 0) & (tp < 3),
        tp == 0
    ]

    choices = [
        -1, 0, 2, 5, 8, 9, 10
    ]

    return np.select(conditions, choices, default=np.nan)


def ws_rating(ws):
    conditions = [
        ws > 70,
        (ws >= 50) & (ws <= 70),
        (ws >= 40) & (ws < 50),
        (ws >= 30) & (ws < 40),
        (ws >= 20) & (ws < 30),
        (ws >= 10) & (ws < 20),
        (ws >= 1) & (ws < 10),
        (ws >= 0) & (ws < 1)
    ]

    choices = [
        -10, 0, 3, 6, 8, 9, 10, 8  # Note: last choice is 8 based on the table you provided
    ]

    return np.select(conditions, choices, default=np.nan)


def hci_rating(hci):
    conditions = [
        (hci >= 70) & (hci <= 100),
        (hci >= 50) & (hci < 70),
        (hci >= 10) & (hci < 50),
        (hci >= 0) & (hci < 10)
    ]

    choices = [
        4, 3, 2, 1
    ]

    return np.select(conditions, choices, default=np.nan)


def hci_text(hci_rating):
    if hci_rating == 4:
        return 'Kondisi cuaca ideal'
    elif hci_rating == 3:
        return 'Perlu diantisipasi potensi gangguan cuaca'
    elif hci_rating == 2:
        return 'Potensi gangguan cuaca signifikan'
    elif hci_rating == 1:
        return 'Sebaiknya dihindari'


# IBF Text function
def ibf_text(tp_rate, net_rate, ws_rate, tcc_rate):
    all_text = []
    prec_text = np.select(
        [(tp_rate == 10) | (tp_rate == 9),
         tp_rate == 8,
         tp_rate == 5,
         tp_rate <= 2],
        ['Terdapat potensi gerimis / hujan ringan namun tidak memberikan dampak atau gangguan.',
         'Jalur setapak pendakian dapat menjadi licin, tetapi aktivitas masih dapat dilakukan. Aktivitas walking tour atau hiking pendek kurang nyaman dilakukan. Aktivitas pantai masih mungkin dilakukan, namun kurang nyaman.',
         'Jalur hiking bisa menjadi lebih licin dan berbahaya, terutama di jalur yang curam; aktivitas masih dapat dilakukan dengan lebih berhati-hati. Risiko tergelincir atau jatuh ketika hiking. Jarak pandang dapat menurun akibat hujan. Ketinggian ombak dapat meningkat, aktivitas berenang di pantai dapat berbahaya.',
         'Jalur hiking bisa menjadi sangat licin, dapat terjadi genangan atau aliran air di jalur setapak. Risiko banjir dan longsor dapat terjadi. Risiko terjadi pohon tumbang dan sambaran petir ketika hujan badai. Ketinggian ombak dapat meningkat signifikan akibat hujan badai hindari aktivitas di pantai.'
         ], default='Tidak ada informasi dampak hujan')

    net_text = np.select(
        [(net_rate >= 9) & (net_rate <= 10),
         (net_rate >= 6) & (net_rate < 9),
         (net_rate >= 3) & (net_rate < 6),
         (net_rate >= 0) & (net_rate < 3)],
        ['Kondisi suhu udara dan kelembapan nyaman untuk melakukan aktivitas luar ruangan.',
         'Suhu udara terasa sedikit panas, aktivitas masih dapat dilakukan.',
         'Risiko kelelahan ketika melakukan aktivitas luar ruangan meningkat.',
         'Kondisi udara terlalu panas dan lembap untuk aktivitas fisik berat, risiko kelelahan dan dehidrasi meningkat.'],
        default='Tidak ada informasi dampak suhu')

    ws_text = np.select(
        [(ws_rate >= 9) & (ws_rate <= 10),
         (ws_rate >= 6) & (ws_rate < 9),
         (ws_rate >= 3) & (ws_rate < 6),
         (ws_rate >= 0) & (ws_rate < 3)],
        ['Angin sepoi-sepoi, mendukung aktivitas luar ruangan.',
         'Kecepatan angin meningkat, gangguan-gangguan kecil dapat terjadi namun tetap aman dalam beraktivitas.',
         'Angin dapat menerbangkan debu / pasir, dahan dan ranting pohon. Mengganggu kenyamanan beraktivitas. Gelombang di pantai dapat meningkat dan mengganggu aktivitas berenang.',
         'Angin kencang dapat terjadi, meningkatkan resiko pohon tumbang di jalur hiking atau wilayah pepohonan. Ombak di pantai dapat menjadi cukup tinggi dan berbahaya untuk aktivitas di pantai.'],
        default='Tidak ada informasi dampak angin')

    tcc_text = np.select(
        [(tcc_rate >= 9) & (tcc_rate <= 10),
         (tcc_rate >= 6) & (tcc_rate < 9),
         (tcc_rate >= 3) & (tcc_rate < 6),
         (tcc_rate >= 0) & (tcc_rate < 3)],
        ['Langit cerah, tutupan awan sangat minim.',
         'Tutupan awan dapat sedikit mengganggu pemandangan.',
         'Tutupan awan cukup tebal dan dapat mengganggu pemandangan.',
         'Langit tertutup awan sepenuhnya / mendung, pemandangan seperti sunset tidak dapat diamati.'],
        default='Tidak ada informasi dampak kondisi langit')

    # Append texts based on condition
    all_text.append(prec_text)

    if tp_rate > 8:
        all_text.extend([net_text, ws_text, tcc_text])

    # Convert numpy arrays to strings and flatten list
    all_text = [str(text) for text in all_text]

    return all_text


def main():
    data_path = "D:/Data/sample_df"
    ftimes = [i for i in range(0, 10)]
    filelist = [f"{data_path}/harmonization_df_{i:}.grib" for i in ftimes]
    lat_slice = slice(-7.7, -11.08)
    lon_slice = slice(118.40, 125.35)

    print('Load data')
    ds = xr.open_mfdataset(filelist, engine='cfgrib', concat_dim='time', combine='nested',
                           backend_kwargs={'filter_by_keys': {'dataType': 'fc', }}).sel(latitude=lat_slice,
                                                                                        longitude=lon_slice)
    ds_wind = xr.open_mfdataset(filelist, engine='cfgrib', concat_dim='time', combine='nested', backend_kwargs={
        'filter_by_keys': {'dataType': 'fc', 'typeOfLevel': 'heightAboveGround', 'level': 10.0}}).sel(
        latitude=lat_slice, longitude=lon_slice)

    print('Calculate parameters')
    ws_ms = (ds_wind['u10'] ** 2 + ds_wind['v10'] ** 2) ** 0.5
    ws_km = (ws_ms * 3.6).round(0)
    wd = ((270 - np.degrees(np.arctan2(ds_wind['v10'], ds_wind['u10']))) % 360).round(0)
    tp = (ds['tp']).round(1)
    t2 = (ds['t2m'] - 273.15).round(1)
    r2 = (ds['r2']).round(0)
    tcc = (ds['tcc']).round(0)

    term1 = 37 - (37 - t2) / (0.68 - 0.0014 * r2 + 1 / (1.76 + 1.4 * ws_ms ** 0.75))
    term2 = 0.29 * t2 * (1 - 0.01 * r2)
    NET = term1 - term2

    print('Calculate ratings')
    NET_rating = xr.apply_ufunc(
        net_rating,  # function to apply
        NET,  # input DataArray
        vectorize=True, dask='parallelized'  # vectorize allows element-wise application
    )

    TP_rating = xr.apply_ufunc(
        tp_rating,  # function to apply
        tp,  # input DataArray
        vectorize=True, dask='parallelized'  # vectorize allows element-wise application
    )

    WS_rating = xr.apply_ufunc(
        ws_rating,  # function to apply
        ws_km,  # input DataArray
        vectorize=True, dask='parallelized'
    )  # vectorize allows element-wise application

    TCC_rating = xr.apply_ufunc(
        cc_rating,  # function to apply
        tcc,  # input DataArray
        vectorize=True, dask='parallelized'  # vectorize allows element-wise application
    )

    HCI = (4 * NET_rating.values) + (2 * TCC_rating.values) + (3 * TP_rating.values) + (1 * WS_rating.values)
    HCI = xr.DataArray(HCI, coords=ds.coords, dims=ds.dims, attrs=ds.attrs)

    HCI_rating = xr.apply_ufunc(
        hci_rating,  # function to apply
        HCI,  # input DataArray
        vectorize=True,  # vectorize allows element-wise application
        dask='parallelized'
    )

    destinasi = [
        {"nama": "Pulau Komodo", "latitude": -8.566487, "longitude": 119.488146},
        {"nama": "Pulau Padar", "latitude": -8.649305, "longitude": 119.623066},
        {"nama": "Pulau Rinca", "latitude": -8.711295, "longitude": 119.699974},
        {"nama": "Pantai Pink", "latitude": -8.556533, "longitude": 119.512536},
        {"nama": "Goa Batu Cermin", "latitude": -8.521387, "longitude": 119.872306},
        {"nama": "Pulau Kanawa", "latitude": -8.498315, "longitude": 119.759122},
        {"nama": "Pulau Seraya", "latitude": -8.485655, "longitude": 119.856750},
        {"nama": "Manta Point", "latitude": -8.700915, "longitude": 119.518787},
        {"nama": "Taka Makassar", "latitude": -8.641016, "longitude": 119.537625},
        {"nama": "Pulau Kelor", "latitude": -8.533795, "longitude": 119.822438},
    ]

    dest_holder = []
    print('Preparing json output')
    for d in destinasi:
        print(f"Processing {d['nama']}")
        loc_name = d['nama']
        loc_lat = d['latitude']
        loc_lon = d['longitude']

        # Pre-select all data for the location
        tp_loc = tp.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        t2_loc = t2.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        r2_loc = r2.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        wd_loc = wd.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        ws_loc = ws_km.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        tcc_loc = tcc.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        net_loc = NET.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        net_rating_loc = NET_rating.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        tp_rating_loc = TP_rating.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        ws_rating_loc = WS_rating.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        tcc_rating_loc = TCC_rating.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        hci_loc = HCI.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()
        hci_rating_loc = HCI_rating.sel(latitude=loc_lat, longitude=loc_lon, method='nearest').load()

        forecast_list = []
        for i in range(tp_loc.sizes['time']):
            forecast = {
                "index": i,
                "analysis_date": ds.time.values[i].astype(str).item(),
                "valid_date": ds.valid_time.values[i].astype(str).item(),
                "tp": tp_loc.isel(time=i).values.item(),
                "t2": t2_loc.isel(time=i).values.item(),
                "r2": r2_loc.isel(time=i).values.item(),
                "wd": wd_loc.isel(time=i).values.item(),
                "ws": ws_loc.isel(time=i).values.item(),
                "tcc": tcc_loc.isel(time=i).values.item(),
                "normal_effective_temperature": net_loc.isel(time=i).values.item(),
                "net_rating": net_rating_loc.isel(time=i).values.item(),
                "tp_rating": tp_rating_loc.isel(time=i).values.item(),
                "ws_rating": ws_rating_loc.isel(time=i).values.item(),
                "tcc_rating": tcc_rating_loc.isel(time=i).values.item(),
                "hci": hci_loc.isel(time=i).values.item(),
                "hci_rating": hci_rating_loc.isel(time=i).values.item(),
                "hci_text": hci_text(hci_rating_loc.isel(time=i).values.item())
            }
            forecast_list.append(forecast)

        # Determine minimum HCI and related data
        hci_min_index = hci_loc.argmin(dim="time").item()
        hci_min = hci_loc.isel(time=hci_min_index).values.item()
        hci_min_text = hci_text(hci_rating_loc.isel(time=hci_min_index).values.item())
        tp_rating_min = tp_rating_loc.isel(time=hci_min_index).values.item()
        net_rating_min = net_rating_loc.isel(time=hci_min_index).values.item()
        ws_rating_min = ws_rating_loc.isel(time=hci_min_index).values.item()
        tcc_rating_min = tcc_rating_loc.isel(time=hci_min_index).values.item()
        impact_text = ibf_text(tp_rating_min, net_rating_min, ws_rating_min, tcc_rating_min)

        data_dict={
            "nama": loc_name,
            "latitude": loc_lat,
            "longitude": loc_lon,
            "forecast": forecast_list,
            "hci_min": hci_min,
            "hci_min_text": hci_min_text,
            "impact_text": impact_text
        }
        dest_holder.append(data_dict)

    with open('D:/Data/ibf_tourism.json', 'w') as f:
        json.dump(dest_holder, f, indent=4)


if __name__ == "__main__":
    main()