# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# Copyright 2018 Ross Golder
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterInterface

import json
import logging
_logger = logging.getLogger(__name__)

CMC_URL_PREFIX = 'https://api.coinmarketcap.com/v1/ticker/?convert='


class CMCGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface
    for CoinMarketCap service
    """
    code = 'CMC'
    name = 'Coin Market Cap'

    allowed_base_currencies = [
        "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP",
        "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK",
        "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD",
        "USD", "ZAR"
    ]
    supported_currency_array = [
        "BTC", "ETH", "XRP", "BCH", "LTC", "ADA", "NEO", "XLM", "MIOTA",
        "XMR", "DASH", "XEM", "ETC", "QTUM", "LSK", "BTG", "NANO", "ZEC",
        "STEEM", "BCN", "WAVES", "STRAT", "XVG", "BTS", "DOGE", "SC", "DCR",
        "KMD", "ARDR", "ARK", "CNX", "HSR", "MONA", "DGB", "ETN", "PIVX",
        "FCT", "SYS", "GXS", "XZC", "RDD", "EMC", "NXT", "PART", "GBYTE",
        "SMART", "NEBL", "NXS", "MNX", "BTCD", "BTX", "VTC", "BLOCK",
        "GAME", "ACT", "XAS", "SKY", "NAV", "UBQ", "ZEN", "SLS", "XP",
        "PURA", "POA", "FTC", "XDN", "ION", "BCO", "EMC2", "PPC", "XBY",
        "BAY", "NLG", "LBC", "VIA", "BURST", "CLOAK", "HTML", "XCP", "AEON",
        "GRS", "ETP", "UNO", "CRW", "LKK", "ERA", "LEO", "NMC", "POT",
        "SBD", "BITB", "XWC", "ONION", "ECA", "DCT", "ZCL", "ECC", "SIB",
        "RVR", "IOC", "SHIFT", "FLASH", "MOON", "DIME", "BLK", "LET", "XEL",
        "COLX", "DMD", "VRC", "EDR", "PPY", "XPM", "GRC", "BCC", "ALQO",
        "NLC2", "MUE", "PASC", "RVN", "OMNI", "RADS", "PZM", "EXP", "XSH",
        "SLR", "FLO", "POSW", "ZOI", "MINT", "RMC", "NYC", "THC", "RISE",
        "RBY", "GBX", "EAC", "BSD", "LMC", "PHR", "TIPS", "ENRG", "USNBT",
        "CLAM", "UNIT", "BBR", "AUR", "TX", "OK", "OXY", "TOA", "XMY",
        "MUSIC", "LINDA", "BIS", "DOPE", "TCC", "NEOS", "XSPEC", "ATB",
        "GAM", "PINK", "KB3", "GCN", "ESP", "DYN", "ECN", "BUN", "PND",
        "GOLOS", "SYNX", "LUX", "DBIX", "POLIS", "NVC", "FAIR", "XLR",
        "HEAT", "XST", "SEQ", "SPHR", "IOP", "CURE", "XVC", "1337", "GEO",
        "BIO", "ATMS", "HYP", "NTRN", "DNR", "BTM", "ABY", "PIRL", "BWK",
        "KORE", "MNTP", "MEME", "SNRG", "XBC", "HUSH", "PTC", "UFO", "BTCZ",
        "EXCL", "VTR", "BRX", "IPBC", "NOTE", "VRM", "RC", "TRC", "GRFT",
        "BASH", "KZC", "ERC", "GLD", "TRF", "MONK", "ADC", "2GIVE", "HWC",
        "BELA", "RIC", "VSX", "IFLT", "CANN", "KRB", "BTDX", "XMCC", "SUMO",
        "ZER", "HUC", "BUZZ", "CRAVE", "TZC", "TES", "QRK", "ZEIT", "CREA",
        "SPR", "CMPCO", "PUT", "ODN", "SPRTS", "MTNC", "BLU", "IXC", "BRK",
        "SAGA", "GCR", "XMG", "DFT", "ZEPH", "XGOX", "EGC", "EBST", "TRUST",
        "YOC", "BLITZ", "SEND", "REC", "EFL", "ZNY", "INN", "SXC", "HXX",
        "STAK", "CHC", "FOR", "NKA", "ELLA", "GRE", "ITNS", "PKB", "BTW",
        "MXT", "RAIN", "RUP", "XFT", "UNB", "MAG", "LINX", "PROC", "ADZ",
        "MZC", "EQT", "BBP", "RUPX", "SMLY", "HOLD", "MRJA", "NOBL", "GCC",
        "GRWI", "ARC", "LDOGE", "PHO", "DP", "PURE", "ORB", "VIVO", "IC",
        "CRC", "DEUS", "MOIN", "UNIFY", "42", "MAGE", "AU", "UIS", "XPTX",
        "CDN", "CRM", "LOG", "ZENI", "ARG", "RNS", "ZET", "BRIT", "DCY",
        "BYC", "CCRB", "XPD", "BDL", "BRO", "FJC", "DEM", "START", "POP",
        "GUN", "SKC", "FRST", "PIGGY", "QBIC", "OPC", "TTC", "DFS", "BTCS",
        "HPC", "DGC", "ITI", "CPC", "CNT", "MEC", "BTA", "GLS", "MOJO",
        "SMC", "EL", "TRUMP", "BLZ", "ORE", "WHL", "MANNA", "PCN", "CJ",
        "PXC", "ONX", "XCPO", "RBT", "ENT", "POST", "ARI", "AERM", "MAO",
        "CUBE", "PNX", "LCP", "GB", "QBC", "DRXNE", "VISIO", "GRLC", "AIB",
        "HVCO", "STN", "PAK", "XHI", "TEK", "PR", "BLC", "TOKC", "BTG", "TAG",
        "ACC", "BOLI", "BCF", "ZZC", "MNM", "KAYI", "C2", "808", "XCXT",
        "TGC", "VOT", "PCOIN", "ETHD", "MCRN", "PHS", "HBC", "GLT", "DSR",
        "HONEY", "IRL", "SANDG", "GOLF", "SHND", "PASL", "HNC", "MAY",
        "INFX", "CHAN", "LBTC", "611", "REE", "VUC", "COAL", "LUNA", "BTPL",
        "GCC", "BSTAR", "XCO", "CACH", "NUKO", "MSCN", "ZYD", "PRX", "GP",
        "ATX", "ERY", "BNX", "QCN", "SFC", "LTCU", "VEC2", "CASH", "ALTCOM",
        "WOMEN", "GBC", "PLACO", "DOLLAR", "PRC", "ARGUS", "CONX", "VLTC",
        "HMC", "DMB", "XTO", "KLC", "AC", "CHIPS", "VTA", "BPL", "CARBON",
        "YASH", "CBX", "LEAF", "V", "SHORTY", "WDC", "KEK", "USC", "UNI",
        "FLT", "INSN", "ANC", "METAL", "MAX", "FST", "I0C", "SDC", "FCN",
        "XLC", "HTC", "Q2C", "NET", "KOBO", "UNIC", "TRI", "HBN", "BITS",
        "TROLL", "GRIM", "BXT", "MAC", "ELE", "FIMK", "BTCR", "CV2", "FC2",
        "TALK", "LANA", "HODL", "TIT", "BTB", "VAL", "XCN", "OPAL", "NYAN",
        "BIGUP", "HAL", "AMBER", "VIDZ", "GAIA", "UTC", "WAY", "NETKO",
        "XJO", "SIGT", "FLY", "BITZ", "TRK", "XGR", "KURT", "SCORE", "MOTO",
        "BUCKS", "CNO", "SUPER", "KUSH", "DSH", "SRC", "XPY", "SLG", "ICN",
        "ARCO", "GAP", "8BIT", "CHESS", "XRA", "MARS", "CCN", "TSE", "VC",
        "DAXX", "DTC", "PX", "BERN", "MNC", "ABJ", "SAC", "EVIL", "NEVA",
        "CYP", "XVP", "RBIES", "SPEX", "RED", "ATOM", "FRC", "SWING",
        "AMMO", "GTC", "BSTY", "STV", "UNITS", "EMD", "GLC", "BRIA", "XRE",
        "AMS", "XIOS", "ECO", "LTB", "J", "DLC", "XCT", "YTN", "BOST",
        "SPACE", "IMX", "ZUR", "LEA", "IMS", "BUMBA", "XNG", "888", "PXI",
        "KED", "MAD", "CAT", "SCRT", "JIN", "QTL", "RPC", "ASAFE2", "FRK",
        "EVO", "FIRE", "DUO", "ISL", "VLT", "MST", "ICOB", "XBTC21", "YAC",
        "CON", "DRS", "CRX", "GPU", "EUC", "PLC", "MDC", "ROOFS", "$$$",
        "DBTC", "SOJ", "FUZZ", "SCS", "SOON", "HMP", "SOIL", "ELC", "XCRE",
        "FLAX", "ANTI", "ALL", "TAJ", "ACOIN", "CPN", "WARP", "MAR", "ADCN",
        "BIP", "NRO", "CMT", "CXT", "CF", "FNC", "BENJI", "SPT", "MTLMC3",
        "CTO", "SH", "BLRY", "CAB", "LTCR", "BTQ", "GPL", "SONG", "WORM",
        "VPRC", "URO", "JWL", "PULSE", "CESC", "MND", "SLEVIN", "DLISK",
        "CNNC", "VIP", "BXC", "PONZI", "ARB", "EGO", "KRONE", "ZMC", "KNC",
        "WBB", "ICON", "STARS", "BSC", "URC", "MILO", "DRM", "STEPS", "G3N",
        "IMPS", "RIDE", "BIOS", "XBTS", "BRAIN", "PIE", "PEX", "ORLY", "BOAT",
        "TAGR", "JOBS", "GEERT", "CWXT", "ACP", "DES", "RSGP", "PLNC", "ZNE",
        "CRT", "LIR", "OS76", "VOLT", "OFF", "CRDNC", "TOR", "ALTC", "SDP",
        "AGLC", "XOC", "XRC", "IBANK", "BIOB", "P7C", "COUPE", "ELS", "SOCC",
        "NODC", "CREVA", "MGM", "ULA", "SLFI", "CTIC2", "NANOX", "GSR",
        "LVPS", "CALC", "TYCHO", "DGCS", "TSTR", "PIZZA", "ABN", "EBT",
        "HT", "ATMC", "ELA", "OC", "WIC", "BCD", "CHAT", "W3C", "LBTC",
        "FRGC", "XTZ", "OCC", "BTCP", "OF", "XIN", "BSR", "BCX", "MLM",
        "SBTC", "BOS", "WC", "TER", "UBTC", "FIL", "$PAC", "LCC", "CLUB",
        "MSD", "ADK", "SWTC", "B2X", "MGC", "SBC", "NMS", "EAG", "SIC",
        "THS", "JIYO", "TMC", "IFC", "ENT", "TOK", "PCS", "GBG", "ACC",
        "BCA", "WA", "ANI", "XID", "JEW", "BT2", "VASH", "BIT", "TOKEN",
        "GMX", "GOD", "SPK", "VULC", "WOW", "CSC", "HC", "DAV", "ACES",
        "XRY", "SFE", "XQN", "EDRC", "ZBC", "FRN", "LEVO", "LEPEN", "SUP",
        "FONZ", "CYDER", "TCOIN", "CRYPT", "ROYAL", "DMC", "BAT", "SHA",
        "FLAP", "SLOTH", "WSX", "BIRDS", "BLAZR", "HIGH", "GRN", "GDC",
        "RBBT", "TOP", "RUNNERS", "ANTX", "MUSE", "UNRC", "ACN", "RICHX",
        "SKR", "PRN", "DON", "INDIA", "REGA", "XSTC", "KDC", "FID", "MARX",
        "XVE", "SJW", "LKC", "TURBO", "CMP", "TOPAZ", "APC", "GAIN",
        "ZSE", "LDCN", "NAMO", "PRIMU", "HNC", "NUMUS", "PAYP", "XTD", "BEST",
        "WINK", "AV", "SKULL", "BUB", "DCRE", "CME", "AKY", "UR", "GAY",
        "TELL", "HALLO", "FAZZ", "SIGMA", "SAK", "DUTCH", "SHELL", "MAGN",
        "OP", "HYPER", "BSN", "QBT", "CFC", "TODAY", "RUBIT", "POKE", "CHEAP",
        "DBG", "DASHS", "EGG", "OPES", "BET", "TEAM", "BAC", "NBIT", "MMXVI",
        "MONETA", "AXIOM", "MBL", "LTH", "FUTC", "BITOK", "BTBc", "SPORT",
        "CYC", "FRWC", "DUB", "GML", "CC", "VOYA", "QORA", "KARMA", "XAU",
        "TRICK", "IVZ", "X2", "PSY", "TCR", "DISK", "PRM", "HCC", "OMC",
        "LAZ", "RCN", "YES", "PDG", "KASHH", "RHFC", "TLE", "ASN", "UNC",
        "OCOW", "INF", "FRCT",
    ]

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of curreny_getter_interface"""
        if main_currency not in self.allowed_base_currencies:
            raise Exception('Company currency %s is not allowed in '
                            'CoinMarketCap service ' % main_currency)
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        url = CMC_URL_PREFIX + main_currency
        for curr in currency_array:
            rawfile = self.get_url(url)
            rawfile_str = str(rawfile, 'utf-8')
            vals = json.loads(rawfile_str)
            main_currency_attr = ("price_" + main_currency).lower()
            if not vals:
                raise Exception('Could not fetch values for main currency '
                                '%s.' % main_currency)
            for val in vals:
                if main_currency_attr not in val.keys():
                    raise Exception('Attribute %s not found.' %
                                    main_currency_attr)
                if val['symbol'] == curr:
                    try:
                        self.updated_currency[curr] = \
                            1.0 / float(val[main_currency_attr])

                    except ZeroDivisionError as e:
                        raise Exception(
                            'Cannot convert a price for %s that is '
                            'zero.' % main_currency)
            if curr not in self.updated_currency:
                raise Exception('Could not fetch values for main '
                                'currency %s and crypto currency %s.' %
                                (main_currency, curr))
        return self.updated_currency, self.log_info
