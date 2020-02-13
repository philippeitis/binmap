import binmap
import pytest
import struct


def test_baseclass():
    b = binmap.Binmap()
    assert type(b) == binmap.Binmap


def test_baseclass_with_keyword():
    with pytest.raises(TypeError) as excinfo:
        binmap.Binmap(temp=10)
    assert "got an unexpected keyword argument 'temp'" in str(excinfo)


class Temp(binmap.Binmap):
    _datafields = {"temp": "B"}


class TempHum(binmap.Binmap):
    _datafields = {"temp": "B", "humidity": "B"}


def test_different_classes_eq():
    t = Temp(temp=10)
    th = TempHum(temp=10, humidity=60)
    assert t != th
    assert t.temp == th.temp


class TestTempClass:
    def test_with_argument(self):
        t = Temp(temp=10)
        assert t.temp == 10

    def test_without_argument(self):
        t = Temp()
        assert t.temp == 0
        assert t.binarydata == struct.pack("B", 0)

    def test_unknown_argument(self):
        with pytest.raises(TypeError) as excinfo:
            Temp(hum=60)
        assert "got an unexpected keyword argument 'hum'" in str(excinfo)

    def test_value(self):
        t = Temp()
        t.temp = 10
        assert t.binarydata == struct.pack("B", 10)

    def test_raw(self):
        t = Temp(binarydata=struct.pack("B", 10))
        assert t.temp == 10

    def test_update_binarydata(self):
        t = Temp(binarydata=struct.pack("B", 10))
        assert t.temp == 10
        t.binarydata = struct.pack("B", 20)
        assert t.temp == 20

    def test_change_value(self):
        t = Temp(temp=10)
        assert t.binarydata == struct.pack("B", 10)

        t.temp = 20
        assert t.binarydata == struct.pack("B", 20)

    def test_value_bounds(self):
        t = Temp()
        with pytest.raises(struct.error) as excinfo:
            t.temp = 256
        assert "ubyte format requires 0 <= number <= 255" in str(excinfo)

        with pytest.raises(struct.error) as excinfo:
            t.temp = -1
        assert "ubyte format requires 0 <= number <= 255" in str(excinfo)

    def test_compare_equal(self):
        t1 = Temp(temp=10)
        t2 = Temp(temp=10)
        assert t1.temp == t2.temp
        assert t1 == t2

    def test_compare_not_equal(self):
        t1 = Temp(temp=10)
        t2 = Temp(temp=20)
        assert t1.temp != t2.temp
        assert t1 != t2


class TestTempHumClass:
    def test_with_argument(self):
        th = TempHum(temp=10, humidity=60)
        assert th.temp == 10
        assert th.humidity == 60

    def test_without_argument(self):
        th = TempHum()
        assert th.temp == 0
        assert th.humidity == 0
        assert th.binarydata == struct.pack("BB", 0, 0)

    def test_raw(self):
        th = TempHum(binarydata=struct.pack("BB", 10, 70))
        assert th.temp == 10
        assert th.humidity == 70

    def test_change_values(self):
        th = TempHum(temp=10, humidity=70)
        th.temp = 30
        th.humidity = 30
        assert th.temp == 30
        assert th.humidity == 30
        assert th.binarydata == struct.pack("BB", 30, 30)

    def test_compare_equal(self):
        th1 = TempHum(temp=10, humidity=70)
        th2 = TempHum(temp=10, humidity=70)
        assert th1.temp == th2.temp
        assert th1 == th2

    def test_compare_not_equal(self):
        th1 = TempHum(temp=10, humidity=70)
        th2 = TempHum(temp=20, humidity=60)
        th3 = TempHum(temp=10, humidity=60)
        th4 = TempHum(temp=20, humidity=70)
        assert (th1.temp != th2.temp) and (th1.humidity != th2.humidity)
        assert th1 != th2
        assert th1 != th3
        assert th1 != th4
        assert th2 != th3
        assert th2 != th4


class Pad(binmap.Binmap):
    _datafields = {"temp": "B", "_pad1": "xx", "humidity": "B"}


class AdvancedPad(binmap.Binmap):
    _datafields = {
        "temp": "B",
        "_pad1": "xx",
        "humidity": "B",
        "_pad2": "3x",
        "_pad3": "x",
    }


class TestPadClass:
    def test_create_pad(self):
        p = Pad(temp=10, humidity=60)
        assert p.temp == 10
        with pytest.raises(AttributeError) as excinfo:
            p._pad1
        assert "Padding (_pad1) is not readable" in str(excinfo)
        assert p.humidity == 60

    def test_parse_data(self):
        p = Pad(binarydata=struct.pack("BxxB", 10, 60))
        assert p.temp == 10
        with pytest.raises(AttributeError) as excinfo:
            p._pad1
        assert "Padding (_pad1) is not readable" in str(excinfo)
        assert p.humidity == 60

    def test_pack_data(self):
        p = Pad()
        p.temp = 10
        p.humidity = 60
        assert p.binarydata == struct.pack("BxxB", 10, 60)

    def test_advanced_pad(self):
        p = AdvancedPad(temp=10, humidity=60)
        assert p.temp == 10
        assert p.humidity == 60
        with pytest.raises(AttributeError) as excinfo:
            p._pad1
        assert "Padding (_pad1) is not readable" in str(excinfo)
        with pytest.raises(AttributeError) as excinfo:
            p._pad2
        assert "Padding (_pad2) is not readable" in str(excinfo)
        with pytest.raises(AttributeError) as excinfo:
            p._pad3
        assert "Padding (_pad3) is not readable" in str(excinfo)

    def test_advanced_parse_data(self):
        p = AdvancedPad(binarydata=struct.pack("BxxB4x", 10, 60))
        assert p.temp == 10
        with pytest.raises(AttributeError) as excinfo:
            p._pad1
        assert "Padding (_pad1) is not readable" in str(excinfo)
        assert p.humidity == 60

    def test_advanced_pack_data(self):
        p = AdvancedPad()
        p.temp = 10
        p.humidity = 60
        assert p.binarydata == struct.pack("BxxB4x", 10, 60)


class Property(binmap.Binmap):
    _datafields = {
        "temp": "B",
        "wind": "B",
    }

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @property
    def winddirection(self):
        if self.wind == Property.NORTH:
            return "North"
        if self.wind == Property.EAST:
            return "East"
        if self.wind == Property.SOUTH:
            return "South"
        if self.wind == Property.WEST:
            return "West"

    @winddirection.setter
    def winddirection(self, value):
        if isinstance(value, str):
            if value.lower() == "north":
                self.wind = Property.NORTH
            elif value.lower() == "east":
                self.wind = Property.EAST
            elif value.lower() == "south":
                self.wind = Property.SOUTH
            elif value.lower() == "west":
                self.wind = Property.WEST
            else:
                raise ValueError("Unknown direction")
        elif isinstance(value, int):
            self.wind = value
        else:
            raise ValueError("Unknown direction")


class TestPropertyClass:
    def test_create_class(self):
        pc = Property()
        assert pc

    def test_get_wind(self):
        pc = Property(temp=10, wind=2)
        assert pc.winddirection == "South"

    def test_wind_binary(self):
        pc = Property(binarydata=struct.pack("BB", 10, 2))
        assert pc.wind == Property.SOUTH
        assert pc.winddirection == "South"

    def test_set_named_wind(self):
        pc = Property()
        pc.winddirection = "South"
        assert pc.wind == Property.SOUTH

        with pytest.raises(ValueError) as excinfo:
            pc.winddirection = "Norhtwest"
        assert "Unknown direction" in str(excinfo)

        with pytest.raises(ValueError) as excinfo:
            pc.winddirection = 1.2
        assert "Unknown direction" in str(excinfo)


class AllDatatypes(binmap.Binmap):
    _datafields = {
        "_pad": "x",
        "char": "c",
        "signedchar": "b",
        "unsignedchar": "B",
        "boolean": "?",
        "short": "h",
        "unsignedshort": "H",
        "integer": "i",
        "unsignedint": "I",
        "long": "l",
        "unsignedlong": "L",
        "longlong": "q",
        "unsignedlonglong": "Q",
        "ssize_t": "n",
        "size_t": "N",
        "halffloat": "e",
        "floating": "f",
        "double": "d",
        "string": "10s",
        "pascalstring": "15p",
        "pointer": "P",
    }


class TestAllDatatypes:
    def test_create_class(self):
        sc = AllDatatypes()
        assert sc

    def test_with_arguments(self):
        sc = AllDatatypes(
            char=b"%",
            signedchar=-2,
            unsignedchar=5,
            boolean=True,
            short=-7,
            unsignedshort=17,
            integer=-15,
            unsignedint=11,
            long=-2312,
            unsignedlong=2212,
            longlong=-1212,
            unsignedlonglong=4444,
            ssize_t=15,
            size_t=22,
            halffloat=3.5,
            floating=3e3,
            double=13e23,
            string=b"helloworld",
            pascalstring=b"hello pascal",
            pointer=0xFCE2,
        )
        assert sc.char == b"%"
        assert sc.signedchar == -2
        assert sc.unsignedchar == 5
        assert sc.boolean
        assert sc.short == -7
        assert sc.unsignedshort == 17
        assert sc.integer == -15
        assert sc.unsignedint == 11
        assert sc.long == -2312
        assert sc.unsignedlong == 2212
        assert sc.longlong == -1212
        assert sc.unsignedlonglong == 4444
        assert sc.ssize_t == 15
        assert sc.size_t == 22
        assert sc.halffloat == 3.5
        assert sc.floating == 3e3
        assert sc.double == 13e23
        assert sc.string == b"helloworld"
        assert sc.pascalstring == b"hello pascal"
        assert sc.pointer == 0xFCE2
        assert (
            sc.binarydata
            == b"\x00%\xfe\x05\x01\x00\xf9\xff\x11\x00\x00\x00\xf1\xff\xff\xff\x0b\x00\x00\x00\x00\x00\x00\x00\xf8\xf6\xff\xff\xff\xff\xff\xff\xa4\x08"
            b"\x00\x00\x00\x00\x00\x00D\xfb\xff\xff\xff\xff\xff\xff\\\x11\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\x00"
            b"\x00\x00\x00C\x00\x00\x00\x80;E\xe8\x0cgB\x924\xf1Dhelloworld\x0chello pascal\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe2\xfc\x00\x00\x00\x00\x00\x00"
        )

    def test_with_binarydata(self):
        sc = AllDatatypes(
            binarydata=b"\x0fW\xee\x15\x00\x00\xf9\xf4\x11\x10\x00\x00\x31\xff\xff\xff\x0b\x01\x00\x00\x00\x00\x00\x00"
            b"\xf8\xe6\xff\xff\xff\xff\xff\xff\xa4\x18\x00\x00\x00\x00\x00\x00E\xfb\xff\xff\xff\xff\xff\xff\\\x11\x01"
            b"\x00\x00\x00\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x26\x00\x00\x00\x00\x00\x00"
            b"\x00\x01C\x00\x00\x00\x81;E\xe8\x0cgB\xa24\xf1Dhi world  \x09hi pascal\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe3\xfc\x00\x00\x00\x00\x00\x00"
        )
        assert sc.char == b"W"
        assert sc.signedchar == -18
        assert sc.unsignedchar == 21
        assert not sc.boolean
        assert sc.short == -2823
        assert sc.unsignedshort == 4113
        assert sc.integer == -207
        assert sc.unsignedint == 267
        assert sc.long == -6408
        assert sc.unsignedlong == 6308
        assert sc.longlong == -1211
        assert sc.unsignedlonglong == 69980
        assert sc.ssize_t == 31
        assert sc.size_t == 38
        assert sc.halffloat == 3.501953125
        assert sc.floating == 3000.0625
        assert sc.double == 1.3000184467440736e24
        assert sc.string == b"hi world  "
        assert sc.pascalstring == b"hi pascal"
        assert sc.pointer == 0xFCE3
