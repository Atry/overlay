import weakref
from abc import ABC
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    Generic,
    Never,
    Self,
    Type,
    TypeVar,
    cast,
    final,
)


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


@cast(Type[ABC], Collection).register
class InternedLinkedList(*((Collection,) if TYPE_CHECKING else ()), Generic[T_co]):
    """Base class for interned linked lists supporting O(1) equality comparison.

    Equal lists are interned to the same object instance, making equality
    comparison a simple identity check (O(1) instead of O(n)).

    This class is immutable and hashable, suitable for use as dictionary keys.

    Example::

        >>> list1 = InternedLinkedList(iter([1, 2, 3]))
        >>> list2 = InternedLinkedList(iter([1, 2, 3]))
        >>> list1 is list2  # Same object due to interning
        True

        >>> # Empty list is a singleton
        >>> empty1 = InternedLinkedList(iter([]))
        >>> empty2 = Empty.INSTANCE
        >>> empty1 is empty2
        True

        >>> # O(1) equality comparison via identity
        >>> list1 == list2
        True

        >>> # Suitable as dict key
        >>> cache = {list1: "cached_value"}
        >>> cache[list2]  # Same key due to interning
        'cached_value'
    """

    __slots__ = ()

    @staticmethod
    def from_iterable(values: Iterable[T_co]):
        """Create an interned linked list from the given iterable.

        :param values: The iterable to create the list from.
        :return: EmptyInternedLinkedList if iterator is empty,
                 otherwise returns NonEmptyInternedLinkedList.
        """
        values_tuple = tuple(values)
        if not values_tuple:
            return EmptyInternedLinkedList.INSTANCE

        result: InternedLinkedList[T_co] = EmptyInternedLinkedList.INSTANCE
        for element in reversed(values_tuple):
            result = NonEmptyInternedLinkedList(head=element, tail=result)

        assert isinstance(result, NonEmptyInternedLinkedList)
        return result


@final
class EmptyInternedLinkedList(InternedLinkedList[Never], Enum):
    """
    Singleton representing an empty interned linked list.

    Uses Enum to guarantee exactly one instance exists.
    Registered as virtual subclass of InternedLinkedList.
    """

    INSTANCE = auto()

    def __iter__(self) -> Iterator[Never]:
        return iter(())

    def __len__(self) -> int:
        return 0

    def __contains__(self, item: object) -> bool:
        return False


@final
@dataclass(kw_only=True, slots=True, frozen=True, weakref_slot=False)
class _InternPoolKey(Generic[T]):
    """Key for the intern pool, uniquely identifying a linked list node.

    Uses dataclass-generated __eq__ and __hash__ for structural comparison.
    Since tail is an InternedLinkedList (which uses identity-based eq/hash),
    comparing tails effectively compares by identity.
    """

    head: Final[T]
    tail: Final[InternedLinkedList[T]]


@final
@dataclass(kw_only=True, slots=True, frozen=True, weakref_slot=True, eq=False)
class NonEmptyInternedLinkedList(InternedLinkedList[T]):
    """Non-empty interned linked list node.

    Uses object.__eq__ and object.__hash__ (identity-based) for O(1) comparison.
    This works because interned lists with equal content are the same object.
    """

    head: Final[T]
    tail: Final[InternedLinkedList[T]]

    _intern_pool: ClassVar = weakref.WeakValueDictionary[_InternPoolKey[T], Self]()

    def __iter__(self) -> Iterator[T]:
        current: InternedLinkedList[T] = self
        while isinstance(current, NonEmptyInternedLinkedList):
            yield current.head
            current = current.tail

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __contains__(self, item: object) -> bool:
        return any(element == item for element in self)


def _replace_init():
    """
    Replace dataclass-generated ``__init__`` with a custom ``__new__`` for interning.

    This function patches :class:`NonEmptyInternedLinkedList` to support the
    flyweight/interning pattern with a frozen dataclass.

    Why delete ``__init__``?
    ------------------------

    Python's object creation follows this sequence:

    1. Call ``__new__(cls, ...)`` to create or retrieve an instance
    2. Call ``__init__(instance, ...)`` on the returned object

    For frozen dataclasses, ``__init__`` uses ``object.__setattr__`` to set
    attributes. The problem arises when returning a cached instance:

    .. code-block:: python

        # In __new__:
        existing = pool.get(key)
        if existing is not None:
            return existing  # Return already-initialized frozen instance

        # Python then automatically calls:
        # existing.__init__(head=..., tail=...)
        # This raises FrozenInstanceError because frozen instances
        # cannot have their attributes set again!

    Solution
    --------

    1. Save the original ``__init__`` generated by ``@dataclass``
    2. Delete ``__init__`` from the class (prevents automatic invocation)
    3. Define custom ``__new__`` that:

       - Returns existing instance from pool if found (no init needed)
       - For new instances: create via ``super().__new__``, manually call
         ``original_init``, then cache in pool

    This ensures ``__init__`` is only called once per unique instance.
    """
    original_init = NonEmptyInternedLinkedList.__init__
    del NonEmptyInternedLinkedList.__init__

    def __new__(
        cls: Type[NonEmptyInternedLinkedList[T]],
        *,
        head: T,
        tail: InternedLinkedList[T],
    ) -> NonEmptyInternedLinkedList[T]:
        key = _InternPoolKey(head=head, tail=tail)
        existing = NonEmptyInternedLinkedList._intern_pool.get(key)
        if existing is not None:
            return existing
        else:
            instance = super(NonEmptyInternedLinkedList, cls).__new__(cls)
            original_init(instance, head=head, tail=tail)
            NonEmptyInternedLinkedList._intern_pool[key] = instance
            return instance

    NonEmptyInternedLinkedList.__new__ = __new__


_replace_init()
