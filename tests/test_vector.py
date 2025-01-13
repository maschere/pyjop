"""Tests for the Vector module."""

from __future__ import annotations

__all__: list[str] = []

import math
from typing import TYPE_CHECKING

import numpy as np
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pyjop.Vector import TOLERANCE_ANGLE, Rotator3, Vector3

if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal


st_floats_no_nan = st.floats(allow_nan=False)
st_floats_no_nan_1e6 = st.floats(allow_nan=False, min_value=-1e6, max_value=1e6)
st_floats_no_nan_1e6_no_small = st_floats_no_nan_1e6.filter(lambda x: abs(x) >= 0.1)  # noqa: PLR2004


@st.composite
def st_vectors(
    draw: st.DrawFn,
    value_strategy: st.SearchStrategy[float] = st_floats_no_nan,
    dimension: Literal[0, 1, 2, 3] = 3,
) -> Vector3:
    return Vector3(
        x=draw(value_strategy) if dimension >= 1 else 0.0,
        y=draw(value_strategy) if dimension >= 2 else 0.0,  # noqa: PLR2004
        z=draw(value_strategy) if dimension == 3 else 0.0,  # noqa: PLR2004
    )


class TestVector:
    class TestCreation:
        @given(
            x=st.floats(allow_nan=False),
        )
        def test_create_vector3_one_arg(
            self,
            x: float,
        ) -> None:
            """Test creating a Vector3 object."""
            v_bare = Vector3(x)
            v_tuple = Vector3((x,))
            v_list = Vector3([x])
            v_ndarray = Vector3(np.array([x]))
            v_vector = Vector3(v_bare)

            for v in (v_bare, v_tuple, v_list, v_ndarray, v_vector):
                assert v.x == x
                assert v.y == x
                assert v.z == x

        @given(
            x=st.floats(allow_nan=False),
            y=st.floats(allow_nan=False),
        )
        def test_create_vector3_two_args(
            self,
            x: float,
            y: float,
        ) -> None:
            """Test creating a Vector3 object."""
            v_bare = Vector3(x, y)
            v_tuple = Vector3((x, y))
            v_list = Vector3([x, y])
            v_ndarray = Vector3(np.array([x, y]))
            v_vector = Vector3(v_bare)

            for v in (v_bare, v_tuple, v_list, v_ndarray, v_vector):
                assert v.x == x
                assert v.y == y
                assert v.z == 0.0

        @given(
            x=st.floats(allow_nan=False),
            y=st.floats(allow_nan=False),
            z=st.floats(allow_nan=False),
        )
        def test_create_vector3_three_args(
            self,
            x: float,
            y: float,
            z: float,
        ) -> None:
            """Test creating a Vector3 object."""
            v_bare = Vector3(x, y, z)
            v_tuple = Vector3((x, y, z))
            v_list = Vector3([x, y, z])
            v_ndarray = Vector3(np.array([x, y, z]))
            v_vector = Vector3(v_bare)
            v_view = np.array([x, y, z]).view(Vector3)

            for v in (v_bare, v_tuple, v_list, v_ndarray, v_vector, v_view):
                assert v.x == x
                assert v.y == y
                assert v.z == z

        @given(
            x=st.floats(allow_nan=False),
        )
        def test_create_vector3_invalid(
            self,
            x: float,
        ) -> None:
            """Test creating a Vector3 object."""
            raises_value_error = pytest.raises(
                ValueError,
                match=(
                    r"Invalid input for Vector3 - must be an instance "
                    r"of a Vector3, a length-3 array, 3 scalars, or "
                    r"nothing for \[0., 0., 0.\]"
                ),
            )
            with raises_value_error:
                Vector3((x, x, x, x))  # type: ignore[arg-type]
            with raises_value_error:
                Vector3([x, x, x, x])
            with raises_value_error:
                Vector3(np.array([x, x, x, x]))
            with raises_value_error:
                Vector3([])

            with pytest.raises(
                ValueError,
                match=r"Invalid array to view as Vector3 - must be length-3 array.",
            ):
                np.array([x]).view(Vector3)

    class TestOperations:
        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_str_repr(
            self,
            v: Vector3,
        ) -> None:
            """Test string representation of a Vector3 object."""
            assert str(v) == repr(v)

        @given(
            v=st_vectors(),
            new_v=st_vectors(),
        )
        def test_modify(
            self,
            v: Vector3,
            new_v: Vector3,
        ) -> None:
            """Test modifying a Vector3 object."""
            assert v.x == v.x
            assert v.y == v.y
            assert v.z == v.z
            v.x = new_v.x
            assert v.x == new_v.x
            assert v.y == v.y
            assert v.z == v.z
            v.y = new_v.y
            assert v.x == new_v.x
            assert v.y == new_v.y
            assert v.z == v.z
            v.z = new_v.z
            assert v.x == new_v.x
            assert v.y == new_v.y
            assert v.z == new_v.z

        @given(
            v=st_vectors(
                value_strategy=st_floats_no_nan_1e6,
                dimension=1,
            ),
        )
        def test_length_1d(
            self,
            v: Vector3,
        ) -> None:
            """Test the length of a Vector3 object."""
            assert v.length == pytest.approx(np.abs(v.x))

        @given(
            v=st_vectors(
                value_strategy=st_floats_no_nan_1e6,
                dimension=2,
            ),
        )
        def test_length_2d(
            self,
            v: Vector3,
        ) -> None:
            """Test the length of a Vector3 object."""
            assert v.length == pytest.approx(np.sqrt(v.x**2 + v.y**2))

        @given(
            v=st_vectors(
                value_strategy=st_floats_no_nan_1e6,
            ),
        )
        def test_length_3d(
            self,
            v: Vector3,
        ) -> None:
            """Test the length of a Vector3 object."""
            assert v.length == pytest.approx(np.sqrt(v.x**2 + v.y**2 + v.z**2))

        # Test length parameterized
        @pytest.mark.parametrize(
            ("v", "length"),
            [
                (Vector3(0.0, 0.0, 0.0), 0.0),
                (Vector3(1.0, 0.0, 0.0), 1.0),
                (Vector3(0.0, 1.0, 0.0), 1.0),
                (Vector3(0.0, 0.0, 1.0), 1.0),
                (Vector3(1.0, 1.0, 0.0), np.sqrt(2)),
                (Vector3(1.0, 0.0, 1.0), np.sqrt(2)),
                (Vector3(0.0, 1.0, 1.0), np.sqrt(2)),
                (Vector3(1.0, 1.0, 1.0), np.sqrt(3)),
                (Vector3(1.0, 2.0, 3.0), np.sqrt(14)),
            ],
        )
        def test_length_param(
            self,
            v: Vector3,
            length: float,
        ) -> None:
            """Test the length of a Vector3 object."""
            assert v.length == pytest.approx(length)

        @given(
            v=st_vectors(),
        )
        def test_slicing(
            self,
            v: Vector3,
        ) -> None:
            """Test slicing a Vector3 object."""
            assert v[0] == v.x
            assert v[1] == v.y
            assert v[2] == v.z
            assert v[-1] == v.z
            assert v[-2] == v.y
            assert v[-3] == v.x
            assert (v[:] == v).all()

        @given(
            v=st_vectors(),
        )
        def test_xy(
            self,
            v: Vector3,
        ) -> None:
            """Test xy of Vector3 objects."""
            assert (v.xy == Vector3(v.x, v.y, 0.0)).all()

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_dot_product(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test dot product of two Vector3 objects."""
            assert v.dot(v2) == pytest.approx(v.x * v2.x + v.y * v2.y + v.z * v2.z)

        def test_dot_cross_invalid(self) -> None:
            """Test invalid dot product."""
            v = Vector3(1.0, 2.0, 3.0)
            with pytest.raises(
                TypeError,
                match=r"Dot product operand must be a vector",
            ):
                v.dot(np.array([1.0, 2.0, 3.0]))  # type: ignore[arg-type]
            with pytest.raises(
                TypeError,
                match=r"Cross product operand must be a vector",
            ):
                v.cross(np.array([1.0, 2.0, 3.0]))  # type: ignore[arg-type]

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_cross_product(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test cross product of two Vector3 objects."""
            cross = v.cross(v2)
            assert cross.x == pytest.approx(v.y * v2.z - v.z * v2.y)
            assert cross.y == pytest.approx(v.z * v2.x - v.x * v2.z)
            assert cross.z == pytest.approx(v.x * v2.y - v.y * v2.x)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_parallel(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test if two Vector3 objects are parallel."""
            assert v.parallel(v2) == (v.cross(v2).length < TOLERANCE_ANGLE)

        @pytest.mark.parametrize(
            ("v1", "v2", "expected"),
            [
                (Vector3(1, 0, 0), Vector3(2, 0, 0), True),
                (Vector3(1, 1, 0), Vector3(2, 2, 0), True),
                (Vector3(1, 0, 0), Vector3(0, 1, 0), False),
                (Vector3(1, 1, 1), Vector3(2, 2, 2), True),
                (Vector3(1, 1, 1), Vector3(1, -1, 1), False),
            ],
        )
        def test_parallel_param(
            self,
            v1: Vector3,
            v2: Vector3,
            *,
            expected: bool,
        ) -> None:
            """Test if two Vector3 objects are parallel."""
            assert v1.parallel(v2) == expected

        @given(
            v=st_vectors(),
            v2=st_vectors(),
        )
        def test_perpendicular(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test if two Vector3 objects are perpendicular."""
            assert v.perpendicular(v2) == (abs(v.dot(v2)) < TOLERANCE_ANGLE)

        @pytest.mark.parametrize(
            ("v1", "v2", "expected"),
            [
                (Vector3(1, 0, 0), Vector3(0, 1, 0), True),
                (Vector3(1, 1, 0), Vector3(-1, 1, 0), True),
                (Vector3(1, 0, 0), Vector3(1, 0, 0), False),
                (Vector3(1, 1, 1), Vector3(1, 1, 1), False),
            ],
        )
        def test_perpendicular_param(
            self,
            v1: Vector3,
            v2: Vector3,
            *,
            expected: bool,
        ) -> None:
            """Test if two Vector3 objects are perpendicular."""
            assert v1.perpendicular(v2) == expected

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_as_normal(
            self,
            v: Vector3,
        ) -> None:
            """Test normalizing a Vector3 object."""
            assume(v.length >= 0.01)  # noqa: PLR2004
            normal = v.as_normal()
            assert normal.length == pytest.approx(1.0)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6_no_small),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6_no_small),
        )
        def test_angle(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test angle between two Vector3 objects."""
            assume(v.length != 0.0 and v2.length != 0.0 and not v.parallel(v2))
            angle_rad = v.angle(v2, unit="rad")
            angle_deg = v.angle(v2, unit="deg")
            if not math.isnan(angle_rad):
                assert angle_deg == pytest.approx(np.degrees(angle_rad))

            with pytest.raises(
                TypeError,
                match=r"Angle operand must be of class Vector3",
            ):
                v.angle(v2.view(np.ndarray), unit="rad")  # type: ignore[arg-type]

            with pytest.raises(
                ValueError,
                match=r"Only units of rad or deg are supported",
            ):
                v.angle(v2, unit="invalid")  # type: ignore[arg-type]

            with pytest.raises(
                ZeroDivisionError,
                match=r"Cannot calculate angle between zero-length vector\(s\)",
            ):
                v.angle(Vector3(0.0, 0.0, 0.0), unit="rad")

        def test_rotate_vector(self) -> None:
            # sourcery skip: class-extract-method
            """Test rotating a Vector3 object."""
            v = Vector3(1, 0, 0)
            rot = Rotator3(0, 0, 90)
            rotated_v = v.rotate_vector(rot)
            assert rotated_v.x == pytest.approx(0.0)
            assert rotated_v.y == pytest.approx(1.0)
            assert rotated_v.z == pytest.approx(0.0)

        def test_unrotate_vector(self) -> None:
            """Test un-rotating a Vector3 object."""
            v = Vector3(0, 1, 0)
            rot = Rotator3(0, 0, 90)
            unrotated_v = v.unrotate_vector(rot)
            assert unrotated_v.x == pytest.approx(1.0)
            assert unrotated_v.y == pytest.approx(0.0)
            assert unrotated_v.z == pytest.approx(0.0)

        def test_distance_to_line(self) -> None:
            """Test distance of a point from a line."""
            a = Vector3(0, 0, 0)
            b = Vector3(1, 0, 0)
            c = Vector3(0, 1, 0)
            distance = Vector3.distance_to_line(a, b, c)
            assert distance == pytest.approx(1.0)

        def test_random(self) -> None:
            """Test generating a random Vector3 object."""
            v = Vector3.random()
            assert -1.0 <= v.x <= 1.0
            assert -1.0 <= v.y <= 1.0
            assert -1.0 <= v.z <= 1.0

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_mul(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test multiplication of a Vector3 object."""
            result = v * val
            assert result.x == pytest.approx(v.x * val)
            assert result.y == pytest.approx(v.y * val)
            assert result.z == pytest.approx(v.z * val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_mul_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test multiplication of a Vector3 object with another Vector3."""
            result = v * v2
            assert result.x == pytest.approx(v.x * v2.x)
            assert result.y == pytest.approx(v.y * v2.y)
            assert result.z == pytest.approx(v.z * v2.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_rmul(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse multiplication of a Vector3 object."""
            result = val * v
            assert result.x == pytest.approx(v.x * val)
            assert result.y == pytest.approx(v.y * val)
            assert result.z == pytest.approx(v.z * val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_add(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test addition of a Vector3 object."""
            result = v + val
            assert result.x == pytest.approx(v.x + val)
            assert result.y == pytest.approx(v.y + val)
            assert result.z == pytest.approx(v.z + val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_add_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test addition of a Vector3 object with another Vector3."""
            result = v + v2
            assert result.x == pytest.approx(v.x + v2.x)
            assert result.y == pytest.approx(v.y + v2.y)
            assert result.z == pytest.approx(v.z + v2.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_radd(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse addition of a Vector3 object."""
            result = val + v
            assert result.x == pytest.approx(v.x + val)
            assert result.y == pytest.approx(v.y + val)
            assert result.z == pytest.approx(v.z + val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6_no_small,
        )
        def test_truediv(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test true division of a Vector3 object."""
            assume(val != 0)
            result = v / val
            assert result.x == pytest.approx(v.x / val)
            assert result.y == pytest.approx(v.y / val)
            assert result.z == pytest.approx(v.z / val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6_no_small),
        )
        def test_truediv_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test true division of a Vector3 object with another Vector3."""
            assume(v2.x != 0 and v2.y != 0 and v2.z != 0)
            result = v / v2
            assert result.x == pytest.approx(v.x / v2.x)
            assert result.y == pytest.approx(v.y / v2.y)
            assert result.z == pytest.approx(v.z / v2.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6_no_small),
            val=st_floats_no_nan_1e6,
        )
        def test_rtruediv(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse true division of a Vector3 object."""
            assume(v.x != 0 and v.y != 0 and v.z != 0)
            result = val / v
            assert result.x == pytest.approx(val / v.x)
            assert result.y == pytest.approx(val / v.y)
            assert result.z == pytest.approx(val / v.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6_no_small,
        )
        def test_floordiv(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test floor division of a Vector3 object."""
            assume(val != 0)
            result = v // val
            assert result.x == pytest.approx(v.x // val)
            assert result.y == pytest.approx(v.y // val)
            assert result.z == pytest.approx(v.z // val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6_no_small),
        )
        def test_floordiv_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test floor division of a Vector3 object with another Vector3."""
            assume(v2.x != 0.0 and v2.y != 0.0 and v2.z != 0.0)
            result = v // v2
            assert result.x == pytest.approx(v.x // v2.x)
            assert result.y == pytest.approx(v.y // v2.y)
            assert result.z == pytest.approx(v.z // v2.z)

        @given(
            v=st_vectors(
                value_strategy=st_floats_no_nan_1e6_no_small,
            ),
            val=st_floats_no_nan_1e6,
        )
        def test_rfloordiv(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse floor division of a Vector3 object."""
            assume(v.x != 0 and v.y != 0 and v.z != 0)
            result = val // v
            assert result.x == pytest.approx(val // v.x)
            assert result.y == pytest.approx(val // v.y)
            assert result.z == pytest.approx(val // v.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_sub(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test subtraction of a Vector3 object."""
            result = v - val
            assert result.x == pytest.approx(v.x - val)
            assert result.y == pytest.approx(v.y - val)
            assert result.z == pytest.approx(v.z - val)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            v2=st_vectors(value_strategy=st_floats_no_nan_1e6),
        )
        def test_sub_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test subtraction of a Vector3 object with another Vector3."""
            result = v - v2
            assert result.x == pytest.approx(v.x - v2.x)
            assert result.y == pytest.approx(v.y - v2.y)
            assert result.z == pytest.approx(v.z - v2.z)

        @given(
            v=st_vectors(value_strategy=st_floats_no_nan_1e6),
            val=st_floats_no_nan_1e6,
        )
        def test_rsub(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse subtraction of a Vector3 object."""
            result = val - v
            assert result.x == pytest.approx(val - v.x)
            assert result.y == pytest.approx(val - v.y)
            assert result.z == pytest.approx(val - v.z)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=0.1, max_value=10),
            ),
            val=st.floats(allow_nan=False, min_value=0.1, max_value=10),
        )
        def test_pow(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test power of a Vector3 object."""
            result = v**val
            assert result.x == pytest.approx(v.x**val)
            assert result.y == pytest.approx(v.y**val)
            assert result.z == pytest.approx(v.z**val)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=0.1, max_value=10),
            ),
            v2=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=0.1, max_value=10),
            ),
        )
        def test_pow_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test power of a Vector3 object with another Vector3."""
            result = v**v2
            assert result.x == pytest.approx(v.x**v2.x)
            assert result.y == pytest.approx(v.y**v2.y)
            assert result.z == pytest.approx(v.z**v2.z)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=0.1, max_value=10),
            ),
            val=st.floats(allow_nan=False, min_value=0.1, max_value=10),
        )
        def test_rpow(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse power of a Vector3 object."""
            result = val**v
            assert result.x == pytest.approx(val**v.x)
            assert result.y == pytest.approx(val**v.y)
            assert result.z == pytest.approx(val**v.z)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=1, max_value=1e6),
            ),
            val=st.floats(allow_nan=False, min_value=1, max_value=1e6),
        )
        def test_mod(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test modulo of a Vector3 object."""
            result = v % val
            assert result.x == pytest.approx(v.x % val)
            assert result.y == pytest.approx(v.y % val)
            assert result.z == pytest.approx(v.z % val)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=1, max_value=1e6),
            ),
            v2=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=1, max_value=1e6),
            ),
        )
        def test_mod_vector(
            self,
            v: Vector3,
            v2: Vector3,
        ) -> None:
            """Test modulo of a Vector3 object with another Vector3."""
            result = v % v2
            assert result.x == pytest.approx(v.x % v2.x)
            assert result.y == pytest.approx(v.y % v2.y)
            assert result.z == pytest.approx(v.z % v2.z)

        @given(
            v=st_vectors(
                value_strategy=st.floats(allow_nan=False, min_value=1, max_value=1e6),
            ),
            val=st.floats(allow_nan=False, min_value=1, max_value=1e6),
        )
        def test_rmod(
            self,
            v: Vector3,
            val: float,
        ) -> None:
            """Test reverse modulo of a Vector3 object."""
            assume(v.x != 0 and v.y != 0 and v.z != 0)
            result = val % v
            assert result.x == pytest.approx(val % v.x)
            assert result.y == pytest.approx(val % v.y)
            assert result.z == pytest.approx(val % v.z)

        def test_find_lookat_rotation(self) -> None:
            """Test finding lookat rotation."""
            v = Vector3(1, 1, 1)
            target = Vector3(2, 2, 2)
            rot = v.find_lookat_rotation(target)
            assert isinstance(rot, Rotator3)
            assert rot.as_normal().parallel(target - v)

        def test_as_orientation_rotator(self) -> None:
            """Test converting vector to orientation rotator."""
            v = Vector3(1, 1, 1)
            rot = v.as_orientation_rotator()
            assert isinstance(rot, Rotator3)
            assert rot.as_normal().parallel(v)
