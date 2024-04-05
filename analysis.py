import pickle

from obspy import UTCDateTime
from obspy.clients.filesystem.tsindex import Client

with open("inv.pickle", "rb") as f:
    inv = pickle.load(f)

client = Client("rrepo/data/timeseries.sqlite")

bridge_lat, bridge_lon = 39.21596, -76.52978
event_time = UTCDateTime("2024-03-26T5:29:00Z")

st = client.get_waveforms("*", "*", "*", "*", event_time - 5*60, event_time + 5*60)
for tr in st:
    coords = inv.get_coordinates(tr.get_id())
    tr.stats.distance = obspy.geodetics.base.gps2dist_azimuth(coords["latitude"], coords["longitude"], bridge_lat, bridge_lon)[0]
    tr.stats.back_azimuth = obspy.geodetics.base.gps2dist_azimuth(bridge_lat, bridge_lon, coords["latitude"], coords["longitude"])[2]
st.rotate("NE->RT")


def plot(station_code):
    st2 = st.select(station=station_code)
    st2 = st2.copy()
    st2.taper(0.005)
    st2.filter("bandpass", freqmin=1, freqmax=5)
    st2.slice(starttime=event_time, endtime=event_time + 2*60).plot()

def plot_spectrogram(station_code):
    st2 = st.select(station=station_code, component="Z")
    st2 = st2.copy()
    st2.slice(starttime=event_time, endtime=event_time + 2*60).spectrogram()

def plot_section(component="Z"):
    st2 = st.select(component=component)
    st2 = st2.copy()
    st2.taper(0.005)
    st2.filter("bandpass", freqmin=1, freqmax=5)
    st2.slice(starttime=event_time).plot(type="section", orientation="horizontal")
