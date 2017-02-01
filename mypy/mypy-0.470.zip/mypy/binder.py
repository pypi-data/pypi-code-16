from typing import (Dict, List, Set, Iterator, Union)
from contextlib import contextmanager

from mypy.types import Type, AnyType, PartialType
from mypy.nodes import (Key, Node, Expression, Var, RefExpr, SymbolTableNode)

from mypy.subtypes import is_subtype
from mypy.join import join_simple
from mypy.sametypes import is_same_type


class Frame(Dict[Key, Type]):
    """A Frame represents a specific point in the execution of a program.
    It carries information about the current types of expressions at
    that point, arising either from assignments to those expressions
    or the result of isinstance checks. It also records whether it is
    possible to reach that point at all.

    This information is not copied into a new Frame when it is pushed
    onto the stack, so a given Frame only has information about types
    that were assigned in that frame.
    """

    def __init__(self) -> None:
        self.unreachable = False


class ConditionalTypeBinder:
    """Keep track of conditional types of variables.

    NB: Variables are tracked by literal expression, so it is possible
    to confuse the binder; for example,

    ```
    class A:
        a = None          # type: Union[int, str]
    x = A()
    lst = [x]
    reveal_type(x.a)      # Union[int, str]
    x.a = 1
    reveal_type(x.a)      # int
    reveal_type(lst[0].a) # Union[int, str]
    lst[0].a = 'a'
    reveal_type(x.a)      # int
    reveal_type(lst[0].a) # str
    ```
    """

    def __init__(self) -> None:
        # The stack of frames currently used.  These map
        # expr.literal_hash -- literals like 'foo.bar' --
        # to types. The last element of this list is the
        # top-most, current frame. Each earlier element
        # records the state as of when that frame was last
        # on top of the stack.
        self.frames = [Frame()]

        # For frames higher in the stack, we record the set of
        # Frames that can escape there, either by falling off
        # the end of the frame or by a loop control construct
        # or raised exception. The last element of self.frames
        # has no corresponding element in this list.
        self.options_on_return = []  # type: List[List[Frame]]

        # Maps expr.literal_hash] to get_declaration(expr)
        # for every expr stored in the binder
        self.declarations = Frame()
        # Set of other keys to invalidate if a key is changed, e.g. x -> {x.a, x[0]}
        # Whenever a new key (e.g. x.a.b) is added, we update this
        self.dependencies = {}  # type: Dict[Key, Set[Key]]

        # Whether the last pop changed the newly top frame on exit
        self.last_pop_changed = False

        self.try_frames = set()  # type: Set[int]
        self.break_frames = []  # type: List[int]
        self.continue_frames = []  # type: List[int]

    def _add_dependencies(self, key: Key, value: Key = None) -> None:
        if value is None:
            value = key
        else:
            self.dependencies.setdefault(key, set()).add(value)
        for elt in key:
            if isinstance(elt, Key):
                self._add_dependencies(elt, value)

    def push_frame(self) -> Frame:
        """Push a new frame into the binder."""
        f = Frame()
        self.frames.append(f)
        self.options_on_return.append([])
        return f

    def _push(self, key: Key, type: Type, index: int=-1) -> None:
        self.frames[index][key] = type

    def _get(self, key: Key, index: int=-1) -> Type:
        if index < 0:
            index += len(self.frames)
        for i in range(index, -1, -1):
            if key in self.frames[i]:
                return self.frames[i][key]
        return None

    def push(self, node: Node, typ: Type) -> None:
        if not node.literal:
            return
        key = node.literal_hash
        if key not in self.declarations:
            self.declarations[key] = self.get_declaration(node)
            self._add_dependencies(key)
        self._push(key, typ)

    def unreachable(self) -> None:
        self.frames[-1].unreachable = True

    def get(self, expr: Union[Expression, Var]) -> Type:
        return self._get(expr.literal_hash)

    def is_unreachable(self) -> bool:
        # TODO: Copy the value of unreachable into new frames to avoid
        # this traversal on every statement?
        return any(f.unreachable for f in self.frames)

    def cleanse(self, expr: Expression) -> None:
        """Remove all references to a Node from the binder."""
        self._cleanse_key(expr.literal_hash)

    def _cleanse_key(self, key: Key) -> None:
        """Remove all references to a key from the binder."""
        for frame in self.frames:
            if key in frame:
                del frame[key]

    def update_from_options(self, frames: List[Frame]) -> bool:
        """Update the frame to reflect that each key will be updated
        as in one of the frames.  Return whether any item changes.

        If a key is declared as AnyType, only update it if all the
        options are the same.
        """

        frames = [f for f in frames if not f.unreachable]
        changed = False
        keys = set(key for f in frames for key in f)

        for key in keys:
            current_value = self._get(key)
            resulting_values = [f.get(key, current_value) for f in frames]
            if any(x is None for x in resulting_values):
                # We didn't know anything about key before
                # (current_value must be None), and we still don't
                # know anything about key in at least one possible frame.
                continue

            if isinstance(self.declarations.get(key), AnyType):
                type = resulting_values[0]
                if not all(is_same_type(type, t) for t in resulting_values[1:]):
                    type = AnyType()
            else:
                type = resulting_values[0]
                for other in resulting_values[1:]:
                    type = join_simple(self.declarations[key], type, other)
            if not is_same_type(type, current_value):
                self._push(key, type)
                changed = True

        self.frames[-1].unreachable = not frames

        return changed

    def pop_frame(self, can_skip: bool, fall_through: int) -> Frame:
        """Pop a frame and return it.

        See frame_context() for documentation of fall_through.
        """

        if fall_through > 0:
            self.allow_jump(-fall_through)

        result = self.frames.pop()
        options = self.options_on_return.pop()

        if can_skip:
            options.insert(0, self.frames[-1])

        self.last_pop_changed = self.update_from_options(options)

        return result

    def get_declaration(self, expr: Node) -> Type:
        if isinstance(expr, RefExpr) and isinstance(expr.node, Var):
            type = expr.node.type
            if isinstance(type, PartialType):
                return None
            return type
        else:
            return None

    def assign_type(self, expr: Expression,
                    type: Type,
                    declared_type: Type,
                    restrict_any: bool = False) -> None:
        if not expr.literal:
            return
        self.invalidate_dependencies(expr)

        if declared_type is None:
            # Not sure why this happens.  It seems to mainly happen in
            # member initialization.
            return
        if not is_subtype(type, declared_type):
            # Pretty sure this is only happens when there's a type error.

            # Ideally this function wouldn't be called if the
            # expression has a type error, though -- do other kinds of
            # errors cause this function to get called at invalid
            # times?
            return

        # If x is Any and y is int, after x = y we do not infer that x is int.
        # This could be changed.

        if (isinstance(self.most_recent_enclosing_type(expr, type), AnyType)
                and not restrict_any):
            pass
        elif isinstance(type, AnyType):
            self.push(expr, declared_type)
        else:
            self.push(expr, type)

        for i in self.try_frames:
            # XXX This should probably not copy the entire frame, but
            # just copy this variable into a single stored frame.
            self.allow_jump(i)

    def invalidate_dependencies(self, expr: Expression) -> None:
        """Invalidate knowledge of types that include expr, but not expr itself.

        For example, when expr is foo.bar, invalidate foo.bar.baz.

        It is overly conservative: it invalidates globally, including
        in code paths unreachable from here.
        """
        for dep in self.dependencies.get(expr.literal_hash, set()):
            self._cleanse_key(dep)

    def most_recent_enclosing_type(self, expr: Expression, type: Type) -> Type:
        if isinstance(type, AnyType):
            return self.get_declaration(expr)
        key = expr.literal_hash
        enclosers = ([self.get_declaration(expr)] +
                     [f[key] for f in self.frames
                      if key in f and is_subtype(type, f[key])])
        return enclosers[-1]

    def allow_jump(self, index: int) -> None:
        # self.frames and self.options_on_return have different lengths
        # so make sure the index is positive
        if index < 0:
            index += len(self.options_on_return)
        frame = Frame()
        for f in self.frames[index + 1:]:
            frame.update(f)
            if f.unreachable:
                frame.unreachable = True
        self.options_on_return[index].append(frame)

    def handle_break(self) -> None:
        self.allow_jump(self.break_frames[-1])
        self.unreachable()

    def handle_continue(self) -> None:
        self.allow_jump(self.continue_frames[-1])
        self.unreachable()

    @contextmanager
    def frame_context(self, *, can_skip: bool, fall_through: int = 1,
                      break_frame: int = 0, continue_frame: int = 0,
                      try_frame: bool = False) -> Iterator[Frame]:
        """Return a context manager that pushes/pops frames on enter/exit.

        If can_skip is True, control flow is allowed to bypass the
        newly-created frame.

        If fall_through > 0, then it will allow control flow that
        falls off the end of the frame to escape to its ancestor
        `fall_through` levels higher. Otherwise control flow ends
        at the end of the frame.

        If break_frame > 0, then 'break' statements within this frame
        will jump out to the frame break_frame levels higher than the
        frame created by this call to frame_context. Similarly for
        continue_frame and 'continue' statements.

        If try_frame is true, then execution is allowed to jump at any
        point within the newly created frame (or its descendents) to
        its parent (i.e., to the frame that was on top before this
        call to frame_context).

        After the context manager exits, self.last_pop_changed indicates
        whether any types changed in the newly-topmost frame as a result
        of popping this frame.
        """
        assert len(self.frames) > 1

        if break_frame:
            self.break_frames.append(len(self.frames) - break_frame)
        if continue_frame:
            self.continue_frames.append(len(self.frames) - continue_frame)
        if try_frame:
            self.try_frames.add(len(self.frames) - 1)

        new_frame = self.push_frame()
        if try_frame:
            # An exception may occur immediately
            self.allow_jump(-1)
        yield new_frame
        self.pop_frame(can_skip, fall_through)

        if break_frame:
            self.break_frames.pop()
        if continue_frame:
            self.continue_frames.pop()
        if try_frame:
            self.try_frames.remove(len(self.frames) - 1)

    @contextmanager
    def top_frame_context(self) -> Iterator[Frame]:
        """A variant of frame_context for use at the top level of
        a namespace (module, function, or class).
        """
        assert len(self.frames) == 1
        yield self.push_frame()
        self.pop_frame(True, 0)
