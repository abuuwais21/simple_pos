import datetime as dt

ADMIN_M = "admin_m"
PELANGGAN_M = "pelanggan_m"
LAUNDRY_M = "laundry_m"
JENISLAUNDRY_T = "jenislaundry_t"
KETLAUNDRY_T = "keteranganlaundry_t"
PARFUM_T = "parfum_t"
HANDSIGN_IMG_T = "handsign_img_t"


def format_date(datetime_):
    return datetime_
    #return datetime_.strftime('%Y-%m-%d %H:%M:%S-%f')
    # return dt.datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S-%f')
