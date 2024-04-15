import pickle

import obspy
import obspy.signal
import scipy
from matplotlib import pyplot as plt
from obspy import UTCDateTime
from obspy.clients.filesystem.tsindex import Client
from obspy.geodetics.base import gps2dist_azimuth

with open("inv.pickle", "rb") as f:
    inv = pickle.load(f)

client = Client("rrepo/data/timeseries.sqlite")


def load_st(event_time, event_lat, event_lon):
    st = client.get_waveforms(
        "*", "*", "*", "*", event_time - 5 * 60, event_time + 5 * 60
    )
    # TODO: Convert to displacement or velocity?
    st.remove_response(inventory=inv, output="DISP")
    for tr in st:
        coords = inv.get_coordinates(tr.get_id())
        dist, _, azimuth = gps2dist_azimuth(
            event_lat, event_lon, coords["latitude"], coords["longitude"]
        )
        tr.stats.distance = dist
        tr.stats.back_azimuth = azimuth
    st.rotate("NE->RT")
    return st


def compute_spectrum(tr):
    tr = tr.copy()
    tr.detrend()
    tr.taper(0.01)
    # TODO: What scaling to use?
    f, Pxx = scipy.signal.welch(tr.data, fs=tr.stats.sampling_rate)
    return f, Pxx


class Event:
    def __init__(self, event_time, lat, lon):
        self.event_time = event_time
        self.lat = lat
        self.lon = lon
        self.st = load_st(self.event_time, lat, lon)

    def plot_station(self, station_code, pre_s=0, post_s=60, **filter_kwargs):
        st2 = self.st.select(station=station_code)
        st2 = st2.copy()
        st2.taper(0.005)
        st2.filter(**filter_kwargs)
        st2.slice(
            starttime=self.event_time - pre_s, endtime=self.event_time + post_s
        ).plot()

    def plot_spectrogram(self, station_code):
        st2 = self.st.select(station=station_code, component="Z")
        st2 = st2.copy()
        st2.slice(
            starttime=self.event_time, endtime=self.event_time + 1 * 60
        ).spectrogram()

    def plot_section(self, component="Z", **filter_kwargs):
        st2 = self.st.select(component=component)
        st2 = st2.copy()
        st2.taper(0.005)
        st2.filter(**filter_kwargs)
        st2.slice(starttime=self.event_time, endtime=self.event_time + 5 * 60).plot(
            type="section", orientation="horizontal"
        )

    def plot_spectra(self, station_code, start_s, end_s):
        # TODO: Take shaking start and end as arguments.
        tr = self.st.select(component="Z", station=station_code)[0]
        print(len(tr))
        f, P1 = compute_spectrum(
            tr.slice(starttime=self.event_time + start_s, endtime=self.event_time + end_s)
        )
        _, P2 = compute_spectrum(
            tr.slice(starttime=self.event_time - 60, endtime=self.event_time)
        )
        plt.xlabel("Frequency [Hz]")
        plt.xlim(0.1, 50)
        plt.xscale("log")
        plt.yscale("log")
        plt.plot(f, P2, "k", label="noise")
        plt.plot(f, P1, "r", label="event")
        plt.legend()
        plt.show()


bridge_collision_time = UTCDateTime("2024-03-26T5:29:00Z")
bridge_lat, bridge_lon = 39.21596, -76.52978
bridge_event = Event(bridge_collision_time, bridge_lat, bridge_lon)

# MD2.1, 9 km deep
local_eq_time = UTCDateTime("2005-02-23T14:22:44")
local_eq_lat, local_eq_lon = 39.26, -76.588
local_eq_event = Event(local_eq_time, local_eq_lat, local_eq_lon)
