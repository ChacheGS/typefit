try:
    from typing import Literal, NamedTuple, Union
except ImportError:
    pass
else:
    from typefit.fitting import _handle_literal
    from typefit import typefit
    from pytest import raises

    def test_handle_literal():
        t = Literal["a", "b", "c"]
        assert _handle_literal(t, "a") == "a"
        assert _handle_literal(t, "b") == "b"
        assert _handle_literal(t, "c") == "c"

        with raises(ValueError):
            _handle_literal(t, "d")

    def test_typefit():
        class A(NamedTuple):
            type: Literal["a"]

        class B(NamedTuple):
            type: Literal["b"]

        T = Union[A, B]

        assert isinstance(typefit(T, {"type": "a"}), A)
        assert isinstance(typefit(T, {"type": "b"}), B)

        with raises(ValueError):
            typefit(T, {"type": "c"})
