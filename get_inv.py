import pickle

from obspy import UTCDateTime
from obspy.clients.fdsn import Client

bridge_lat, bridge_lon = 39.21596, -76.52978 # TODO: duplication.

client = Client("IRIS")

inv = client.get_stations(
    network="*",
    station="*",
    level="response",
    latitude=bridge_lat,
    longitude=bridge_lon,
    starttime=UTCDateTime("2000-01-01"),
    endtime=UTCDateTime("2024-04-01"),
    # Radius in degrees.
    minradius=0,
    maxradius=2,
)

if __name__ == "__main__":
    with open("inv.pickle", "wb") as f:
        pickle.dump(inv, f)
