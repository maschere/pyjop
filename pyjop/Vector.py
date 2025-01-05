#based on https://github.com/seequent/vectormath/blob/master/vectormath/vector.py licensed under MIT by seequent
#and on https://github.com/allelos/vectors/blob/master/vectors/vectors.py licensed under MIT by 
from typing import Optional, SupportsFloat
import numpy as np



class Vector3(np.ndarray):
    """3D vector defined from the origin in a left-handed coordinate system. x is forward, y is right, z is up.
    """

    UP:"Vector3"
    RIGHT:"Vector3"
    FORWARD:"Vector3"
    DOWN:"Vector3"
    LEFT:"Vector3"
    BACKWARD:"Vector3"
    
    def __new__(cls, x:list|tuple|np.ndarray|SupportsFloat=0.0, y:Optional[SupportsFloat]=None, z:Optional[SupportsFloat]=None) -> "Vector3":                                  #pylint: disable=arguments-differ

        def read_array(X, Y, Z)->Vector3:
            """Build Vector3 from another Vector3, [x, y, z], or x/y/z"""
            if isinstance(X, cls):
                return cls(X.x, X.y, X.z)
            if isinstance(X, (list, tuple, np.ndarray)):
                if isinstance(X, np.ndarray):
                    X = X.flatten()
                if len(X) == 3:
                    return cls(X[0], X[1], X[2])
                if len(X) == 2:
                    return cls(X[0], X[1], 0.0)
                if len(X) == 1:
                    return cls(X[0],X[0], X[0])
            if np.isscalar(X) and Y is None and Z is None:
                xyz = np.r_[X, X, X]
                xyz = xyz.astype(float)
                return xyz.view(cls)
            if np.isscalar(X) and np.isscalar(Y) and Z is None:
                xyz = np.r_[X, Y, 0.0]
                xyz = xyz.astype(float)
                return xyz.view(cls)
            if np.isscalar(X) and np.isscalar(Y) and np.isscalar(Z):
                xyz = np.r_[X, Y, Z]
                xyz = xyz.astype(float)
                return xyz.view(cls)
            raise ValueError('Invalid input for Vector3 - must be an instance '
                             'of a Vector3, a length-3 array, 3 scalars, or '
                             'nothing for [0., 0., 0.]')

        return read_array(x, y, z)

    def __array_wrap__(self, out_arr, context=None):                           #pylint: disable=no-self-use, unused-argument
        """This is called at the end of ufuncs

        If the output is the wrong shape, return the ndarray view
        instead of vector view
        """
        if out_arr.shape != (3,):
            out_arr = out_arr.view(np.ndarray)
        return out_arr

    def __array_finalize__(self, obj):
        """This is called when initializing the vector

        If the constructor is used, obj is None. If slicing is
        used, obj has the same class as self. In both these cases,
        we let things pass.

        If we are viewing another array class as a vector, then obj has
        a different class than self. In this case, if the array has
        an invalid shape a ValueError is raised
        """
        if obj is None or obj.__class__ is Vector3:
            return
        if self.shape != (3,):
            raise ValueError(
                'Invalid array to view as Vector3 - must be length-3 array.'
            )


    @property
    def x(self) -> float:
        """x or forwards-component of vector"""
        return self[0]

    @x.setter
    def x(self, value:float):
        self[0] = value

    @property
    def y(self) -> float:
        """y or rightwards-component of vector"""
        return self[1]

    @y.setter
    def y(self, value:float):
        self[1] = value

    @property
    def length(self):
        """Length / size of vector"""
        return float(np.sqrt(np.sum(self**2)))



    def dot(self, vec) -> float:
        """Dot product with another vector"""
        if not isinstance(vec, self.__class__):
            raise TypeError('Dot product operand must be a vector')
        return np.dot(self, vec)

    def cross(self, vec) -> "Vector3":
        """Cross product with another vector"""
        if not isinstance(vec, self.__class__):
            raise TypeError('Cross product operand must be a vector')
        return self.__class__(np.cross(self, vec))

    def parallel(self, vector) -> bool:
        """Return True if vectors are parallel to each other."""
        if self.cross(vector).length < 0.000001:
            return True
        return False

    def perpendicular(self, vector) -> bool:
        """Return True if vectors are perpendicular to each other."""
        if abs(self.dot(vector)) < 0.000001:
            return True
        return False

    @property
    def z(self) -> float:
        """z or upwards-component of the vector"""
        return self[2]

    @z.setter
    def z(self, value:float):
        self[2] = value

    @property
    def xy(self) -> "Vector3":
        """planar xy vector, returned as vector3 with z set to 0."""
        return Vector3(self[0], self[1], 0.0)

    def __str__(self) -> str:
        return f"x: {round(self.x, 8)} y: {round(self.y, 8)} z: {round(self.z, 8)}"
    def __repr__(self) -> str:
        return self.__str__()

    def as_normal(self) -> "Vector3":
        """Return a new normal unit vector (normalized to length 1)"""
        return self * 1.0/(self.length)

    def angle(self, vec, unit='deg') -> float:
        """Calculate the angle between two Vectors

        unit: unit for returned angle, either 'rad' or 'deg'. Defaults to 'deg'
        """
        if not isinstance(vec, self.__class__):
            raise TypeError('Angle operand must be of class {}'
                            .format(self.__class__.__name__))
        if unit not in ['deg', 'rad']:
            raise ValueError('Only units of rad or deg are supported')

        denom = self.length * vec.length
        if denom == 0:
            raise ZeroDivisionError('Cannot calculate angle between '
                                    'zero-length vector(s)')

        ang = np.arccos(self.dot(vec) / denom)
        if unit == 'deg':
            ang = ang * 180 / np.pi
        return ang


    def __mul__(self, val) -> "Vector3":
        return Vector3(super().__mul__(val))
    def __rmul__(self, other) -> "Vector3":
        return Vector3(super().__rmul__(other))

    def __add__(self, val) -> "Vector3":
        return Vector3(super().__add__(val))
    def __radd__(self, other) -> "Vector3":
        return Vector3(super().__radd__(other))

    def __truediv__(self, val) -> "Vector3":
        return Vector3(super().__truediv__(val))
    def __rtruediv__(self, other) -> "Vector3":
        return Vector3(super().__rtruediv__(other))

    def __floordiv__(self, val) -> "Vector3":
        return Vector3(super().__floordiv__(val))
    def __rfloordiv__(self, other) -> "Vector3":
        return Vector3(super().__rfloordiv__(other))

    def __sub__(self, val) -> "Vector3":
        return Vector3(super().__sub__(val))
    def __rsub__(self, other) -> "Vector3":
        return Vector3(super().__rsub__(other))

    def __eq__(self, val) -> bool:
        return (self.__sub__(val).length < 0.0001)
    def __ne__(self, other):
        return self.__eq__(other) == False

    def __pow__(self, val) -> "Vector3":
        return Vector3(super().__pow__(val))
    def __rpow__(self, other) -> "Vector3":
        return Vector3(super().__rpow__(other))

    def __mod__(self, val) -> "Vector3":
        return Vector3(super().__mod__(val))
    def __rmod__(self, other) -> "Vector3":
        return Vector3(super().__rmod__(other))

    def rotate_vector(self, rot:"Rotator3", pivot:"Vector3" = (0,0,0)) -> "Vector3":
        """Rotate this vector by a specified rotator around the specified pivot point."""
        pivot = Vector3(pivot)
        return rot.rotate_vector(self - pivot) + pivot
    def unrotate_vector(self, rot:"Rotator3", pivot:"Vector3" = (0,0,0)) -> "Vector3":
        """Un-rotate this vector by a specified rotator around the specified pivot point."""
        pivot = Vector3(pivot)
        return rot.unrotate_vector(self - pivot) + pivot

    def find_lookat_rotation(self, target:"Vector3") -> "Rotator3":
        """Find a rotator that would rotate a forward unit vector (1,0,0) to look at at the specified target vector (point) from this vector (point).
        """
        return Rotator3.make_from_xforward(target - self)

    def as_orientation_rotator(self) -> "Rotator3":
        """Create a rotator that corresponds to the direction in which this vectors points. Roll cannot be determined from this and will be zero.
        """
        return Rotator3.make_from_normal(self)

    @staticmethod
    def distance_to_line(a:"Vector3", b:"Vector3", c:"Vector3") -> float:
        """Return the distance of point c from the line between a and b.

        Args:
            a (Vector3): one point on the line
            b (Vector3): another point on the line
            c (Vector3): point in space
        """
        return (c - a).cross(c - b).length / (b-a).length

    @staticmethod
    def random(xmin=-1.0, xmax=1.0, ymin=-1.0, ymax=1.0, zmin=-1.0, zmax=1.0) -> "Vector3":
        """Generate a new random vector within the specified bounds."""
        return Vector3(np.random.uniform(xmin,xmax), np.random.uniform(ymin,ymax), np.random.uniform(zmin,zmax))
        
Vector3.UP = Vector3(0,0,1)
Vector3.RIGHT = Vector3(0,1,0)
Vector3.FORWARD = Vector3(1,0,0)        
Vector3.DOWN = Vector3(0,0,-1)
Vector3.LEFT = Vector3(0,-1,0)
Vector3.BACKWARD = Vector3(-1,0,0)  


class Rotator3(np.ndarray):
    """3d rotator defined as roll, pitch, yaw in degrees around the forward x-axis.
    """
    
    TURN_LEFT:"Rotator3"
    TURN_RIGHT:"Rotator3"
    LOOK_UP:"Rotator3"
    LOOK_DOWN:"Rotator3"
    ROLL_CLOCKWISE:"Rotator3"
    ROLL_COUNTER_CLOCKWISE:"Rotator3"
    
    
    def __new__(cls, roll:list|tuple|np.ndarray|SupportsFloat=0.0, pitch:SupportsFloat=0.0, yaw:SupportsFloat=0.0) -> "Rotator3":                                  #pylint: disable=arguments-differ

        def read_array(X, Y, Z)->Rotator3:
            """Build Rotator3 from another Rotator3"""
            if isinstance(X, cls):
                return cls(X.roll, X.pitch, X.yaw)
            if isinstance(X, (list, tuple, np.ndarray)):
                if isinstance(X, np.ndarray):
                    X = X.flatten()
                if len(X) == 3:
                    return cls(X[0], X[1], X[2])
                if len(X) == 2:
                    return cls(X[0], X[1], 0.0)
                if len(X) == 1:
                    return cls(X[0],0.0, 0.0)
            if np.isscalar(X) and np.isscalar(Y) and np.isscalar(Z):
                xyz = np.r_[X, Y, Z]
                xyz = xyz.astype(float)
                return xyz.view(cls)
            raise ValueError('Invalid input for Rotator3 - must be an instance '
                             'of a Rotator3, a length-3 array, 3 scalars, or '
                             'nothing for [0., 0., 0.]')

        return read_array(roll, pitch, yaw)

    def __array_wrap__(self, out_arr, context=None):                           #pylint: disable=no-self-use, unused-argument
        """This is called at the end of ufuncs

        If the output is the wrong shape, return the ndarray view
        instead of vector view
        """
        if out_arr.shape != (3,):
            out_arr = out_arr.view(np.ndarray)
        return out_arr

    def __array_finalize__(self, obj):
        """This is called when initializing the vector

        If the constructor is used, obj is None. If slicing is
        used, obj has the same class as self. In both these cases,
        we let things pass.

        If we are viewing another array class as a vector, then obj has
        a different class than self. In this case, if the array has
        an invalid shape a ValueError is raised
        """
        if obj is None or obj.__class__ is Rotator3:
            return
        if self.shape != (3,):
            raise ValueError(
                'Invalid array to view as Vector3 - must be length-3 array.'
            )

    @property
    def roll(self) -> float:
        """roll (rotation about x-forward axis), 1st rotator component"""
        return self[0]

    @roll.setter
    def roll(self, value:float):
        self[0] = value

    @property
    def pitch(self) -> float:
        """pitch (rotation about rightwards-axis), 2nd rotator component"""
        return self[1]

    @pitch.setter
    def pitch(self, value:float):
        self[1] = value

    @property
    def yaw(self) -> float:
        """yaw (rotation about up-axis), 3rd rotator component"""
        return self[2]

    @yaw.setter
    def yaw(self, value:float):
        self[2] = value

    def __str__(self) -> str:
        return f"R: {round(self.roll, 4)} P: {round(self.pitch, 4)} Y: {round(self.yaw, 4)}"
    def __repr__(self) -> str:
        return self.__str__()

    def rotate_vector(self, vector:Vector3) -> Vector3:
        """Rotate a specified vector by this rotator."""
        m = self.make_rotation_matrix()
        return Vector3(np.dot(m,vector))
    def unrotate_vector(self, vector:Vector3) -> Vector3:
        """Un-rotate a specified vector by this rotator."""
        m = self.make_rotation_matrix()
        return Vector3(np.dot(m.T,vector))

    def as_normal(self) -> Vector3:
        """Convert this rotator to a normal unit vector (normalized to length 1) facing in the direction of this rotator."""
        return Vector3.FORWARD.rotate_vector(self).as_normal()

    def get_opposite(self) -> "Rotator3":
        """Get a rotator that faces in the opposite direction of this rotator."""
        return Rotator3.make_from_xforward(self.as_normal() * -1.0)

    def get_unwinded(self) -> "Rotator3":
        """Unwind this rotator to make sure all angles are between -180 and 180."""
        unwind = self.copy()
        for i in range(3):
            while unwind[i] > 180:
                unwind[i] -= 360.0
            while unwind[i] < -180:
                unwind[i] += 360.0
        return unwind


    def __mul__(self, val) -> "Rotator3":
        return Rotator3(super().__mul__(val))
    def __rmul__(self, other) -> "Rotator3":
        return Rotator3(super().__rmul__(other))

    def __add__(self, val) -> "Rotator3":
        return Rotator3(super().__add__(val))
    def __radd__(self, other) -> "Rotator3":
        return Rotator3(super().__radd__(other))

    def __truediv__(self, val) -> "Rotator3":
        return Rotator3(super().__truediv__(val))
    def __rtruediv__(self, other) -> "Rotator3":
        return Rotator3(super().__rtruediv__(other))

    def __floordiv__(self, val) -> "Rotator3":
        return Rotator3(super().__floordiv__(val))
    def __rfloordiv__(self, other) -> "Rotator3":
        return Rotator3(super().__rfloordiv__(other))

    def __sub__(self, val) -> "Rotator3":
        return Rotator3(super().__sub__(val))
    def __rsub__(self, other) -> "Rotator3":
        return Rotator3(super().__rsub__(other))


    def __pow__(self, val) -> "Rotator3":
        return Rotator3(super().__pow__(val))
    def __rpow__(self, other) -> "Rotator3":
        return Rotator3(super().__rpow__(other))

    def __mod__(self, val) -> "Rotator3":
        return Rotator3(super().__mod__(val))
    def __rmod__(self, other) -> "Rotator3":
        return Rotator3(super().__rmod__(other))




    @staticmethod
    def make_from_normal(v:Vector3) -> "Rotator3":
        """Create a rotator that corresponds to the direction in which the specified vectors points. Roll cannot be determined from this and will be zero.
        """
        rot = Rotator3(
            0,
            np.rad2deg(np.arctan2(v.z, np.sqrt(v.x*v.x + v.y*v.y))),
            np.rad2deg(np.arctan2(v.y,v.x)))
        return rot.get_unwinded()
        

    @staticmethod
    def make_from_xforward(v:Vector3) -> "Rotator3":
        newx = v.as_normal()
        up = Vector3.UP if abs(newx.z) < 1.0 - 1e-4 else Vector3.FORWARD
        newy = up.cross(newx).as_normal()
        newz = newx.cross(newy)
        pitch = np.rad2deg(np.arctan2(newx.z, np.sqrt(newx.x*newx.x + newx.y*newx.y)))
        yaw = np.rad2deg(np.arctan2(newx.y, newx.x))
        rot = Rotator3(0,pitch,yaw)
        m = Vector3(rot.make_rotation_matrix()[:,1])
        rot.roll = np.rad2deg(np.arctan2(newz.dot(m), newy.dot(m)))
        return rot.get_unwinded()

    def make_rotation_matrix(self) -> np.ndarray:
        # Convert angles to radians
        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)
        roll_rad = np.radians(self.roll)

        # Calculate sin and cos values
        CY = np.cos(yaw_rad)
        SY = np.sin(yaw_rad)
        CP = np.cos(pitch_rad)
        SP = np.sin(pitch_rad)
        CR = np.cos(roll_rad)
        SR = np.sin(roll_rad)

        # Build the rotation matrix
        rotation_matrix = np.array([
        [CP * CY, SR * SP * CY - CR * SY, -(CR * SP * CY + SR * SY)],
        [CP * SY, SR * SP * SY + CR * CY, CY * SR - CR * SP * SY],
        [SP, -SR * CP, CR * CP]
        ])
        

        return rotation_matrix

    @staticmethod
    def random() -> "Rotator3":
        """Generate a random rotator with all components (roll,pitch,yaw) initialized at random between -180 and 180 degrees.
        """
        return Rotator3(np.random.uniform(-180,180,size=(3,)))


Rotator3.TURN_LEFT = Rotator3(0,0,-90)
Rotator3.TURN_RIGHT = Rotator3(0,0,90)
Rotator3.LOOK_UP = Rotator3(0,90,0)        
Rotator3.LOOK_DOWN = Rotator3(0,-90,0)
Rotator3.ROLL_CLOCKWISE = Rotator3(90,0,0)
Rotator3.ROLL_COUNTER_CLOCKWISE = Rotator3(-90,0,0)  

#TODO: Add quaternion support

# v = Vector3(5,5,0)
# v2 = Vector3(5,0,0)
# v.find_lookat_rotation(v2)
# # # r = Rotator3(0,20,-45)

# # # #Rotator3.make_from_normal(v)
# v.rotate_vector(r)


# Vector3(40.2,40,2) - Vector3(2.2,40,2)
# v = Vector3()
# r = Rotator3(0,0,-45)
#print(Vector3(5,5,-4).rotate_vector(Rotator3(12,-324,3554), (10,-10,5)).unrotate_vector(Rotator3(12,-324,3554), (10,-10,5)))
#print(Vector3(1))