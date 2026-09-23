from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoPlace:
    name: str
    municipality: str
    province: str
    region: str
    latitude: float
    longitude: float
    istat_code: str


PLACES = [
    GeoPlace("Roma", "Roma", "RM", "Lazio", 41.9028, 12.4964, "058091"),
    GeoPlace("Milano", "Milano", "MI", "Lombardia", 45.4642, 9.19, "015146"),
    GeoPlace("Napoli", "Napoli", "NA", "Campania", 40.8518, 14.2681, "063049"),
    GeoPlace("Torino", "Torino", "TO", "Piemonte", 45.0703, 7.6869, "001272"),
    GeoPlace("Palermo", "Palermo", "PA", "Sicilia", 38.1157, 13.3615, "082053"),
    GeoPlace("Genova", "Genova", "GE", "Liguria", 44.4056, 8.9463, "010025"),
    GeoPlace("Bologna", "Bologna", "BO", "Emilia-Romagna", 44.4949, 11.3426, "037006"),
    GeoPlace("Firenze", "Firenze", "FI", "Toscana", 43.7696, 11.2558, "048017"),
    GeoPlace("Venezia", "Venezia", "VE", "Veneto", 45.4408, 12.3155, "027042"),
    GeoPlace("Perugia", "Perugia", "PG", "Umbria", 43.1107, 12.3908, "054039"),
    GeoPlace("Viterbo", "Viterbo", "VT", "Lazio", 42.4174, 12.1084, "056059"),
    GeoPlace("Tarquinia", "Tarquinia", "VT", "Lazio", 42.254, 11.756, "056050"),
    GeoPlace("San Felice Circeo", "San Felice Circeo", "LT", "Lazio", 41.2375, 13.0942, "059025"),
    GeoPlace("Latina", "Latina", "LT", "Lazio", 41.4676, 12.9037, "059011"),
    GeoPlace("Frosinone", "Frosinone", "FR", "Lazio", 41.6396, 13.3516, "060038"),
    GeoPlace("Rieti", "Rieti", "RI", "Lazio", 42.4049, 12.8625, "057059"),
    GeoPlace("Foligno", "Foligno", "PG", "Umbria", 42.956, 12.7033, "054018"),
    GeoPlace("Assisi", "Assisi", "PG", "Umbria", 43.0707, 12.6171, "054001"),
    GeoPlace("Terni", "Terni", "TR", "Umbria", 42.5636, 12.6427, "055032"),
    GeoPlace("Aosta", "Aosta", "AO", "Valle d'Aosta", 45.737, 7.32, "007003"),
    GeoPlace("Trento", "Trento", "TN", "Trentino-Alto Adige", 46.0664, 11.1258, "022205"),
    GeoPlace("Bolzano", "Bolzano", "BZ", "Trentino-Alto Adige", 46.4983, 11.3548, "021008"),
    GeoPlace("Udine", "Udine", "UD", "Friuli-Venezia Giulia", 46.0711, 13.2346, "030129"),
    GeoPlace("Ancona", "Ancona", "AN", "Marche", 43.6158, 13.5189, "042002"),
    GeoPlace("L'Aquila", "L'Aquila", "AQ", "Abruzzo", 42.3498, 13.3995, "066049"),
    GeoPlace("Campobasso", "Campobasso", "CB", "Molise", 41.5603, 14.6627, "070006"),
    GeoPlace("Bari", "Bari", "BA", "Puglia", 41.1171, 16.8719, "072006"),
    GeoPlace("Potenza", "Potenza", "PZ", "Basilicata", 40.6404, 15.8056, "076063"),
    GeoPlace("Catanzaro", "Catanzaro", "CZ", "Calabria", 38.9106, 16.5877, "079023"),
    GeoPlace("Cagliari", "Cagliari", "CA", "Sardegna", 39.2238, 9.1217, "092009"),
]


def search_places(query: str, limit: int = 8) -> list[GeoPlace]:
    normalized = query.strip().casefold()
    if len(normalized) < 2:
        return []

    starts = [place for place in PLACES if place.name.casefold().startswith(normalized)]
    contains = [place for place in PLACES if normalized in place.name.casefold() and place not in starts]
    return [*starts, *contains][:limit]
