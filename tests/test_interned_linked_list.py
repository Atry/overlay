import gc
from collections.abc import Collection

from mixinject.interned_linked_list import NonEmptyInternedLinkedList, EmptyInternedLinkedList, InternedLinkedList


class TestEmpty:
    """Test empty list behavior."""

    def test_empty_from_empty_iterable(self) -> None:
        result = InternedLinkedList.from_iterable([])
        assert result is EmptyInternedLinkedList.INSTANCE

    def test_empty_iteration(self) -> None:
        assert list(EmptyInternedLinkedList.INSTANCE) == []

    def test_empty_length(self) -> None:
        assert len(EmptyInternedLinkedList.INSTANCE) == 0

    def test_empty_contains(self) -> None:
        assert 1 not in EmptyInternedLinkedList.INSTANCE
        assert "x" not in EmptyInternedLinkedList.INSTANCE


class TestCons:
    """Test non-empty list behavior."""

    def test_single_element(self) -> None:
        result = InternedLinkedList.from_iterable([42])
        assert isinstance(result, NonEmptyInternedLinkedList)
        assert result.head == 42
        assert result.tail is EmptyInternedLinkedList.INSTANCE

    def test_multiple_elements(self) -> None:
        result = InternedLinkedList.from_iterable([1, 2, 3])
        assert isinstance(result, NonEmptyInternedLinkedList)
        assert list(result) == [1, 2, 3]

    def test_iteration(self) -> None:
        result = InternedLinkedList.from_iterable(["a", "b", "c"])
        assert list(result) == ["a", "b", "c"]

    def test_length(self) -> None:
        result = InternedLinkedList.from_iterable([1, 2, 3, 4, 5])
        assert len(result) == 5

    def test_contains_present(self) -> None:
        result = InternedLinkedList.from_iterable([1, 2, 3])
        assert 2 in result

    def test_contains_absent(self) -> None:
        result = InternedLinkedList.from_iterable([1, 2, 3])
        assert 99 not in result


class TestInterning:
    """Test interning behavior for O(1) equality."""

    def test_same_content_same_object(self) -> None:
        list1 = InternedLinkedList.from_iterable([1, 2, 3])
        list2 = InternedLinkedList.from_iterable([1, 2, 3])
        assert list1 is list2

    def test_different_content_different_object(self) -> None:
        list1 = InternedLinkedList.from_iterable([1, 2, 3])
        list2 = InternedLinkedList.from_iterable([1, 2, 4])
        assert list1 is not list2

    def test_identity_based_equality(self) -> None:
        list1 = InternedLinkedList.from_iterable([1, 2, 3])
        list2 = InternedLinkedList.from_iterable([1, 2, 3])
        assert list1 == list2
        assert list1 is list2

    def test_usable_as_dict_key(self) -> None:
        list1 = InternedLinkedList.from_iterable([1, 2, 3])
        cache = {list1: "cached_value"}
        list2 = InternedLinkedList.from_iterable([1, 2, 3])
        assert cache[list2] == "cached_value"

    def test_tail_sharing(self) -> None:
        list1 = InternedLinkedList.from_iterable([2, 3])
        list2 = InternedLinkedList.from_iterable([1, 2, 3])
        assert isinstance(list2, NonEmptyInternedLinkedList)
        assert list2.tail is list1


class TestWeakReference:
    """Test weak reference behavior of intern pool."""

    def test_garbage_collection_removes_from_pool(self) -> None:
        list1 = InternedLinkedList.from_iterable([100, 200, 300])
        pool_size_before = len(NonEmptyInternedLinkedList._intern_pool)

        del list1
        gc.collect()

        pool_size_after = len(NonEmptyInternedLinkedList._intern_pool)
        assert pool_size_after < pool_size_before

    def test_recreate_after_gc(self) -> None:
        list1 = InternedLinkedList.from_iterable([999, 888, 777])

        del list1
        gc.collect()

        # After GC, the weak reference should be cleared from the intern pool.
        # Creating a new list with the same values should succeed.
        # We verify the intern pool was cleared by checking its size before/after.
        pool_size_after_gc = len(NonEmptyInternedLinkedList._intern_pool)

        list2 = InternedLinkedList.from_iterable([999, 888, 777])

        # The pool should now have one more entry (the newly created list2)
        pool_size_after_create = len(NonEmptyInternedLinkedList._intern_pool)
        assert pool_size_after_create == pool_size_after_gc + 3  # 3 nodes: 999->888->777

        # Verify list2 is usable
        assert tuple(list2) == (999, 888, 777)


class TestCollectionABC:
    """Test isinstance/issubclass behavior with collections.abc.Collection."""

    def test_interned_linked_list_is_subclass_of_collection(self) -> None:
        assert issubclass(InternedLinkedList, Collection)

    def test_empty_interned_linked_list_is_subclass_of_collection(self) -> None:
        assert issubclass(EmptyInternedLinkedList, Collection)

    def test_non_empty_interned_linked_list_is_subclass_of_collection(self) -> None:
        assert issubclass(NonEmptyInternedLinkedList, Collection)

    def test_empty_instance_is_instance_of_collection(self) -> None:
        empty = EmptyInternedLinkedList.INSTANCE
        assert isinstance(empty, Collection)

    def test_non_empty_instance_is_instance_of_collection(self) -> None:
        non_empty = InternedLinkedList.from_iterable([1, 2, 3])
        assert isinstance(non_empty, Collection)

    def test_empty_instance_is_instance_of_interned_linked_list(self) -> None:
        empty = EmptyInternedLinkedList.INSTANCE
        assert isinstance(empty, InternedLinkedList)

    def test_non_empty_instance_is_instance_of_interned_linked_list(self) -> None:
        non_empty = InternedLinkedList.from_iterable([1, 2, 3])
        assert isinstance(non_empty, InternedLinkedList)

    def test_empty_is_subclass_of_interned_linked_list(self) -> None:
        assert issubclass(EmptyInternedLinkedList, InternedLinkedList)

    def test_non_empty_is_subclass_of_interned_linked_list(self) -> None:
        assert issubclass(NonEmptyInternedLinkedList, InternedLinkedList)
