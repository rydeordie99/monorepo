CP_DELIVERED = (
    20,
    21,
    1421,
    1422,
    1423,
    1424,
    1425,
    1426,
    1427,
    1428,
    1429,
    1430,
    1431,
    1432,
    1433,
    1434,
    1441,
    1442,
    1496,
    1497,
    1498,
    1499,
    2001,
)
NA = "N/A"

PUROLATOR_START = """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:v1="http://purolator.com/pws/datatypes/v1">
<soapenv:Header>
    <v1:RequestContext>
        <v1:Version>1.2</v1:Version>
        <v1:Language>en</v1:Language>
        <v1:GroupID>x</v1:GroupID>
        <v1:RequestReference>soapui</v1:RequestReference>
        <v1:UserToken>x</v1:UserToken>
    </v1:RequestContext>
</soapenv:Header>
<soapenv:Body>
    <v1:TrackPackagesByPinRequest>
        <v1:PINs>
            <!--Zero or more repetitions:-->
            <v1:PIN>
            <v1:Value>"""

PUROLATOR_END = """</v1:Value>
            </v1:PIN>
        </v1:PINs>
    </v1:TrackPackagesByPinRequest>
</soapenv:Body>
</soapenv:Envelope>"""
