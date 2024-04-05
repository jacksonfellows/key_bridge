import pickle

from obspy.clients.fdsn import Client

from analysis import bridge_lat, bridge_lon, event_time

client = Client("IRIS")

inv = client.get_stations(
    network="*",
    station="*",
    level="response",
    latitude=bridge_lat,
    longitude=bridge_lon,
    starttime=event_time,
    endtime=event_time + 60,
    # Radius in degrees.
    minradius=0,
    maxradius=2,
)

if __name__ == "__main__":
    with open("inv.pickle", "wb") as f:
        pickle.dump(inv, f)
