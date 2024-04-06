import pickle

import obspy
import obspy.signal
import scipy
from matplotlib import pyplot as plt
from obspy import UTCDateTime
from obspy.clients.filesystem.tsindex import Client

with open("inv.pickle", "rb") as f:
    inv = pickle.load(f)

client = Client("rrepo/data/timeseries.sqlite")

bridge_lat, bridge_lon = 39.21596, -76.52978
event_time = UTCDateTime("2024-03-26T5:29:00Z")

def load_st():
    st = client.get_waveforms("*", "*", "*", "*", event_time - 10*60, event_time + 10*60)
    st.remove_response(inventory=inv)
    for tr in st:
        coords = inv.get_coordinates(tr.get_id())
        tr.stats.distance = obspy.geodetics.base.gps2dist_azimuth(coords["latitude"], coords["longitude"], bridge_lat, bridge_lon)[0]
        tr.stats.back_azimuth = obspy.geodetics.base.gps2dist_azimuth(bridge_lat, bridge_lon, coords["latitude"], coords["longitude"])[2]
    st.rotate("NE->RT")
    return st

st = load_st()


def plot(station_code, pre_s=0, post_s=60, **filter_kwargs):
    st2 = st.select(station=station_code)
    st2 = st2.copy()
    st2.taper(0.005)
    st2.filter(**filter_kwargs)
    st2.slice(starttime=event_time - pre_s, endtime=event_time + post_s).plot()

def plot_spectrogram(station_code):
    st2 = st.select(station=station_code, component="Z")
    st2 = st2.copy()
    st2.slice(starttime=event_time, endtime=event_time + 2*60).spectrogram()

def plot_section(component="Z", **filter_kwargs):
    st2 = st.select(component=component)
    st2 = st2.copy()
    st2.taper(0.005)
    st2.filter(**filter_kwargs)
    st2.slice(starttime=event_time).plot(type="section", orientation="horizontal")

def compute_spectra(tr):
    tr = tr.copy()
    tr.detrend()
    tr.taper(0.01)
    f, Pxx = scipy.signal.welch(tr.data, fs=tr.stats.sampling_rate)
    return f, Pxx

def plot_spectra(station_code):
    tr = st.select(component="Z", station=station_code)[0]
    print(len(tr))
    f, P1 = compute_spectra(tr.slice(starttime=event_time + 18, endtime=event_time + 60))
    _, P2 = compute_spectra(tr)
    plt.xlabel("Frequency [Hz]")
    plt.yscale("log")
    plt.plot(f, P1, label="event")
    plt.plot(f, P2, label="noise")
    plt.legend()
    plt.show()
