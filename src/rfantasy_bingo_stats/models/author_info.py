from enum import StrEnum
from math import isnan
from typing import (
    Any,
    Optional,
)

from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel
from pydantic.type_adapter import TypeAdapter

from rfantasy_bingo_stats.models.defined_types import (
    Author,
    SortedMapping,
)


class Gender(StrEnum):
    M = "Man"
    W = "Woman"
    N = "Nonbinary"
    U = "Unknown"


class Nationality(StrEnum):
    AFG = "Afghanistan"
    ALB = "Albania"
    DZA = "Algeria"
    AND = "Andorra"
    AGO = "Angola"
    ATG = "Antigua and Barbuda"
    ARG = "Argentina"
    ARM = "Armenia"
    AUS = "Australia"
    AUT = "Austria"
    AZE = "Azerbaijan"
    BHS = "Bahamas"
    BHR = "Bahrain"
    BGD = "Bangladesh"
    BRB = "Barbados"
    BLR = "Belarus"
    BEL = "Belgium"
    BLZ = "Belize"
    BEN = "Benin"
    BTN = "Bhutan"
    BOL = "Bolivia"
    BIH = "Bosnia and Herzegovina"
    BWA = "Botswana"
    BRA = "Brazil"
    BRN = "Brunei Darussalam"
    BGR = "Bulgaria"
    BFA = "Burkina Faso"
    BDI = "Burundi"
    CPV = "Cabo Verde"
    KHM = "Cambodia"
    CMR = "Cameroon"
    CAN = "Canada"
    CAF = "Central African Republic"
    TCD = "Chad"
    CHL = "Chile"
    CHN = "China"
    COL = "Colombia"
    COM = "Comoros"
    COG = "Congo"
    COD = "Congo (DRC)"
    CRI = "Costa Rica"
    CIV = "Côte d'Ivoire"
    HRV = "Croatia"
    CUB = "Cuba"
    CYP = "Cyprus"
    CZE = "Czechia"
    DNK = "Denmark"
    DJI = "Djibouti"
    DMA = "Dominica"
    DOM = "Dominican Republic"
    ECU = "Ecuador"
    EGY = "Egypt"
    SLV = "El Salvador"
    GNQ = "Equatorial Guinea"
    ERI = "Eritrea"
    EST = "Estonia"
    SWZ = "Eswatini"
    ETH = "Ethiopia"
    FJI = "Fiji"
    FIN = "Finland"
    FRA = "France"
    GAB = "Gabon"
    GMB = "Gambia"
    GEO = "Georgia"
    DEU = "Germany"
    GHA = "Ghana"
    GRC = "Greece"
    GRL = "Greenland"
    GRD = "Grenada"
    GTM = "Guatemala"
    GIN = "Guinea"
    GNB = "Guinea-Bissau"
    GUY = "Guyana"
    HTI = "Haiti"
    HND = "Honduras"
    HKG = "Hong Kong"
    HUN = "Hungary"
    ISL = "Iceland"
    IND = "India"
    IDN = "Indonesia"
    IRN = "Iran"
    IRQ = "Iraq"
    IRL = "Ireland"
    ISR = "Israel"
    ITA = "Italy"
    JAM = "Jamaica"
    JPN = "Japan"
    JOR = "Jordan"
    KAZ = "Kazakhstan"
    KEN = "Kenya"
    KIR = "Kiribati"
    PRK = "North Korea"
    KOR = "South Korea"
    XKX = "Kosovo"
    KWT = "Kuwait"
    KGZ = "Kyrgyzstan"
    LAO = "Laos"
    LVA = "Latvia"
    LBN = "Lebanon"
    LSO = "Lesotho"
    LBR = "Liberia"
    LBY = "Libya"
    LIE = "Liechtenstein"
    LTU = "Lithuania"
    LUX = "Luxembourg"
    MAC = "Macao"
    MDG = "Madagascar"
    MWI = "Malawi"
    MYS = "Malaysia"
    MDV = "Maldives"
    MLI = "Mali"
    MLT = "Malta"
    MHL = "Marshall Islands"
    MRT = "Mauritania"
    MUS = "Mauritius"
    MEX = "Mexico"
    FSM = "Micronesia"
    MDA = "Moldova"
    MCO = "Monaco"
    MNG = "Mongolia"
    MNE = "Montenegro"
    MAR = "Morocco"
    MOZ = "Mozambique"
    MMR = "Myanmar"
    NAM = "Namibia"
    NRU = "Nauru"
    NPL = "Nepal"
    NLD = "Netherlands"
    NZL = "New Zealand"
    NIC = "Nicaragua"
    NER = "Niger"
    NGA = "Nigeria"
    MKD = "North Macedonia"
    NOR = "Norway"
    OMN = "Oman"
    PAK = "Pakistan"
    PLW = "Palau"
    PSE = "Palestine"
    PAN = "Panama"
    PNG = "Papua New Guinea"
    PRY = "Paraguay"
    PER = "Peru"
    PHL = "Philippines"
    POL = "Poland"
    PRT = "Portugal"
    PRI = "Puerto Rico"
    QAT = "Qatar"
    ROU = "Romania"
    RUS = "Russia"
    RWA = "Rwanda"
    KNA = "Saint Kitts and Nevis"
    LCA = "Saint Lucia"
    VCT = "Saint Vincent and the Grenadines"
    WSM = "Samoa"
    SMR = "San Marino"
    STP = "Sao Tome and Principe"
    SAU = "Saudi Arabia"
    SEN = "Senegal"
    SRB = "Serbia"
    SYC = "Seychelles"
    SLE = "Sierra Leone"
    SGP = "Singapore"
    SVK = "Slovakia"
    SVN = "Slovenia"
    SLB = "Solomon Islands"
    SOM = "Somalia"
    ZAF = "South Africa"
    SSD = "South Sudan"
    ESP = "Spain"
    LKA = "Sri Lanka"
    SDN = "Sudan"
    SUR = "Suriname"
    SWE = "Sweden"
    CHE = "Switzerland"
    SYR = "Syria"
    TWN = "Taiwan"
    TJK = "Tajikistan"
    TZA = "Tanzania"
    THA = "Thailand"
    TLS = "Timor-Leste"
    TGO = "Togo"
    TON = "Tonga"
    TTO = "Trinidad and Tobago"
    TUN = "Tunisia"
    TUR = "Türkiye"
    TKM = "Turkmenistan"
    TUV = "Tuvalu"
    UGA = "Uganda"
    UKR = "Ukraine"
    SUN = "Union of Soviet Socialist Republics"
    ARE = "United Arab Emirates"
    GBR = "United Kingdom"
    USA = "United States"
    URY = "Uruguay"
    UZB = "Uzbekistan"
    VUT = "Vanuatu"
    VEN = "Venezuela"
    VNM = "Vietnam"
    YEM = "Yemen"
    ZMB = "Zambia"
    ZWE = "Zimbabwe"
    U = "Unknown"


class Ethnicity(StrEnum):
    ARABIC = "Arabic"
    ASIAN = "Asian"
    BLACK = "Black"
    HISPANIC = "Hispanic"
    MIXED = "Multiracial"
    NATIVE = "Native"
    WHITE = "White"
    U = "Unknown"


class UNSubregion(StrEnum):
    ANZ = "Australia and New Zealand"
    C = "Caribbean"
    EAF = "Eastern Africa"
    MAF = "Middle Africa"
    NAF = "Northern Africa"
    SAF = "Southern Africa"
    WAF = "Western Africa"
    CAM = "Central America"
    NAM = "Northern America"
    SAM = "South America"
    CAS = "Central Asia"
    EAS = "Eastern Asia"
    SAS = "Southern Asia"
    SEA = "Southeastern Asia"
    WAS = "Western Asia"
    EE = "Eastern Europe"
    NE = "Northern Europe"
    SE = "Southern Europe"
    WE = "Western Europe"
    MEL = "Melanesia"
    MIC = "Micronesia"
    POL = "Polynesia"


NATIONALITY_TO_SUBREGION = {
    Nationality.AFG: UNSubregion.SAS,
    Nationality.ALB: UNSubregion.SE,
    Nationality.DZA: UNSubregion.NAF,
    Nationality.AND: UNSubregion.SE,
    Nationality.AGO: UNSubregion.MAF,
    Nationality.ATG: UNSubregion.C,
    Nationality.ARG: UNSubregion.SAM,
    Nationality.ARM: UNSubregion.WAS,
    Nationality.AUS: UNSubregion.ANZ,
    Nationality.AUT: UNSubregion.WE,
    Nationality.AZE: UNSubregion.WAS,
    Nationality.BHS: UNSubregion.C,
    Nationality.BHR: UNSubregion.WAS,
    Nationality.BGD: UNSubregion.SAS,
    Nationality.BRB: UNSubregion.C,
    Nationality.BLR: UNSubregion.EE,
    Nationality.BEL: UNSubregion.WE,
    Nationality.BLZ: UNSubregion.CAM,
    Nationality.BEN: UNSubregion.WAF,
    Nationality.BTN: UNSubregion.SAS,
    Nationality.BOL: UNSubregion.SAM,
    Nationality.BIH: UNSubregion.SE,
    Nationality.BWA: UNSubregion.SAF,
    Nationality.BRA: UNSubregion.SAM,
    Nationality.BRN: UNSubregion.SEA,
    Nationality.BGR: UNSubregion.EE,
    Nationality.BFA: UNSubregion.WAF,
    Nationality.BDI: UNSubregion.EAF,
    Nationality.CPV: UNSubregion.WAF,
    Nationality.KHM: UNSubregion.SEA,
    Nationality.CMR: UNSubregion.MAF,
    Nationality.CAN: UNSubregion.NAM,
    Nationality.CAF: UNSubregion.MAF,
    Nationality.TCD: UNSubregion.MAF,
    Nationality.CHL: UNSubregion.SAM,
    Nationality.CHN: UNSubregion.EAS,
    Nationality.COL: UNSubregion.SAM,
    Nationality.COM: UNSubregion.EAF,
    Nationality.COG: UNSubregion.MAF,
    Nationality.COD: UNSubregion.MAF,
    Nationality.CRI: UNSubregion.CAM,
    Nationality.CIV: UNSubregion.WAF,
    Nationality.HRV: UNSubregion.SE,
    Nationality.CUB: UNSubregion.C,
    Nationality.CYP: UNSubregion.WAS,
    Nationality.CZE: UNSubregion.EE,
    Nationality.DNK: UNSubregion.NE,
    Nationality.DJI: UNSubregion.EAF,
    Nationality.DMA: UNSubregion.C,
    Nationality.DOM: UNSubregion.C,
    Nationality.ECU: UNSubregion.SAM,
    Nationality.EGY: UNSubregion.NAF,
    Nationality.SLV: UNSubregion.CAM,
    Nationality.GNQ: UNSubregion.MAF,
    Nationality.ERI: UNSubregion.EAF,
    Nationality.EST: UNSubregion.NE,
    Nationality.SWZ: UNSubregion.SAF,
    Nationality.ETH: UNSubregion.EAF,
    Nationality.FJI: UNSubregion.MEL,
    Nationality.FIN: UNSubregion.NE,
    Nationality.FRA: UNSubregion.WE,
    Nationality.GAB: UNSubregion.MAF,
    Nationality.GMB: UNSubregion.WAF,
    Nationality.GEO: UNSubregion.WAS,
    Nationality.DEU: UNSubregion.WE,
    Nationality.GHA: UNSubregion.WAF,
    Nationality.GRC: UNSubregion.SE,
    Nationality.GRL: UNSubregion.NAM,
    Nationality.GRD: UNSubregion.C,
    Nationality.GTM: UNSubregion.CAM,
    Nationality.GIN: UNSubregion.WAF,
    Nationality.GNB: UNSubregion.WAF,
    Nationality.GUY: UNSubregion.SAM,
    Nationality.HTI: UNSubregion.C,
    Nationality.HND: UNSubregion.CAM,
    Nationality.HKG: UNSubregion.EAS,
    Nationality.HUN: UNSubregion.EE,
    Nationality.ISL: UNSubregion.NE,
    Nationality.IND: UNSubregion.SAS,
    Nationality.IDN: UNSubregion.SEA,
    Nationality.IRN: UNSubregion.SAS,
    Nationality.IRQ: UNSubregion.WAS,
    Nationality.IRL: UNSubregion.NE,
    Nationality.ISR: UNSubregion.WAS,
    Nationality.ITA: UNSubregion.SE,
    Nationality.JAM: UNSubregion.C,
    Nationality.JPN: UNSubregion.EAS,
    Nationality.JOR: UNSubregion.WAS,
    Nationality.KAZ: UNSubregion.CAS,
    Nationality.KEN: UNSubregion.EAF,
    Nationality.KIR: UNSubregion.MIC,
    Nationality.PRK: UNSubregion.EAS,
    Nationality.KOR: UNSubregion.EAS,
    Nationality.XKX: UNSubregion.SE,
    Nationality.KWT: UNSubregion.WAS,
    Nationality.KGZ: UNSubregion.CAS,
    Nationality.LAO: UNSubregion.SEA,
    Nationality.LVA: UNSubregion.NE,
    Nationality.LBN: UNSubregion.WAS,
    Nationality.LSO: UNSubregion.SAF,
    Nationality.LBR: UNSubregion.WAF,
    Nationality.LBY: UNSubregion.NAF,
    Nationality.LIE: UNSubregion.WE,
    Nationality.LTU: UNSubregion.NE,
    Nationality.LUX: UNSubregion.WE,
    Nationality.MAC: UNSubregion.EAS,
    Nationality.MDG: UNSubregion.EAF,
    Nationality.MWI: UNSubregion.EAF,
    Nationality.MYS: UNSubregion.SEA,
    Nationality.MDV: UNSubregion.SAS,
    Nationality.MLI: UNSubregion.WAF,
    Nationality.MLT: UNSubregion.SE,
    Nationality.MHL: UNSubregion.MIC,
    Nationality.MRT: UNSubregion.WAF,
    Nationality.MUS: UNSubregion.EAF,
    Nationality.MEX: UNSubregion.CAM,
    Nationality.FSM: UNSubregion.MIC,
    Nationality.MDA: UNSubregion.EE,
    Nationality.MCO: UNSubregion.WE,
    Nationality.MNG: UNSubregion.EAS,
    Nationality.MNE: UNSubregion.SE,
    Nationality.MAR: UNSubregion.NAF,
    Nationality.MOZ: UNSubregion.EAF,
    Nationality.MMR: UNSubregion.SEA,
    Nationality.NAM: UNSubregion.SAF,
    Nationality.NRU: UNSubregion.MIC,
    Nationality.NPL: UNSubregion.SAS,
    Nationality.NLD: UNSubregion.WE,
    Nationality.NZL: UNSubregion.ANZ,
    Nationality.NIC: UNSubregion.CAM,
    Nationality.NER: UNSubregion.WAF,
    Nationality.NGA: UNSubregion.WAF,
    Nationality.MKD: UNSubregion.SE,
    Nationality.NOR: UNSubregion.NE,
    Nationality.OMN: UNSubregion.WAS,
    Nationality.PAK: UNSubregion.SAS,
    Nationality.PLW: UNSubregion.MIC,
    Nationality.PSE: UNSubregion.WAS,
    Nationality.PAN: UNSubregion.CAM,
    Nationality.PNG: UNSubregion.MEL,
    Nationality.PRY: UNSubregion.SAM,
    Nationality.PER: UNSubregion.SAM,
    Nationality.PHL: UNSubregion.SEA,
    Nationality.POL: UNSubregion.EE,
    Nationality.PRT: UNSubregion.SE,
    Nationality.PRI: UNSubregion.C,
    Nationality.QAT: UNSubregion.WAS,
    Nationality.ROU: UNSubregion.EE,
    Nationality.RUS: UNSubregion.EE,
    Nationality.RWA: UNSubregion.EAF,
    Nationality.KNA: UNSubregion.C,
    Nationality.LCA: UNSubregion.C,
    Nationality.VCT: UNSubregion.C,
    Nationality.WSM: UNSubregion.POL,
    Nationality.SMR: UNSubregion.SE,
    Nationality.STP: UNSubregion.MAF,
    Nationality.SAU: UNSubregion.WAS,
    Nationality.SEN: UNSubregion.WAF,
    Nationality.SRB: UNSubregion.SE,
    Nationality.SYC: UNSubregion.EAF,
    Nationality.SLE: UNSubregion.WAF,
    Nationality.SGP: UNSubregion.SEA,
    Nationality.SVK: UNSubregion.EE,
    Nationality.SVN: UNSubregion.SE,
    Nationality.SLB: UNSubregion.MEL,
    Nationality.SOM: UNSubregion.EAF,
    Nationality.ZAF: UNSubregion.SAF,
    Nationality.SSD: UNSubregion.EAF,
    Nationality.ESP: UNSubregion.SE,
    Nationality.LKA: UNSubregion.SAS,
    Nationality.SDN: UNSubregion.NAF,
    Nationality.SUR: UNSubregion.SAM,
    Nationality.SWE: UNSubregion.NE,
    Nationality.CHE: UNSubregion.WE,
    Nationality.SYR: UNSubregion.WAS,
    Nationality.TWN: UNSubregion.EAS,
    Nationality.TJK: UNSubregion.CAS,
    Nationality.TZA: UNSubregion.EAF,
    Nationality.THA: UNSubregion.SEA,
    Nationality.TLS: UNSubregion.SEA,
    Nationality.TGO: UNSubregion.WAF,
    Nationality.TON: UNSubregion.POL,
    Nationality.TTO: UNSubregion.C,
    Nationality.TUN: UNSubregion.NAF,
    Nationality.TUR: UNSubregion.WAS,
    Nationality.TKM: UNSubregion.CAS,
    Nationality.TUV: UNSubregion.POL,
    Nationality.UGA: UNSubregion.EAF,
    Nationality.UKR: UNSubregion.EE,
    Nationality.ARE: UNSubregion.WAS,
    Nationality.GBR: UNSubregion.NE,
    Nationality.USA: UNSubregion.NAM,
    Nationality.URY: UNSubregion.SAM,
    Nationality.SUN: UNSubregion.EE,
    Nationality.UZB: UNSubregion.CAS,
    Nationality.VUT: UNSubregion.MEL,
    Nationality.VEN: UNSubregion.SAM,
    Nationality.VNM: UNSubregion.SEA,
    Nationality.YEM: UNSubregion.WAS,
    Nationality.ZMB: UNSubregion.EAF,
    Nationality.ZWE: UNSubregion.EAF,
}


class AuthorInfo(BaseModel):
    """Information about a single author"""

    gender: Gender = Gender.U
    ethnicity: Ethnicity = Ethnicity.U
    queer: Optional[bool] = None
    nationality: Nationality = Nationality.U

    @field_validator("queer", mode="plain")
    @classmethod
    def opt_bool(cls, data: Any) -> Optional[bool]:  # type: ignore[explicit-any]
        if data is None or isnan(data):
            return None
        return bool(data)


AuthorInfoAdapter: TypeAdapter[SortedMapping[Author, AuthorInfo]] = TypeAdapter(
    SortedMapping[Author, AuthorInfo]
)
