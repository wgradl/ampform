"""A collection of data containers."""

import logging
from collections import abc
from functools import total_ordering
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    NewType,
    Optional,
    Tuple,
    Type,
    Union,
)

import attr

Scalar = Union[int, float]


@total_ordering
class Parity(abc.Hashable):
    """Safe, immutable data container for parity."""

    def __init__(self, value: Union[float, int, str]) -> None:
        value = float(value)
        if value not in [-1.0, +1.0]:
            raise ValueError(f"Parity can only be +1 or -1, not {value}")
        self.__value: int = int(value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Parity):
            return self.__value == other.value
        return self.__value == other

    def __gt__(self, other: Any) -> bool:
        return self.value > int(other)

    def __int__(self) -> int:
        return self.value

    def __neg__(self) -> "Parity":
        return Parity(-self.value)

    def __hash__(self) -> int:
        return self.__value

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}({"+1" if self.__value > 0 else "-1"})'
        )

    @property
    def value(self) -> int:
        return self.__value


class Spin(abc.Hashable):
    """Safe, immutable data container for spin **with projection**."""

    def __init__(self, magnitude: float, projection: float) -> None:
        magnitude = float(magnitude)
        projection = float(projection)
        if magnitude % 0.5 != 0.0:
            raise ValueError(
                f"Spin magnitude {magnitude} has to be a multitude of 0.5"
            )
        if abs(projection) > magnitude:
            if magnitude < 0.0:
                raise ValueError(
                    "Spin magnitude has to be positive:\n" f" {magnitude}"
                )
            raise ValueError(
                "Absolute value of spin projection cannot be larger than its "
                "magnitude:\n"
                f" abs({projection}) > {magnitude}"
            )
        if not (projection - magnitude).is_integer():
            raise ValueError(
                f"{self.__class__.__name__}{(magnitude, projection)}: "
                "(projection - magnitude) should be integer! "
            )
        if projection == -0.0:
            projection = 0.0
        self.__magnitude = magnitude
        self.__projection = projection

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Spin):
            return (
                self.__magnitude == other.magnitude
                and self.__projection == other.projection
            )
        return self.__magnitude == other

    def __float__(self) -> float:
        return self.__magnitude

    def __neg__(self) -> "Spin":
        return Spin(self.magnitude, -self.projection)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}{(self.__magnitude, self.__projection)}"
        )

    @property
    def magnitude(self) -> float:
        return self.__magnitude

    @property
    def projection(self) -> float:
        return self.__projection

    def __hash__(self) -> int:
        return hash(repr(self))


@attr.s(frozen=True, init=False)
class EdgeQuantumNumbers:  # pylint: disable=too-many-instance-attributes
    """Definition of quantum numbers for edges.

    This class defines the types that are used in the
    `~.solving.conservation_rules`, for instance in
    `.additive_quantum_number_rule`. You can also create data classes (see
    `attr.s`) with data members that are typed as the data members of
    `.EdgeQuantumNumbers` (see for example `.HelicityParityEdgeInput`) and use
    them in conservation rules that derive from `.Rule`.
    """

    pid = NewType("pid", int)
    mass = NewType("mass", float)
    width = NewType("width", float)
    spin_magnitude = NewType("spin_magnitude", float)
    spin_projection = NewType("spin_projection", float)
    charge = NewType("charge", int)
    isospin_magnitude = NewType("isospin_magnitude", float)
    isospin_projection = NewType("isospin_projection", float)
    strangeness = NewType("strangeness", int)
    charmness = NewType("charmness", int)
    bottomness = NewType("bottomness", int)
    topness = NewType("topness", int)
    baryon_number = NewType("baryon_number", int)
    electron_lepton_number = NewType("electron_lepton_number", int)
    muon_lepton_number = NewType("muon_lepton_number", int)
    tau_lepton_number = NewType("tau_lepton_number", int)
    parity = NewType("parity", Parity)
    c_parity = NewType("c_parity", Parity)
    g_parity = NewType("g_parity", Parity)


for edge_qn_name, edge_qn_type in EdgeQuantumNumbers.__dict__.items():
    if not edge_qn_name.startswith("__"):
        edge_qn_type.__qualname__ = f"EdgeQuantumNumbers.{edge_qn_name}"
        edge_qn_type.__module__ = "expertsystem.data"


# for static typing
EdgeQuantumNumber = Union[
    EdgeQuantumNumbers.pid,
    EdgeQuantumNumbers.mass,
    EdgeQuantumNumbers.width,
    EdgeQuantumNumbers.spin_magnitude,
    EdgeQuantumNumbers.spin_projection,
    EdgeQuantumNumbers.charge,
    EdgeQuantumNumbers.isospin_magnitude,
    EdgeQuantumNumbers.isospin_projection,
    EdgeQuantumNumbers.strangeness,
    EdgeQuantumNumbers.charmness,
    EdgeQuantumNumbers.bottomness,
    EdgeQuantumNumbers.topness,
    EdgeQuantumNumbers.baryon_number,
    EdgeQuantumNumbers.electron_lepton_number,
    EdgeQuantumNumbers.muon_lepton_number,
    EdgeQuantumNumbers.tau_lepton_number,
    EdgeQuantumNumbers.parity,
    EdgeQuantumNumbers.c_parity,
    EdgeQuantumNumbers.g_parity,
]


@attr.s(frozen=True, init=False)
class NodeQuantumNumbers:
    """Definition of quantum numbers for interaction nodes."""

    l_magnitude = NewType("l_magnitude", float)
    l_projection = NewType("l_projection", float)
    s_magnitude = NewType("s_magnitude", float)
    s_projection = NewType("s_projection", float)
    parity_prefactor = NewType("parity_prefactor", float)


for node_qn_name, node_qn_type in NodeQuantumNumbers.__dict__.items():
    if not node_qn_name.startswith("__"):
        node_qn_type.__qualname__ = f"NodeQuantumNumbers.{node_qn_name}"
        node_qn_type.__module__ = "expertsystem.data"


# for static typing
NodeQuantumNumber = Union[
    NodeQuantumNumbers.l_magnitude,
    NodeQuantumNumbers.l_projection,
    NodeQuantumNumbers.s_magnitude,
    NodeQuantumNumbers.s_projection,
    NodeQuantumNumbers.parity_prefactor,
]


@attr.s(frozen=True)
class InteractionProperties:
    """Immutable data structure containing interaction properties.

    .. note:: As opposed to `NodeQuantumNumbers`, the `InteractionProperties`
        class serves as an interface to the user.
    """

    l_magnitude: Optional[int] = attr.ib(
        default=None
    )  # L cannot be half integer
    l_projection: Optional[int] = attr.ib(default=None)
    s_magnitude: Optional[float] = attr.ib(default=None)
    s_projection: Optional[float] = attr.ib(default=None)
    parity_prefactor: Optional[float] = attr.ib(default=None)


def _get_node_quantum_number(
    qn_type: Type[NodeQuantumNumber], node_props: InteractionProperties
) -> Optional[Scalar]:
    return getattr(node_props, qn_type.__name__)


def _create_interaction_properties(
    qn_solution: Dict[Type[NodeQuantumNumber], Scalar]
) -> InteractionProperties:
    converted_solution = {k.__name__: v for k, v in qn_solution.items()}
    kw_args = {
        x.name: converted_solution[x.name]
        for x in attr.fields(InteractionProperties)
        if x.name in converted_solution
    }

    return attr.evolve(InteractionProperties(), **kw_args)


@attr.s(frozen=True)
class Particle:  # pylint: disable=too-many-instance-attributes
    """Immutable container of data defining a physical particle.

    A `Particle` is defined by the minimum set of the quantum numbers that
    every possible instances of that particle have in common (the "static"
    quantum numbers of the particle). A "non-static" quantum number is the spin
    projection. Hence `Particle` instances do **not** contain spin projection
    information.

    `Particle` instances are uniquely defined by their quantum numbers and
    properties like `~Particle.mass`. The `~Particle.name` and `~Particle.pid`
    are therefore just labels that are not taken into account when checking if
    two `Particle` instances are equal.

    .. note:: As opposed to classes such as `EdgeQuantumNumbers` and
        `NodeQuantumNumbers`, the `Particle` class serves as an interface to
        the user (see :doc:`/usage/particles`).
    """

    name: str = attr.ib(eq=False)
    pid: int = attr.ib(eq=False)
    spin: float = attr.ib()
    mass: float = attr.ib()
    width: float = attr.ib(default=0.0)
    charge: int = attr.ib(default=0)
    isospin: Optional[Spin] = attr.ib(default=None)
    strangeness: int = attr.ib(default=0)
    charmness: int = attr.ib(default=0)
    bottomness: int = attr.ib(default=0)
    topness: int = attr.ib(default=0)
    baryon_number: int = attr.ib(default=0)
    electron_lepton_number: int = attr.ib(default=0)
    muon_lepton_number: int = attr.ib(default=0)
    tau_lepton_number: int = attr.ib(default=0)
    parity: Optional[Parity] = attr.ib(default=None)
    c_parity: Optional[Parity] = attr.ib(default=None)
    g_parity: Optional[Parity] = attr.ib(default=None)

    @isospin.validator
    def __check_gellmann_nishijima(self, attribute, value) -> None:  # type: ignore  # pylint: disable=unused-argument
        if (
            self.isospin is not None
            and GellmannNishijima.compute_charge(self) != self.charge
        ):
            raise ValueError(
                f"Cannot construct particle {self.name}, because its quantum"
                " numbers don't agree with the Gell-Mann–Nishijima formula:\n"
                f"  Q[{self.charge}] != "
                f"Iz[{self.isospin.projection}] + 1/2 "
                f"(B[{self.baryon_number}] + "
                f" S[{self.strangeness}] + "
                f" C[{self.charmness}] +"
                f" B'[{self.bottomness}] +"
                f" T[{self.strangeness}]"
                ")"
            )

    def __neg__(self) -> "Particle":
        return create_antiparticle(self)

    def __repr__(self) -> str:
        output_string = f"{self.__class__.__name__}("
        for member in attr.fields(Particle):
            value = getattr(self, member.name)
            if value is None:
                continue
            if member.name not in ["mass", "spin", "isospin"] and value == 0:
                continue
            if isinstance(value, str):
                value = f'"{value}"'
            output_string += f"\n    {member.name}={value},"
        output_string += "\n)"
        return output_string

    def is_lepton(self) -> bool:
        return (
            self.electron_lepton_number != 0
            or self.muon_lepton_number != 0
            or self.tau_lepton_number != 0
        )


ParticleWithSpin = Tuple[Particle, float]


class GellmannNishijima:
    r"""Collection of conversion methods using Gell-Mann–Nishijima.

    The methods in this class use the `Gell-Mann–Nishijima formula
    <https://en.wikipedia.org/wiki/Gell-Mann%E2%80%93Nishijima_formula>`_:

    .. math::
        Q = I_3 + \frac{1}{2}(B+S+C+B'+T)

    where
    :math:`Q` is charge (computed),
    :math:`I_3` is `.Spin.projection` of `~.Particle.isospin`,
    :math:`B` is `~.Particle.baryon_number`,
    :math:`S` is `~.Particle.strangeness`,
    :math:`C` is `~.Particle.charmness`,
    :math:`B'` is `~.Particle.bottomness`, and
    :math:`T` is `~.Particle.topness`.
    """

    @staticmethod
    def compute_charge(state: Particle) -> Optional[float]:
        """Compute charge using the Gell-Mann–Nishijima formula.

        If isospin is not `None`, returns the value :math:`Q`: computed with
        the `Gell-Mann–Nishijima formula <.GellmannNishijima>`.
        """
        if state.isospin is None:
            return None
        computed_charge = state.isospin.projection + 0.5 * (
            state.baryon_number
            + state.strangeness
            + state.charmness
            + state.bottomness
            + state.topness
        )
        return computed_charge

    @staticmethod
    def compute_isospin_projection(  # pylint: disable=too-many-arguments
        charge: float,
        baryon_number: float,
        strangeness: float,
        charmness: float,
        bottomness: float,
        topness: float,
    ) -> float:
        """Compute isospin projection using the Gell-Mann–Nishijima formula.

        See `~.GellmannNishijima.compute_charge`, but then computed for
        :math:`I_3`.
        """
        return charge - 0.5 * (
            baryon_number + strangeness + charmness + bottomness + topness
        )


class ParticleCollection(abc.MutableSet):
    """Searchable collection of immutable `.Particle` instances."""

    def __init__(self, particles: Optional[Iterable[Particle]] = None) -> None:
        self.__particles: Dict[str, Particle] = dict()
        self.__pid_to_name: Dict[int, str] = dict()
        if particles is not None:
            self.update(particles)

    def __contains__(self, instance: object) -> bool:
        if isinstance(instance, str):
            return instance in self.__particles
        if isinstance(instance, Particle):
            return instance in self.__particles.values()
        if isinstance(instance, int):
            return instance in self.__pid_to_name
        raise NotImplementedError(
            f"Cannot search for type {instance.__class__.__name__}"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, abc.Iterable):
            return set(self) == set(other)
        raise NotImplementedError(
            f"Cannot compare {self.__class__.__name__} with  {self.__class__.__name__}"
        )

    def __getitem__(self, particle_name: str) -> Particle:
        if particle_name in self.__particles:
            return self.__particles[particle_name]
        error_message = (
            f'No particle with name "{particle_name} in the database"'
        )
        candidate_names = {
            name for name in self.__particles if particle_name in name
        }
        if candidate_names:
            raise KeyError(
                error_message,
                "Did you mean one of these?",
                candidate_names,
            )
        raise KeyError(error_message)

    def __iter__(self) -> Iterator[Particle]:
        return self.__particles.values().__iter__()

    def __len__(self) -> int:
        return len(self.__particles)

    def __iadd__(
        self, other: Union[Particle, "ParticleCollection"]
    ) -> "ParticleCollection":
        if isinstance(other, Particle):
            self.add(other)
        elif isinstance(other, ParticleCollection):
            self.update(other)
        else:
            raise NotImplementedError(f"Cannot add {other.__class__.__name__}")
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({set(self.__particles.values())})"

    def add(self, value: Particle) -> None:
        if value in self.__particles.values():
            equivalent_particles = {p for p in self if p == value}
            equivalent_particle = next(iter(equivalent_particles))
            raise KeyError(
                "While trying to add particle:",
                value,
                "An equivalent definition already exists:",
                equivalent_particle,
            )
        if value.name in self.__particles:
            logging.warning(f'Overwriting particle with name "{value.name}"')
        if value.pid in self.__pid_to_name:
            logging.warning(
                f'Particle with PID "{value.pid} already exists: {self.find(value.pid).name}"'
            )
        self.__particles[value.name] = value
        self.__pid_to_name[value.pid] = value.name

    def discard(self, value: Union[Particle, str]) -> None:
        particle_name = ""
        if isinstance(value, Particle):
            particle_name = value.name
        elif isinstance(value, str):
            particle_name = value
        else:
            raise NotImplementedError(
                f"Cannot discard something of type {value.__class__.__name__}"
            )
        del self.__pid_to_name[self[particle_name].pid]
        del self.__particles[particle_name]

    def find(self, search_term: Union[int, str]) -> Particle:
        """Search for a particle by either name (`str`) or PID (`int`)."""
        if isinstance(search_term, str):
            particle_name = search_term
            return self.__getitem__(particle_name)
        if isinstance(search_term, int):
            if search_term not in self.__pid_to_name:
                raise KeyError(f"No particle with PID {search_term}")
            particle_name = self.__pid_to_name[search_term]
            return self.__getitem__(particle_name)
        raise NotImplementedError(
            f"Cannot search for a search term of type {type(search_term)}"
        )

    def filter(  # noqa: A003
        self, function: Callable[[Particle], bool]
    ) -> "ParticleCollection":
        """Search by `Particle` properties using a :code:`lambda` function.

        For example:

        >>> from expertsystem import io
        >>> pdg = io.load_pdg()
        >>> results = pdg.filter(
        ...     lambda p: p.mass > 1.8
        ...     and p.mass < 2.0
        ...     and p.spin == 2
        ...     and p.strangeness == 1
        ... )
        >>> sorted([p.name for p in results])
        ['K(2)(1820)+', 'K(2)(1820)0']
        """
        return ParticleCollection(
            {particle for particle in self if function(particle)}
        )

    def update(self, other: Iterable[Particle]) -> None:
        if not isinstance(other, abc.Iterable):
            raise TypeError(
                f"Cannot update {self.__class__.__name__} from "
                f"non-iterable class {self.__class__.__name__}"
            )
        for particle in other:
            self.add(particle)


def create_particle(  # pylint: disable=too-many-arguments,too-many-locals
    template_particle: Particle,
    name: Optional[str] = None,
    pid: Optional[int] = None,
    mass: Optional[float] = None,
    width: Optional[float] = None,
    charge: Optional[int] = None,
    spin: Optional[float] = None,
    isospin: Optional[Spin] = None,
    strangeness: Optional[int] = None,
    charmness: Optional[int] = None,
    bottomness: Optional[int] = None,
    topness: Optional[int] = None,
    baryon_number: Optional[int] = None,
    electron_lepton_number: Optional[int] = None,
    muon_lepton_number: Optional[int] = None,
    tau_lepton_number: Optional[int] = None,
    parity: Optional[int] = None,
    c_parity: Optional[int] = None,
    g_parity: Optional[int] = None,
) -> Particle:
    return Particle(
        name=name if name else template_particle.name,
        pid=pid if pid else template_particle.pid,
        mass=mass if mass is not None else template_particle.mass,
        width=width if width else template_particle.width,
        spin=spin if spin else template_particle.spin,
        charge=charge if charge else template_particle.charge,
        strangeness=strangeness
        if strangeness
        else template_particle.strangeness,
        charmness=charmness if charmness else template_particle.charmness,
        bottomness=bottomness if bottomness else template_particle.bottomness,
        topness=topness if topness else template_particle.topness,
        baryon_number=baryon_number
        if baryon_number
        else template_particle.baryon_number,
        electron_lepton_number=electron_lepton_number
        if electron_lepton_number
        else template_particle.electron_lepton_number,
        muon_lepton_number=muon_lepton_number
        if muon_lepton_number
        else template_particle.muon_lepton_number,
        tau_lepton_number=tau_lepton_number
        if tau_lepton_number
        else template_particle.tau_lepton_number,
        isospin=template_particle.isospin
        if isospin is None
        else template_particle.isospin,
        parity=template_particle.parity if parity is None else Parity(parity),
        c_parity=template_particle.c_parity
        if c_parity is None
        else Parity(c_parity),
        g_parity=template_particle.g_parity
        if g_parity is None
        else Parity(g_parity),
    )


def create_antiparticle(
    template_particle: Particle, new_name: str = None
) -> Particle:
    isospin: Optional[Spin] = None
    if template_particle.isospin:
        isospin = -template_particle.isospin
    parity: Optional[Parity] = None
    if template_particle.parity is not None:
        if template_particle.spin.is_integer():
            parity = template_particle.parity
        else:
            parity = -template_particle.parity
    return Particle(
        name=new_name if new_name else "anti-" + template_particle.name,
        pid=-template_particle.pid,
        mass=template_particle.mass,
        width=template_particle.width,
        charge=-template_particle.charge,
        spin=template_particle.spin,
        isospin=isospin,
        strangeness=-template_particle.strangeness,
        charmness=-template_particle.charmness,
        bottomness=-template_particle.bottomness,
        topness=-template_particle.topness,
        baryon_number=-template_particle.baryon_number,
        electron_lepton_number=-template_particle.electron_lepton_number,
        muon_lepton_number=-template_particle.muon_lepton_number,
        tau_lepton_number=-template_particle.tau_lepton_number,
        parity=parity,
        c_parity=template_particle.c_parity,
        g_parity=template_particle.g_parity,
    )
