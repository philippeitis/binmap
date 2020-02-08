import binmap
import pytest
import struct


@pytest.fixture
def create_temp_class():
    class Temp(binmap.Binmap):
        _datafields = {"temp": "B"}

    return Temp


@pytest.fixture
def create_temp_hum_class():
    class TempHum(binmap.Binmap):
        _datafields = {"temp": "B", "humidity": "B"}

    return TempHum


def test_baseclass():
    b = binmap.Binmap()
    assert type(b) == binmap.Binmap


def test_baseclass_with_keyword():
    with pytest.raises(TypeError) as excinfo:
        binmap.Binmap(temp=10)
    assert "got an unexpected keyword argument 'temp'" in str(excinfo)


def test_different_classes_eq(create_temp_class, create_temp_hum_class):
    t = create_temp_class(temp=10)
    th = create_temp_hum_class(temp=10, humidity=60)
    assert t != th
    assert t.temp == th.temp


class TestTempClass:
    def test_with_argument(self, create_temp_class):
        t = create_temp_class(temp=10)
        assert t.temp == 10

    def test_without_argument(self, create_temp_class):
        t = create_temp_class()
        assert t.temp == 0
        assert t.binarydata == struct.pack("B", 0)

    def test_unknown_argument(self, create_temp_class):
        with pytest.raises(TypeError) as excinfo:
            create_temp_class(hum=60)
        assert "got an unexpected keyword argument 'hum'" in str(excinfo)

    def test_value(self, create_temp_class):
        t = create_temp_class()
        t.temp = 10
        assert t.binarydata == struct.pack("B", 10)

    def test_raw(self, create_temp_class):
        t = create_temp_class(binarydata=struct.pack("B", 10))
        assert t.temp == 10

    def test_change_value(self, create_temp_class):
        t = create_temp_class(temp=10)
        assert t.binarydata == struct.pack("B", 10)

        t.temp = 20
        assert t.binarydata == struct.pack("B", 20)

    def test_value_bounds(self, create_temp_class):
        t = create_temp_class()
        with pytest.raises(struct.error) as excinfo:
            t.temp = 256
        assert "ubyte format requires 0 <= number <= 255" in str(excinfo)

        with pytest.raises(struct.error) as excinfo:
            t.temp = -1
        assert "ubyte format requires 0 <= number <= 255" in str(excinfo)

    def test_compare_equal(self, create_temp_class):
        t1 = create_temp_class(temp=10)
        t2 = create_temp_class(temp=10)
        assert t1.temp == t2.temp
        assert t1 == t2

    def test_compare_not_equal(self, create_temp_class):
        t1 = create_temp_class(temp=10)
        t2 = create_temp_class(temp=20)
        assert t1.temp != t2.temp
        assert t1 != t2


class TestTempHumClass:
    def test_with_argument(self, create_temp_hum_class):
        th = create_temp_hum_class(temp=10, humidity=60)
        assert th.temp == 10
        assert th.humidity == 60

    def test_without_argument(self, create_temp_hum_class):
        th = create_temp_hum_class()
        assert th.temp == 0
        assert th.humidity == 0
        assert th.binarydata == struct.pack("BB", 0, 0)

    def test_raw(self, create_temp_hum_class):
        th = create_temp_hum_class(binarydata=struct.pack("BB", 10, 70))
        assert th.temp == 10
        assert th.humidity == 70

    def test_change_values(self, create_temp_hum_class):
        th = create_temp_hum_class(temp=10, humidity=70)
        th.temp = 30
        th.humidity = 30
        assert th.temp == 30
        assert th.humidity == 30
        assert th.binarydata == struct.pack("BB", 30, 30)

    def test_compare_equal(self, create_temp_hum_class):
        th1 = create_temp_hum_class(temp=10, humidity=70)
        th2 = create_temp_hum_class(temp=10, humidity=70)
        assert th1.temp == th2.temp
        assert th1 == th2

    def test_compare_not_equal(self, create_temp_hum_class):
        th1 = create_temp_hum_class(temp=10, humidity=70)
        th2 = create_temp_hum_class(temp=20, humidity=60)
        th3 = create_temp_hum_class(temp=10, humidity=60)
        th4 = create_temp_hum_class(temp=20, humidity=70)
        assert (th1.temp != th2.temp) and (th1.humidity != th2.humidity)
        assert th1 != th2
        assert th1 != th3
        assert th1 != th4
        assert th2 != th3
        assert th2 != th4
