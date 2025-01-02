import random
from enum import Enum, EnumMeta, auto, unique


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            try:
                cls[item]
            except KeyError:
                return False
        return True


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (
        len(name) > 4
        and name[:2] == name[-2:] == "__"
        and name[2] != "_"
        and name[-3] != "_"
    )


class StrMetaEnum(MetaEnum):
    def __getitem__(cls, name: str):
        if name in cls._member_map_:
            return cls._member_map_[name]
        return name

    def __getattr__(cls, name: str):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        if _is_dunder(name):
            raise AttributeError(name)
        if name in cls._member_map_:
            try:
                return cls._member_map_[name]
            except KeyError:
                raise AttributeError(name) from None
        return name


class IntEnum(int, Enum, metaclass=MetaEnum):
    pass


class StrEnum(str, Enum, metaclass=StrMetaEnum):
    def __str__(self) -> str:
        return self.name

    def _generate_next_value_(name, start, count, last_values):
        return name


class ColorEnum(tuple, Enum, metaclass=MetaEnum):
    pass


@unique
class ParameterTypes(IntEnum):
    """data type enum"""

    _None = 0
    Bool = 1
    Int = 2
    Float = 3
    Vector = 4
    String = 5
    FloatArray = 6
    ByteArray = 7
    Json = 8
    Rotator = 9
    Max = 255


@unique
class MusicNotes(StrEnum):
    """names musical notes"""

    C1 = auto()
    Db1 = auto()
    D1 = auto()
    Eb1 = auto()
    E1 = auto()
    F1 = auto()
    Gb1 = auto()
    G1 = auto()
    Ab1 = auto()
    A1 = auto()
    Bb1 = auto()
    B1 = auto()
    C2 = auto()
    Db2 = auto()
    D2 = auto()
    Eb2 = auto()
    E2 = auto()
    F2 = auto()
    Gb2 = auto()
    G2 = auto()
    Ab2 = auto()
    A2 = auto()
    Bb2 = auto()
    B2 = auto()
    C3 = auto()
    Db3 = auto()
    D3 = auto()
    Eb3 = auto()
    E3 = auto()
    F3 = auto()
    Gb3 = auto()
    G3 = auto()
    Ab3 = auto()
    A3 = auto()
    Bb3 = auto()
    B3 = auto()
    C4 = auto()
    Db4 = auto()
    D4 = auto()
    Eb4 = auto()
    E4 = auto()
    F4 = auto()
    Gb4 = auto()
    G4 = auto()
    Ab4 = auto()
    A4 = auto()
    Bb4 = auto()
    B4 = auto()
    C5 = auto()
    Db5 = auto()
    D5 = auto()
    Eb5 = auto()
    E5 = auto()
    F5 = auto()
    Gb5 = auto()
    G5 = auto()
    Ab5 = auto()
    A5 = auto()
    Bb5 = auto()
    B5 = auto()
    C6 = auto()
    Db6 = auto()
    D6 = auto()
    Eb6 = auto()
    E6 = auto()
    F6 = auto()
    Gb6 = auto()
    G6 = auto()
    Ab6 = auto()
    A6 = auto()
    Bb6 = auto()
    B6 = auto()
    C7 = auto()
    Db7 = auto()
    D7 = auto()
    Eb7 = auto()
    E7 = auto()
    F7 = auto()
    Gb7 = auto()
    G7 = auto()
    Ab7 = auto()
    A7 = auto()
    Bb7 = auto()
    B7 = auto()
    Cs1 = auto()
    Ds1 = auto()
    Fs1 = auto()
    Gs1 = auto()
    As1 = auto()
    Cs2 = auto()
    Ds2 = auto()
    Fs2 = auto()
    Gs2 = auto()
    As2 = auto()
    Cs3 = auto()
    Ds3 = auto()
    Fs3 = auto()
    Gs3 = auto()
    As3 = auto()
    Cs4 = auto()
    Ds4 = auto()
    Fs4 = auto()
    Gs4 = auto()
    As4 = auto()
    Cs5 = auto()
    Ds5 = auto()
    Fs5 = auto()
    Gs5 = auto()
    As5 = auto()
    Cs6 = auto()
    Ds6 = auto()
    Fs6 = auto()
    Gs6 = auto()
    As6 = auto()
    Cs7 = auto()
    Ds7 = auto()
    Fs7 = auto()
    Gs7 = auto()
    As7 = auto()


class Colors(ColorEnum):
    """Named css colors as RGB tuples"""

    Aliceblue = (0.9411764705882353, 0.9725490196078431, 1.0)
    Antiquewhite = (0.9803921568627451, 0.9215686274509803, 0.8431372549019608)
    Aqua = (0.0, 1.0, 1.0)
    Aquamarine = (0.4980392156862745, 1.0, 0.8313725490196079)
    Azure = (0.9411764705882353, 1.0, 1.0)
    Beige = (0.9607843137254902, 0.9607843137254902, 0.8627450980392157)
    Bisque = (1.0, 0.8941176470588236, 0.7686274509803922)
    Black = (0.0, 0.0, 0.0)
    Blanchedalmond = (1.0, 0.9215686274509803, 0.803921568627451)
    Blue = (0.0, 0.0, 1.0)
    Blueviolet = (0.5411764705882353, 0.16862745098039217, 0.8862745098039215)
    Brown = (0.6470588235294118, 0.16470588235294117, 0.16470588235294117)
    Burlywood = (0.8705882352941177, 0.7215686274509804, 0.5294117647058824)
    Cadetblue = (0.37254901960784315, 0.6196078431372549, 0.6274509803921569)
    Chartreuse = (0.4980392156862745, 1.0, 0.0)
    Chocolate = (0.8235294117647058, 0.4117647058823529, 0.11764705882352941)
    Coral = (1.0, 0.4980392156862745, 0.3137254901960784)
    Cornflowerblue = (0.39215686274509803, 0.5843137254901961, 0.9294117647058824)
    Cornsilk = (1.0, 0.9725490196078431, 0.8627450980392157)
    Crimson = (0.8627450980392157, 0.0784313725490196, 0.23529411764705882)
    Cyan = (0.0, 1.0, 1.0)
    Darkblue = (0.0, 0.0, 0.5450980392156862)
    Darkcyan = (0.0, 0.5450980392156862, 0.5450980392156862)
    Darkgoldenrod = (0.7215686274509804, 0.5254901960784314, 0.043137254901960784)
    Darkgray = (0.6627450980392157, 0.6627450980392157, 0.6627450980392157)
    Darkgreen = (0.0, 0.39215686274509803, 0.0)
    Darkgrey = (0.6627450980392157, 0.6627450980392157, 0.6627450980392157)
    Darkkhaki = (0.7411764705882353, 0.7176470588235294, 0.4196078431372549)
    Darkmagenta = (0.5450980392156862, 0.0, 0.5450980392156862)
    Darkolivegreen = (0.3333333333333333, 0.4196078431372549, 0.1843137254901961)
    Darkorange = (1.0, 0.5490196078431373, 0.0)
    Darkorchid = (0.6, 0.19607843137254902, 0.8)
    Darkred = (0.5450980392156862, 0.0, 0.0)
    Darksalmon = (0.9137254901960784, 0.5882352941176471, 0.47843137254901963)
    Darkseagreen = (0.5607843137254902, 0.7372549019607844, 0.5607843137254902)
    Darkslateblue = (0.2823529411764706, 0.23921568627450981, 0.5450980392156862)
    Darkslategray = (0.1843137254901961, 0.30980392156862746, 0.30980392156862746)
    Darkslategrey = (0.1843137254901961, 0.30980392156862746, 0.30980392156862746)
    Darkturquoise = (0.0, 0.807843137254902, 0.8196078431372549)
    Darkviolet = (0.5803921568627451, 0.0, 0.8274509803921568)
    Deeppink = (1.0, 0.0784313725490196, 0.5764705882352941)
    Deepskyblue = (0.0, 0.7490196078431373, 1.0)
    Dimgray = (0.4117647058823529, 0.4117647058823529, 0.4117647058823529)
    Dimgrey = (0.4117647058823529, 0.4117647058823529, 0.4117647058823529)
    Dodgerblue = (0.11764705882352941, 0.5647058823529412, 1.0)
    Firebrick = (0.6980392156862745, 0.13333333333333333, 0.13333333333333333)
    Floralwhite = (1.0, 0.9803921568627451, 0.9411764705882353)
    Forestgreen = (0.13333333333333333, 0.5450980392156862, 0.13333333333333333)
    Fuchsia = (1.0, 0.0, 1.0)
    Gainsboro = (0.8627450980392157, 0.8627450980392157, 0.8627450980392157)
    Ghostwhite = (0.9725490196078431, 0.9725490196078431, 1.0)
    Goldenrod = (0.8549019607843137, 0.6470588235294118, 0.12549019607843137)
    Gold = (1.0, 0.8431372549019608, 0.0)
    Gray = (0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
    Green = (0.0, 0.5019607843137255, 0.0)
    Greenyellow = (0.6784313725490196, 1.0, 0.1843137254901961)
    Grey = (0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
    Honeydew = (0.9411764705882353, 1.0, 0.9411764705882353)
    Hotpink = (1.0, 0.4117647058823529, 0.7058823529411765)
    Indianred = (0.803921568627451, 0.3607843137254902, 0.3607843137254902)
    Indigo = (0.29411764705882354, 0.0, 0.5098039215686274)
    Ivory = (1.0, 1.0, 0.9411764705882353)
    Khaki = (0.9411764705882353, 0.9019607843137255, 0.5490196078431373)
    Lavenderblush = (1.0, 0.9411764705882353, 0.9607843137254902)
    Lavender = (0.9019607843137255, 0.9019607843137255, 0.9803921568627451)
    Lawngreen = (0.48627450980392156, 0.9882352941176471, 0.0)
    Lemonchiffon = (1.0, 0.9803921568627451, 0.803921568627451)
    Lightblue = (0.6784313725490196, 0.8470588235294118, 0.9019607843137255)
    Lightcoral = (0.9411764705882353, 0.5019607843137255, 0.5019607843137255)
    Lightcyan = (0.8784313725490196, 1.0, 1.0)
    Lightgoldenrodyellow = (0.9803921568627451, 0.9803921568627451, 0.8235294117647058)
    Lightgray = (0.8274509803921568, 0.8274509803921568, 0.8274509803921568)
    Lightgreen = (0.5647058823529412, 0.9333333333333333, 0.5647058823529412)
    Lightgrey = (0.8274509803921568, 0.8274509803921568, 0.8274509803921568)
    Lightpink = (1.0, 0.7137254901960784, 0.7568627450980392)
    Lightsalmon = (1.0, 0.6274509803921569, 0.47843137254901963)
    Lightseagreen = (0.12549019607843137, 0.6980392156862745, 0.6666666666666666)
    Lightskyblue = (0.5294117647058824, 0.807843137254902, 0.9803921568627451)
    Lightslategray = (0.4666666666666667, 0.5333333333333333, 0.6)
    Lightslategrey = (0.4666666666666667, 0.5333333333333333, 0.6)
    Lightsteelblue = (0.6901960784313725, 0.7686274509803922, 0.8705882352941177)
    Lightyellow = (1.0, 1.0, 0.8784313725490196)
    Lime = (0.0, 1.0, 0.0)
    Limegreen = (0.19607843137254902, 0.803921568627451, 0.19607843137254902)
    Linen = (0.9803921568627451, 0.9411764705882353, 0.9019607843137255)
    Magenta = (1.0, 0.0, 1.0)
    Maroon = (0.5019607843137255, 0.0, 0.0)
    Mediumaquamarine = (0.4, 0.803921568627451, 0.6666666666666666)
    Mediumblue = (0.0, 0.0, 0.803921568627451)
    Mediumorchid = (0.7294117647058823, 0.3333333333333333, 0.8274509803921568)
    Mediumpurple = (0.5764705882352941, 0.4392156862745098, 0.8588235294117647)
    Mediumseagreen = (0.23529411764705882, 0.7019607843137254, 0.44313725490196076)
    Mediumslateblue = (0.4823529411764706, 0.40784313725490196, 0.9333333333333333)
    Mediumspringgreen = (0.0, 0.9803921568627451, 0.6039215686274509)
    Mediumturquoise = (0.2823529411764706, 0.8196078431372549, 0.8)
    Mediumvioletred = (0.7803921568627451, 0.08235294117647059, 0.5215686274509804)
    Midnightblue = (0.09803921568627451, 0.09803921568627451, 0.4392156862745098)
    Mintcream = (0.9607843137254902, 1.0, 0.9803921568627451)
    Mistyrose = (1.0, 0.8941176470588236, 0.8823529411764706)
    Moccasin = (1.0, 0.8941176470588236, 0.7098039215686275)
    Navajowhite = (1.0, 0.8705882352941177, 0.6784313725490196)
    Navy = (0.0, 0.0, 0.5019607843137255)
    Oldlace = (0.9921568627450981, 0.9607843137254902, 0.9019607843137255)
    Olive = (0.5019607843137255, 0.5019607843137255, 0.0)
    Olivedrab = (0.4196078431372549, 0.5568627450980392, 0.13725490196078433)
    Orange = (1.0, 0.6470588235294118, 0.0)
    Orangered = (1.0, 0.27058823529411763, 0.0)
    Orchid = (0.8549019607843137, 0.4392156862745098, 0.8392156862745098)
    Palegoldenrod = (0.9333333333333333, 0.9098039215686274, 0.6666666666666666)
    Palegreen = (0.596078431372549, 0.984313725490196, 0.596078431372549)
    Paleturquoise = (0.6862745098039216, 0.9333333333333333, 0.9333333333333333)
    Palevioletred = (0.8588235294117647, 0.4392156862745098, 0.5764705882352941)
    Papayawhip = (1.0, 0.9372549019607843, 0.8352941176470589)
    Peachpuff = (1.0, 0.8549019607843137, 0.7254901960784313)
    Peru = (0.803921568627451, 0.5215686274509804, 0.24705882352941178)
    Pink = (1.0, 0.7529411764705882, 0.796078431372549)
    Plum = (0.8666666666666667, 0.6274509803921569, 0.8666666666666667)
    Powderblue = (0.6901960784313725, 0.8784313725490196, 0.9019607843137255)
    Purple = (0.5019607843137255, 0.0, 0.5019607843137255)
    Rebeccapurple = (0.4, 0.2, 0.6)
    Red = (1.0, 0.0, 0.0)
    Rosybrown = (0.7372549019607844, 0.5607843137254902, 0.5607843137254902)
    Royalblue = (0.2549019607843137, 0.4117647058823529, 0.8823529411764706)
    Saddlebrown = (0.5450980392156862, 0.27058823529411763, 0.07450980392156863)
    Salmon = (0.9803921568627451, 0.5019607843137255, 0.4470588235294118)
    Sandybrown = (0.9568627450980393, 0.6431372549019608, 0.3764705882352941)
    Seagreen = (0.1803921568627451, 0.5450980392156862, 0.3411764705882353)
    Seashell = (1.0, 0.9607843137254902, 0.9333333333333333)
    Sienna = (0.6274509803921569, 0.3215686274509804, 0.17647058823529413)
    Silver = (0.7529411764705882, 0.7529411764705882, 0.7529411764705882)
    Skyblue = (0.5294117647058824, 0.807843137254902, 0.9215686274509803)
    Slateblue = (0.41568627450980394, 0.35294117647058826, 0.803921568627451)
    Slategray = (0.4392156862745098, 0.5019607843137255, 0.5647058823529412)
    Slategrey = (0.4392156862745098, 0.5019607843137255, 0.5647058823529412)
    Snow = (1.0, 0.9803921568627451, 0.9803921568627451)
    Springgreen = (0.0, 1.0, 0.4980392156862745)
    Steelblue = (0.27450980392156865, 0.5098039215686274, 0.7058823529411765)
    Tan = (0.8235294117647058, 0.7058823529411765, 0.5490196078431373)
    Teal = (0.0, 0.5019607843137255, 0.5019607843137255)
    Thistle = (0.8470588235294118, 0.7490196078431373, 0.8470588235294118)
    Tomato = (1.0, 0.38823529411764707, 0.2784313725490196)
    Turquoise = (0.25098039215686274, 0.8784313725490196, 0.8156862745098039)
    Violet = (0.9333333333333333, 0.5098039215686274, 0.9333333333333333)
    Wheat = (0.9607843137254902, 0.8705882352941177, 0.7019607843137254)
    White = (1.0, 1.0, 1.0)
    Whitesmoke = (0.9607843137254902, 0.9607843137254902, 0.9607843137254902)
    Yellow = (1.0, 1.0, 0.0)
    Yellowgreen = (0.6039215686274509, 0.803921568627451, 0.19607843137254902)

    @staticmethod
    def random() -> tuple[float, float, float]:
        """Get a random RGB color."""
        return (random.random(), random.random(), random.random())


@unique
class ComparisonResult(IntEnum):
    """ComparisonResult enum for pair-wise comparisons between A and B resulting in A<B -> LessThan, A==B -> Equal, A>B -> GreaterThan"""

    LessThan = -1
    Equal = 0
    GreatherThan = 1


@unique
class WeatherScenario(IntEnum):
    """Different weather scenarios selectable in the level editor outdoor levels."""

    ClearSky = 0
    MediumClouded = 1
    Clouded = 2
    MediumRain = 3
    HeavyRain = 4
    ThunderRain = 5
    ThunderStorm = 6
    Foggy = 7


@unique
class CardSuit(IntEnum):
    Spades = 3
    Hearts = 2
    Diamonds = 1
    Clubs = 0


@unique
class CardRank(IntEnum):
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace = 14


@unique
class ElevatorState(StrEnum):
    """Current state of the elevator."""

    Unkown = auto()
    Idle = auto()
    Upwards = auto()
    Downwards = auto()


@unique
class MachineState(StrEnum):
    Unknown = auto()
    Idle = auto()
    Moving = auto()


class ArcadeButtons(StrEnum):
    """All possible buttons on an arcade machine"""

    Up = auto()
    Down = auto()
    Left = auto()
    Right = auto()
    LeftUp = auto()
    RightUp = auto()
    LeftDown = auto()
    RightDown = auto()
    A = auto()
    B = auto()
    X = auto()
    Y = auto()
    Menu = auto()


class ArcadeAxis(StrEnum):
    """All possible axes available on the arcade machine"""

    UpDown = auto()
    RightLeft = auto()
    SecondaryUpDown = auto()
    SecondaryRightLeft = auto()


class ArcadeGames(StrEnum):
    """All available games on the arcade machine"""

    Snak = auto()
    BlokOut = auto()


class TrafficLightStates(StrEnum):
    """Possible states of a traffic light"""

    Off = auto()
    Red = auto()
    RedYellow = auto()
    Yellow = auto()
    Green = auto()


@unique
class CameraType(IntEnum):
    RGB = 0
    Depth = 1
    OpticalFlow = 2
    Segmentation = 3
    ObjectDetector = 4


@unique
class GoalState(StrEnum):
    """GoalStates for level editor"""

    Open = auto()
    Success = auto()
    Fail = auto()
    Ignore = auto()
    Unknown = auto()


@unique
class SpawnableMaps(StrEnum):
    """Spawnable maps for the level editor"""

    MinimalisticIndoor = auto()
    ParkingLot = auto()
    DesertIsland = auto()
    CellarHallway = auto()
    SmartHome = auto()
    MuseumHall = auto()
    BrutalistHall = auto()
    MilitaryBase = auto()
    Bridge = auto()
    WineCellar = auto()
    SmallWarehouse = auto()
    MedievalCourtyard = auto()
    CpuWorld = auto()
    InfinitePlane = auto()
    GrasslandOutdoor = auto()


@unique
class SpawnableEntities(StrEnum):
    """entities which can be spawned in the level editor"""

    # AirstrikeControl=auto()
    ArcadeMachine = auto()
    Artillery = auto()
    # CarvingRobot=auto()
    # ColorCubePuzzle=auto()
    ConveyorBelt = auto()
    DataExchange = auto()
    Deliverable = auto()
    ObjectSpawner = auto()
    DeliveryContainer = auto()
    DialupPhone = auto()
    # Elevator=auto()
    GPSWaypoint = auto()
    # GunTurret=auto()
    HumanoidRobot = auto()
    InputBox = auto()
    Killzone = auto()
    LEDStrip = auto()
    LargeConveyorBelt = auto()
    LaunchPad = auto()
    Maze = auto()
    MovablePlatform = auto()
    # PaintableCanvas=auto()
    Piano = auto()
    PinHacker = auto()
    # PlanarRobotCrane=auto()
    # PoolTable=auto()
    PullerRobot = auto()
    PushButton = auto()
    PusherRobot = auto()
    # RadarTrap=auto()
    # RailConveyorBelt=auto()
    RangeFinder = auto()
    RemoteExplosive = auto()
    RobotArm = auto()
    ServiceDrone = auto()
    Slider = auto()
    SmartCamera = auto()
    SmartDoor = auto()
    SmartLiDAR = auto()
    SmartPointLight = auto()
    SmartSpotLight = auto()
    SmartPictureFrame = auto()
    SmartPortal = auto()
    SmartRadar = auto()
    SmartSpeaker = auto()
    SmartTracker = auto()
    SmartWall = auto()
    SniperRifle = auto()
    ToggleSwitch = auto()
    # TrafficLight=auto()
    TriggerZone = auto()
    TurnableConveyorBelt = auto()
    # VacuumRobot=auto()
    VoxelBuilder = auto()
    AirliftCrane = auto()
    PlayingCard = auto()
    DigitalScale = auto()
    AlarmClock = auto()
    SimplePhysicsCar = auto()
    RaceCar = auto()
    # PostProcessVolume=auto()
    ProximitySensor = auto()
    AlarmSiren = auto()
    SurveillanceSatellite = auto()


@unique
class SpawnableMeshes(StrEnum):
    """meshes which can be spawned in the level editor"""

    Cube = auto()
    Sphere = auto()
    Plane = auto()
    Cylinder = auto()
    Cone = auto()
    BarrelRed = auto()
    BarrelGreen = auto()
    CardboardBox = auto()
    PalletBoxOpen = auto()
    PalletBoxLid = auto()
    Dumpster = auto()
    TireWheel = auto()
    CogWheel = auto()
    SignStop = auto()
    SignDanger = auto()
    TrafficCone = auto()
    SignRadioactive = auto()
    Ladder = auto()
    SignExit = auto()
    Ramp = auto()
    TrussingHigh = auto()
    Trussing200 = auto()
    TrussingCrossing = auto()
    ConcreteBarrier = auto()
    SandBarrier = auto()
    FenceLarge = auto()
    Shelf = auto()
    Door = auto()
    BarbedWire = auto()
    Goldbar = auto()
    CoinEuro1 = auto()
    CoinEuro2 = auto()
    CoinEuroCent1 = auto()
    CoinEuroCent2 = auto()
    CoinEuroCent5 = auto()
    CoinEuroCent10 = auto()
    CoinEuroCent20 = auto()
    CoinEuroCent50 = auto()
    BankNoteEuro5 = auto()
    BankNoteEuro10 = auto()
    BankNoteEuro20 = auto()
    BankNoteEuro50 = auto()
    BankNoteEuro100 = auto()
    Anvil = auto()
    SmallFence = auto()
    Torus = auto()
    Bag = auto()
    Hat1 = auto()
    PaintingWide = auto()
    Flower1 = auto()
    Flower2 = auto()
    Flower3 = auto()
    FlowerPot = auto()
    Bench = auto()
    Chair = auto()
    OfficeChair = auto()
    Table = auto()
    TableRound = auto()
    Postbox = auto()
    Bottle1 = auto()
    Bottle2 = auto()
    Bottle3 = auto()
    WoodenBox = auto()


@unique
class VerbosityLevels(IntEnum):
    """Verbosity level of the pyjop interface. Higher values mean more verbose information."""

    Critical = 0
    """Basically nothing gets printed to the log window. Use with caution, you might miss important information."""
    Important = 1
    """Print only important messages to the log window like warnings and error messages."""
    Info = 2
    """Print almost all information to the log window. Default setting."""
    Debug = 3
    """Print everything to the log window. """


@unique
class SpawnableMaterials(StrEnum):
    """Materials which can be spawned in the level editor"""

    Default = auto()
    SimpleColor = auto()
    ColoredTexture = auto()
    Glass = auto()
    SimpleColorWorldAligned = auto()
    SimpleEmissive = auto()
    SimpleTranslucent = auto()


@unique
class SpawnableSounds(StrEnum):
    """Sounds which can be played from the level editor"""

    Explosion = auto()
    ButtonClick = auto()
    DoorOpen = auto()
    DoorClose = auto()
    DoorSlide = auto()
    ExplosionMagic = auto()
    ExplosionPuff = auto()
    HitBarrel = auto()
    HitCardboard = auto()
    HitRubber = auto()
    HitGravel = auto()
    ElectricityBuzz = auto()
    LargeSwitch = auto()
    GunshotLarge = auto()
    TakePhoto = auto()
    GunshotSilenced = auto()
    TypingKeys = auto()
    SwitchSmall = auto()
    Appear = auto()
    Disappear = auto()


@unique
class BuiltinMusic(StrEnum):
    """Music which can be played from the SmartSpeaker"""

    TropicalPlaylist = auto()
    DemoPlaylist = auto()
    PianoPlaylist = auto()
    LowfiPlaylist = auto()


@unique
class MusicInstruments(StrEnum):
    """Available music instruments for the electric piano / keyboard."""

    AcousticPiano = auto()


@unique
class AmmunitionTypes(StrEnum):
    """Available ammunition types for artillery, grenades, high caliber rifles, etc"""

    Explosive = auto()
    # fire, smoke, emp, splinter


@unique
class Firearms(StrEnum):
    """Personal firearms that can be equipped."""

    Unarmed = auto()
    Pistol = auto()
    Rifle = auto()
    Shotgun = auto()
    MachineGun = auto()
    RocketLauncher = auto()


@unique
class CosmeticItems(StrEnum):
    """Personal cosmetic items that can be equipped."""

    Hat_Tophat = auto()


@unique
class SpawnableVFX(StrEnum):
    """VFX which can be shown from the level editor"""

    Explosion = auto()
    Fireworks1 = auto()
    ColorBurst = auto()
    Rain = auto()
    Distortion = auto()
    Sparks = auto()
    WaterJet = auto()


@unique
class SpawnableImages(StrEnum):
    """Images which can be shown from the level editor or used as material textures."""

    Blank = ""
    TargetIndicator = auto()


@unique
class SpawnableVideos(StrEnum):
    """Videos which can be shown from the level editor"""

    ManimPrintHello = auto()
    ManimForLoops = auto()
    ManimConditionals = auto()
    ManimVariables = auto()


# modding: add to CodeMirror.class_static_hints and CodeMirror.all_enum_tooltips
@unique
class Colormaps(StrEnum):
    """All colormaps available in matplotlib"""

    viridis = auto()
    plasma = auto()
    inferno = auto()
    magma = auto()
    cividis = auto()
    Greys = auto()
    Purples = auto()
    Blues = auto()
    Greens = auto()
    Oranges = auto()
    Reds = auto()
    YlOrBr = auto()
    YlOrRd = auto()
    OrRd = auto()
    PuRd = auto()
    RdPu = auto()
    BuPu = auto()
    GnBu = auto()
    PuBu = auto()
    YlGnBu = auto()
    PuBuGn = auto()
    BuGn = auto()
    YlGn = auto()
    binary = auto()
    gist_yarg = auto()
    gist_gray = auto()
    gray = auto()
    bone = auto()
    pink = auto()
    spring = auto()
    summer = auto()
    autumn = auto()
    winter = auto()
    cool = auto()
    Wistia = auto()
    hot = auto()
    afmhot = auto()
    gist_heat = auto()
    copper = auto()
    PiYG = auto()
    PRGn = auto()
    BrBG = auto()
    PuOr = auto()
    RdGy = auto()
    RdBu = auto()
    RdYlBu = auto()
    RdYlGn = auto()
    Spectral = auto()
    coolwarm = auto()
    bwr = auto()
    seismic = auto()
    twilight = auto()
    twilight_shifted = auto()
    hsv = auto()
    Pastel1 = auto()
    Pastel2 = auto()
    Paired = auto()
    Accent = auto()
    Dark2 = auto()
    Set1 = auto()
    Set2 = auto()
    Set3 = auto()
    tab10 = auto()
    tab20 = auto()
    tab20b = auto()
    tab20c = auto()
    flag = auto()
    prism = auto()
    ocean = auto()
    gist_earth = auto()
    terrain = auto()
    gist_stern = auto()
    gnuplot = auto()
    gnuplot2 = auto()
    CMRmap = auto()
    cubehelix = auto()
    brg = auto()
    gist_rainbow = auto()
    rainbow = auto()
    jet = auto()
    turbo = auto()
    nipy_spectral = auto()
    gist_ncar = auto()


@unique
class CsvDatasets(StrEnum):
    """Tabular CSV datasets included with the game."""

    iris = auto()
    """A small classic dataset about classifying 3 different iris plants. Contains 150 observations (50 per iris type) and 4 real-valued features (sepal length, sepal width, petal length, petal width) + 1 target class label (variety). Iris dataset (https://archive.ics.uci.edu/dataset/53/iris) by R.A. Fisher is licensed under CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/legalcode).
    """

    winequality = auto()
    """A dataset about wine quality based on physicochemical tests. Contains 6497 observations (unbalanced) and 11 real-valued features (fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free sulfur dioxide, total sulfur dioxide, density, pH, sulphates, alcohol) and two categorical columns (color of the wine, quality label of the wine). Wine quality dataset (https://archive.ics.uci.edu/dataset/186/wine+quality) by Cortez et al is licensed under CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/legalcode), slightly modified by maschere."""

    titanic = auto()
    """The original Titanic dataset, describing the survival status of individual passengers on the Titanic. Contains 1309 observations (passengers) with 8 features (pclass, sex, age, sibsp - number of siblings/spouses aboard, parch - number of parents/children aboard, fare, cabin, embarked) and 1 target label (survived 1 or 0). Slightly modified by maschere.

    The titanic data does not contain information from the crew, but it does contain actual ages of half of the passengers. The principal source for data about Titanic passengers is the Encyclopedia Titanica. The datasets used here were begun by a variety of researchers. One of the original sources is Eaton & Haas (1994) Titanic: Triumph and Tragedy, Patrick Stephens Ltd, which includes a passenger list created by many researchers and edited by Michael A. Findlay.

Thomas Cason of UVa has greatly updated and improved the titanic data frame using the Encyclopedia Titanica and created the dataset here. Some duplicate passengers have been dropped, many errors corrected, many missing ages filled in, and new variables created.

For more information about how this dataset was constructed: http://biostat.mc.vanderbilt.edu/wiki/pub/Main/DataSets/titanic3info.txt
Titanic dataset from https://www.openml.org/d/40945 ."""

    heartattack = auto()
    """A dataset for heart attack risk prediction. 303 observations (patients) with 13 features:
    Age : Age of the patient
    Sex : gender of the patient
    exang: exercise induced angina (1 = yes; 0 = no)
    ca: number of major vessels (0-3)
    cp : Chest Pain type chest pain type
        Value 1: typical angina
        Value 2: atypical angina
        Value 3: non-anginal pain
        Value 4: asymptomatic
    trtbps : resting blood pressure (in mm Hg)
    chol : cholestoral in mg/dl fetched via BMI sensor
    fbs : (fasting blood sugar > 120 mg/dl) (1 = true; 0 = false)
    rest_ecg : resting electrocardiographic results
        Value 0: normal
        Value 1: having ST-T wave abnormality (T wave inversions and/or ST elevation or depression of > 0.05 mV)
        Value 2: showing probable or definite left ventricular hypertrophy by Estes' criteria
    thalach : maximum heart rate achieved
    oldpeak: previous peak
    slp: slope
    caa: number of major vessels
    thall: thal rate

    Target variable is "output" with either 1 for increased heart attack risk or 0 for decreased heart attack risk.

    Dataset obtained from https://www.kaggle.com/datasets/rashikrahmanpritom/heart-attack-analysis-prediction-dataset?select=heart.csv by RASHIK RAHMAN licensed as public domain.
    """

    bikerental = auto()
    """Bike Sharing dataset (https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) by Hadi Fanaee-T licensed under CC-BY 4.0 (). Contains 17379 hourly observations with the following features:
    	- instant: record index
        - dteday : date
        - season : season (1:springer, 2:summer, 3:fall, 4:winter)
        - yr : year (0: 2011, 1:2012)
        - mnth : month ( 1 to 12)
        - hr : hour (0 to 23)
        - holiday : weather day is holiday or not (extracted from http://dchr.dc.gov/page/holiday-schedule)
        - weekday : day of the week
        - workingday : if day is neither weekend nor holiday is 1, otherwise is 0.
        + weathersit :
            - 1: Clear, Few clouds, Partly cloudy, Partly cloudy
            - 2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist
            - 3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds
            - 4: Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog
        - temp : Normalized temperature in Celsius. The values are divided to 41 (max)
        - atemp: Normalized feeling temperature in Celsius. The values are divided to 50 (max)
        - hum: Normalized humidity. The values are divided to 100 (max)
        - windspeed: Normalized wind speed. The values are divided to 67 (max)
        - casual: count of casual users
        - registered: count of registered users
        - cnt: count of total rental bikes including both casual and registered
    """
