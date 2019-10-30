"""
Compatibility module that backports the get_origin and get_args functions from
Python 3. This code is from the official standard library.

Copyright © 2001-2019 Python Software Foundation; All Rights Reserved
"""

import collections

# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import Generic, _GenericAlias

try:
    from typing import get_origin
except ImportError:

    def get_origin(tp):
        """Get the unsubscripted version of a type.

        This supports generic types, Callable, Tuple, Union, Literal, Final and ClassVar.
        Return None for unsupported types. Examples::

            get_origin(Literal[42]) is Literal
            get_origin(int) is None
            get_origin(ClassVar[int]) is ClassVar
            get_origin(Generic) is Generic
            get_origin(Generic[T]) is Generic
            get_origin(Union[T, int]) is Union
            get_origin(List[Tuple[T, T]][int]) == list
        """
        if isinstance(tp, _GenericAlias):
            return tp.__origin__
        if tp is Generic:
            return Generic
        return None


try:
    from typing import get_args  # lgtm[py/unused-import]
except ImportError:

    def get_args(tp):
        """Get type arguments with all substitutions performed.

        For unions, basic simplifications used by Union constructor are performed.
        Examples::
            get_args(Dict[str, int]) == (str, int)
            get_args(int) == ()
            get_args(Union[int, Union[T, int], str][int]) == (int, str)
            get_args(Union[int, Tuple[T, int]][str]) == (int, Tuple[str, int])
            get_args(Callable[[], T][int]) == ([], int)
        """
        if isinstance(tp, _GenericAlias):
            res = tp.__args__
            if get_origin(tp) is collections.abc.Callable and res[0] is not Ellipsis:
                res = (list(res[:-1]), res[-1])
            return res
        return ()


try:
    from typing import Literal  # lgtm[py/unused-import]
except ImportError:
    # noinspection PyProtectedMember
    from typing import (
        _tp_cache,
        _Final,
        _Immutable,
        _type_check,
        _remove_dups_flatten,
        Union,
    )

    class _SpecialForm(_Final, _Immutable, _root=True):
        """Internal indicator of special typing constructs.
        See _doc instance attribute for specific docs.
        """

        __slots__ = ("_name", "_doc")

        def __new__(cls, *args, **kwds):
            """Constructor.

            This only exists to give a better error message in case
            someone tries to subclass a special typing object (not a good idea).
            """
            if (
                len(args) == 3
                and isinstance(args[0], str)
                and isinstance(args[1], tuple)
            ):
                # Close enough.
                raise TypeError(f"Cannot subclass {cls!r}")
            return super().__new__(cls)

        def __init__(self, name, doc):
            self._name = name
            self._doc = doc

        def __eq__(self, other):
            if not isinstance(other, _SpecialForm):
                return NotImplemented
            return self._name == other._name

        def __hash__(self):
            return hash((self._name,))

        def __repr__(self):
            return "typing." + self._name

        def __reduce__(self):
            return self._name

        def __call__(self, *args, **kwds):
            raise TypeError(f"Cannot instantiate {self!r}")

        def __instancecheck__(self, obj):
            raise TypeError(f"{self} cannot be used with isinstance()")

        def __subclasscheck__(self, cls):
            raise TypeError(f"{self} cannot be used with issubclass()")

        @_tp_cache
        def __getitem__(self, parameters):
            if self._name == "Literal":
                # There is no '_type_check' call because arguments to Literal[...] are
                # values, not types.
                return _GenericAlias(self, parameters)
            raise TypeError(f"{self} is not subscriptable")

    # noinspection PyArgumentList
    Literal = _SpecialForm(
        "Literal",
        doc="""Special typing form to define literal types (a.k.a. value types).

            This form can be used to indicate to type checkers that the corresponding
            variable or function parameter has a value equivalent to the provided
            literal (or one of several literals):
        
              def validate_simple(data: Any) -> Literal[True]:  # always returns True
                  ...
        
              MODE = Literal['r', 'rb', 'w', 'wb']
              def open_helper(file: str, mode: MODE) -> str:
                  ...
        
              open_helper('/some/path', 'r')  # Passes type check
              open_helper('/other/path', 'typo')  # Error in type checker
        
           Literal[...] cannot be subclassed. At runtime, an arbitrary value
           is allowed as type argument to Literal[...], but type checkers may
           impose restrictions.
        """,
    )
