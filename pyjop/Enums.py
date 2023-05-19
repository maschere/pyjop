from enum import Enum, EnumMeta,auto, unique
from typing import Tuple


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
    """
    Returns True if a __dunder__ name, False otherwise.
    """
    return (
            len(name) > 4 and
            name[:2] == name[-2:] == '__' and
            name[2] != '_' and
            name[-3] != '_'
            )
    
class StrMetaEnum(MetaEnum):
    def __getitem__(cls, name:str):
        if name in cls._member_map_:
            return cls._member_map_[name]
        return name

    def __getattr__(cls, name:str):
        """
        Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        if  _is_dunder(name):
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
    

class ColorEnum(tuple,Enum, metaclass=MetaEnum):
    pass
    


@unique
class ParameterTypes(IntEnum):
    """data type enum
    """
    _None=0
    Bool=1
    Int=2
    Float=3
    Vector=4
    String=5
    FloatArray=6
    ByteArray=7
    Json=8
    Rotator=9
    Max=255

@unique
class MusicNotes(StrEnum):
    """names musical notes
    """
    C1="C1"
    Cs1="Cs1"
    D1="D1"
    Eb1="Eb1"
    E1="E1"
    F1="F1"
    Fs1="Fs1"
    G1="G1"
    Ab1="Ab1"
    A1="A1"
    Bb1="Bb1"
    B1="B1"
    C2="C2"
    Cs2="Cs2"
    D2="D2"
    Eb2="Eb2"
    E2="E2"
    F2="F2"
    Fs2="Fs2"
    G2="G2"
    Ab2="Ab2"
    A2="A2"
    Bb2="Bb2"
    B2="B2"
    C3="C3"
    Cs3="Cs3"
    D3="D3"
    Eb3="Eb3"
    E3="E3"
    F3="F3"
    Fs3="Fs3"
    G3="G3"
    Ab3="Ab3"
    A3="A3"
    Bb3="Bb3"
    B3="B3"
    C4="C4"
    Cs4="Cs4"
    D4="D4"
    Eb4="Eb4"
    E4="E4"
    F4="F4"
    Fs4="Fs4"
    G4="G4"
    Ab4="Ab4"
    A4="A4"
    Bb4="Bb4"
    B4="B4"
    C5="C5"
    Cs5="Cs5"
    D5="D5"
    Eb5="Eb5"
    E5="E5"
    F5="F5"
    Fs5="Fs5"
    G5="G5"
    Ab5="Ab5"
    A5="A5"
    Bb5="Bb5"
    B5="B5"
    C6="C6"
    Cs6="Cs6"
    D6="D6"
    Eb6="Eb6"
    E6="E6"
    F6="F6"
    Fs6="Fs6"
    G6="G6"
    Ab6="Ab6"
    A6="A6"
    Bb6="Bb6"
    B6="B6"
    C7="C7"
    Cs7="Cs7"
    D7="D7"
    Eb7="Eb7"
    E7="E7"
    F7="F7"
    Fs7="Fs7"
    G7="G7"
    Ab7="Ab7"
    A7="A7"
    Bb7="Bb7"
    B7="B7"
    


class Colors(ColorEnum):
    """Named css colors as RGB tuples
    """
    Aliceblue=(0.9411764705882353, 0.9725490196078431, 1.0)
    Antiquewhite=(0.9803921568627451, 0.9215686274509803, 0.8431372549019608)
    Aqua=(0.0, 1.0, 1.0)
    Aquamarine=(0.4980392156862745, 1.0, 0.8313725490196079)
    Azure=(0.9411764705882353, 1.0, 1.0)
    Beige=(0.9607843137254902, 0.9607843137254902, 0.8627450980392157)
    Bisque=(1.0, 0.8941176470588236, 0.7686274509803922)
    Black=(0.0, 0.0, 0.0)
    Blanchedalmond=(1.0, 0.9215686274509803, 0.803921568627451)
    Blue=(0.0, 0.0, 1.0)
    Blueviolet=(0.5411764705882353, 0.16862745098039217, 0.8862745098039215)
    Brown=(0.6470588235294118, 0.16470588235294117, 0.16470588235294117)
    Burlywood=(0.8705882352941177, 0.7215686274509804, 0.5294117647058824)
    Cadetblue=(0.37254901960784315, 0.6196078431372549, 0.6274509803921569)
    Chartreuse=(0.4980392156862745, 1.0, 0.0)
    Chocolate=(0.8235294117647058, 0.4117647058823529, 0.11764705882352941)
    Coral=(1.0, 0.4980392156862745, 0.3137254901960784)
    Cornflowerblue=(0.39215686274509803, 0.5843137254901961, 0.9294117647058824)
    Cornsilk=(1.0, 0.9725490196078431, 0.8627450980392157)
    Crimson=(0.8627450980392157, 0.0784313725490196, 0.23529411764705882)
    Cyan=(0.0, 1.0, 1.0)
    Darkblue=(0.0, 0.0, 0.5450980392156862)
    Darkcyan=(0.0, 0.5450980392156862, 0.5450980392156862)
    Darkgoldenrod=(0.7215686274509804, 0.5254901960784314, 0.043137254901960784)
    Darkgray=(0.6627450980392157, 0.6627450980392157, 0.6627450980392157)
    Darkgreen=(0.0, 0.39215686274509803, 0.0)
    Darkgrey=(0.6627450980392157, 0.6627450980392157, 0.6627450980392157)
    Darkkhaki=(0.7411764705882353, 0.7176470588235294, 0.4196078431372549)
    Darkmagenta=(0.5450980392156862, 0.0, 0.5450980392156862)
    Darkolivegreen=(0.3333333333333333, 0.4196078431372549, 0.1843137254901961)
    Darkorange=(1.0, 0.5490196078431373, 0.0)
    Darkorchid=(0.6, 0.19607843137254902, 0.8)
    Darkred=(0.5450980392156862, 0.0, 0.0)
    Darksalmon=(0.9137254901960784, 0.5882352941176471, 0.47843137254901963)
    Darkseagreen=(0.5607843137254902, 0.7372549019607844, 0.5607843137254902)
    Darkslateblue=(0.2823529411764706, 0.23921568627450981, 0.5450980392156862)
    Darkslategray=(0.1843137254901961, 0.30980392156862746, 0.30980392156862746)
    Darkslategrey=(0.1843137254901961, 0.30980392156862746, 0.30980392156862746)
    Darkturquoise=(0.0, 0.807843137254902, 0.8196078431372549)
    Darkviolet=(0.5803921568627451, 0.0, 0.8274509803921568)
    Deeppink=(1.0, 0.0784313725490196, 0.5764705882352941)
    Deepskyblue=(0.0, 0.7490196078431373, 1.0)
    Dimgray=(0.4117647058823529, 0.4117647058823529, 0.4117647058823529)
    Dimgrey=(0.4117647058823529, 0.4117647058823529, 0.4117647058823529)
    Dodgerblue=(0.11764705882352941, 0.5647058823529412, 1.0)
    Firebrick=(0.6980392156862745, 0.13333333333333333, 0.13333333333333333)
    Floralwhite=(1.0, 0.9803921568627451, 0.9411764705882353)
    Forestgreen=(0.13333333333333333, 0.5450980392156862, 0.13333333333333333)
    Fuchsia=(1.0, 0.0, 1.0)
    Gainsboro=(0.8627450980392157, 0.8627450980392157, 0.8627450980392157)
    Ghostwhite=(0.9725490196078431, 0.9725490196078431, 1.0)
    Goldenrod=(0.8549019607843137, 0.6470588235294118, 0.12549019607843137)
    Gold=(1.0, 0.8431372549019608, 0.0)
    Gray=(0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
    Green=(0.0, 0.5019607843137255, 0.0)
    Greenyellow=(0.6784313725490196, 1.0, 0.1843137254901961)
    Grey=(0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
    Honeydew=(0.9411764705882353, 1.0, 0.9411764705882353)
    Hotpink=(1.0, 0.4117647058823529, 0.7058823529411765)
    Indianred=(0.803921568627451, 0.3607843137254902, 0.3607843137254902)
    Indigo=(0.29411764705882354, 0.0, 0.5098039215686274)
    Ivory=(1.0, 1.0, 0.9411764705882353)
    Khaki=(0.9411764705882353, 0.9019607843137255, 0.5490196078431373)
    Lavenderblush=(1.0, 0.9411764705882353, 0.9607843137254902)
    Lavender=(0.9019607843137255, 0.9019607843137255, 0.9803921568627451)
    Lawngreen=(0.48627450980392156, 0.9882352941176471, 0.0)
    Lemonchiffon=(1.0, 0.9803921568627451, 0.803921568627451)
    Lightblue=(0.6784313725490196, 0.8470588235294118, 0.9019607843137255)
    Lightcoral=(0.9411764705882353, 0.5019607843137255, 0.5019607843137255)
    Lightcyan=(0.8784313725490196, 1.0, 1.0)
    Lightgoldenrodyellow=(0.9803921568627451, 0.9803921568627451, 0.8235294117647058)
    Lightgray=(0.8274509803921568, 0.8274509803921568, 0.8274509803921568)
    Lightgreen=(0.5647058823529412, 0.9333333333333333, 0.5647058823529412)
    Lightgrey=(0.8274509803921568, 0.8274509803921568, 0.8274509803921568)
    Lightpink=(1.0, 0.7137254901960784, 0.7568627450980392)
    Lightsalmon=(1.0, 0.6274509803921569, 0.47843137254901963)
    Lightseagreen=(0.12549019607843137, 0.6980392156862745, 0.6666666666666666)
    Lightskyblue=(0.5294117647058824, 0.807843137254902, 0.9803921568627451)
    Lightslategray=(0.4666666666666667, 0.5333333333333333, 0.6)
    Lightslategrey=(0.4666666666666667, 0.5333333333333333, 0.6)
    Lightsteelblue=(0.6901960784313725, 0.7686274509803922, 0.8705882352941177)
    Lightyellow=(1.0, 1.0, 0.8784313725490196)
    Lime=(0.0, 1.0, 0.0)
    Limegreen=(0.19607843137254902, 0.803921568627451, 0.19607843137254902)
    Linen=(0.9803921568627451, 0.9411764705882353, 0.9019607843137255)
    Magenta=(1.0, 0.0, 1.0)
    Maroon=(0.5019607843137255, 0.0, 0.0)
    Mediumaquamarine=(0.4, 0.803921568627451, 0.6666666666666666)
    Mediumblue=(0.0, 0.0, 0.803921568627451)
    Mediumorchid=(0.7294117647058823, 0.3333333333333333, 0.8274509803921568)
    Mediumpurple=(0.5764705882352941, 0.4392156862745098, 0.8588235294117647)
    Mediumseagreen=(0.23529411764705882, 0.7019607843137254, 0.44313725490196076)
    Mediumslateblue=(0.4823529411764706, 0.40784313725490196, 0.9333333333333333)
    Mediumspringgreen=(0.0, 0.9803921568627451, 0.6039215686274509)
    Mediumturquoise=(0.2823529411764706, 0.8196078431372549, 0.8)
    Mediumvioletred=(0.7803921568627451, 0.08235294117647059, 0.5215686274509804)
    Midnightblue=(0.09803921568627451, 0.09803921568627451, 0.4392156862745098)
    Mintcream=(0.9607843137254902, 1.0, 0.9803921568627451)
    Mistyrose=(1.0, 0.8941176470588236, 0.8823529411764706)
    Moccasin=(1.0, 0.8941176470588236, 0.7098039215686275)
    Navajowhite=(1.0, 0.8705882352941177, 0.6784313725490196)
    Navy=(0.0, 0.0, 0.5019607843137255)
    Oldlace=(0.9921568627450981, 0.9607843137254902, 0.9019607843137255)
    Olive=(0.5019607843137255, 0.5019607843137255, 0.0)
    Olivedrab=(0.4196078431372549, 0.5568627450980392, 0.13725490196078433)
    Orange=(1.0, 0.6470588235294118, 0.0)
    Orangered=(1.0, 0.27058823529411763, 0.0)
    Orchid=(0.8549019607843137, 0.4392156862745098, 0.8392156862745098)
    Palegoldenrod=(0.9333333333333333, 0.9098039215686274, 0.6666666666666666)
    Palegreen=(0.596078431372549, 0.984313725490196, 0.596078431372549)
    Paleturquoise=(0.6862745098039216, 0.9333333333333333, 0.9333333333333333)
    Palevioletred=(0.8588235294117647, 0.4392156862745098, 0.5764705882352941)
    Papayawhip=(1.0, 0.9372549019607843, 0.8352941176470589)
    Peachpuff=(1.0, 0.8549019607843137, 0.7254901960784313)
    Peru=(0.803921568627451, 0.5215686274509804, 0.24705882352941178)
    Pink=(1.0, 0.7529411764705882, 0.796078431372549)
    Plum=(0.8666666666666667, 0.6274509803921569, 0.8666666666666667)
    Powderblue=(0.6901960784313725, 0.8784313725490196, 0.9019607843137255)
    Purple=(0.5019607843137255, 0.0, 0.5019607843137255)
    Rebeccapurple=(0.4, 0.2, 0.6)
    Red=(1.0, 0.0, 0.0)
    Rosybrown=(0.7372549019607844, 0.5607843137254902, 0.5607843137254902)
    Royalblue=(0.2549019607843137, 0.4117647058823529, 0.8823529411764706)
    Saddlebrown=(0.5450980392156862, 0.27058823529411763, 0.07450980392156863)
    Salmon=(0.9803921568627451, 0.5019607843137255, 0.4470588235294118)
    Sandybrown=(0.9568627450980393, 0.6431372549019608, 0.3764705882352941)
    Seagreen=(0.1803921568627451, 0.5450980392156862, 0.3411764705882353)
    Seashell=(1.0, 0.9607843137254902, 0.9333333333333333)
    Sienna=(0.6274509803921569, 0.3215686274509804, 0.17647058823529413)
    Silver=(0.7529411764705882, 0.7529411764705882, 0.7529411764705882)
    Skyblue=(0.5294117647058824, 0.807843137254902, 0.9215686274509803)
    Slateblue=(0.41568627450980394, 0.35294117647058826, 0.803921568627451)
    Slategray=(0.4392156862745098, 0.5019607843137255, 0.5647058823529412)
    Slategrey=(0.4392156862745098, 0.5019607843137255, 0.5647058823529412)
    Snow=(1.0, 0.9803921568627451, 0.9803921568627451)
    Springgreen=(0.0, 1.0, 0.4980392156862745)
    Steelblue=(0.27450980392156865, 0.5098039215686274, 0.7058823529411765)
    Tan=(0.8235294117647058, 0.7058823529411765, 0.5490196078431373)
    Teal=(0.0, 0.5019607843137255, 0.5019607843137255)
    Thistle=(0.8470588235294118, 0.7490196078431373, 0.8470588235294118)
    Tomato=(1.0, 0.38823529411764707, 0.2784313725490196)
    Turquoise=(0.25098039215686274, 0.8784313725490196, 0.8156862745098039)
    Violet=(0.9333333333333333, 0.5098039215686274, 0.9333333333333333)
    Wheat=(0.9607843137254902, 0.8705882352941177, 0.7019607843137254)
    White=(1.0, 1.0, 1.0)
    Whitesmoke=(0.9607843137254902, 0.9607843137254902, 0.9607843137254902)
    Yellow=(1.0, 1.0, 0.0)
    Yellowgreen=(0.6039215686274509, 0.803921568627451, 0.19607843137254902)


def _hex_to_rgb(hex_string:str):
    hex_string = hex_string.lstrip('#').upper()  # Remove '#' and convert to uppercase
    red = int(hex_string[0:2], 16) / 255.0
    green = int(hex_string[2:4], 16) / 255.0
    blue = int(hex_string[4:6], 16) / 255.0
    return red, green, blue


def _parse_color(color_arg)->tuple[float,float,float]:
    if type(color_arg) is str and color_arg in Colors:
        color_arg = Colors[color_arg]
    if type(color_arg) is Colors:
        color_arg = color_arg.value
    if type(color_arg) is str and len(color_arg)==7 and color_arg[0]=="#":
        color_arg = _hex_to_rgb(color_arg)
    if len(color_arg) > 3:
        color_arg = color_arg[:3]
    if max(color_arg) > 1:
        color_arg = [c/255.0 for c in color_arg]
    return color_arg

@unique
class ComparisonResult(IntEnum):
    """ComparisonResult enum for pair-wise comparisons between A and B resulting in A<B -> LessThan, A==B -> Equal, A>B -> GreaterThan 
    """
    LessThan=-1
    Equal=0
    GreatherThan=1




@unique
class GoalState(StrEnum):
    """GoalStates for level editor
    """
    Open=auto()
    Success=auto()
    Fail=auto()
    Ignore=auto()
    Unknown=auto()

@unique
class SpawnableMaps(StrEnum):
    """spawnable maps for the level editor
    """
    MinimalisticIndoor=auto()
    ParkingLot=auto()
    DesertIsland=auto() 

@unique
class SpawnableEntities(StrEnum):
    """entities which can be spawned in the level editor
    """
    ConveyorBelt=auto()
    DeliverableBox=auto()
    RangeFinder=auto()
    ServiceDrone=auto()

@unique
class SpawnableMeshes(StrEnum):
    """meshes which can be spawned in the level editor
    """
    Cube=auto()
    Sphere=auto()
    Plane=auto()
    Cylinder=auto()
    Cone=auto()

@unique
class SpawnableMaterials(StrEnum):
    """materias which can be spawned in the level editor
    """
    Default=auto()
    SimpleColor=auto()

@unique
class SpawnableSounds(StrEnum):
    """Sounds which can be played from the level editor
    """
    Explosion=auto()

@unique
class SpawnableVFX(StrEnum):
    """VFX which can be shown from the level editor
    """
    Explosion=auto()

@unique
class SpawnableImages(StrEnum):
    """Images which can be shown from the level editor
    """
    JoyOfProgrammingLogo=auto()

#modding: add to CodeMirror.class_static_hints and CodeMirror.all_enum_tooltips