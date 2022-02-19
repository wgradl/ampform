# pylint: disable=import-error, import-outside-toplevel
# pyright: reportMissingImports=false
"""Abbreviated the annotations generated by sphinx-autodoc.

It's not necessary to generate the full path of type hints, because they are
rendered as clickable links.

See also https://github.com/sphinx-doc/sphinx/issues/5868.
"""

from typing import List

import sphinx.domains.python
from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.environment import BuildEnvironment

__TARGET_SUBSTITUTIONS = {
    "a set-like object providing a view on D's items": "typing.ItemsView",
    "a set-like object providing a view on D's keys": "typing.KeysView",
    "ampform.helicity._T": "typing.TypeVar",
    "an object providing a view on D's values": "typing.ValuesView",
    "sp.Expr": "sympy.core.expr.Expr",
    "sp.Symbol": "sympy.core.symbol.Symbol",
    "sympy.printing.numpy.NumPyPrinter": "sympy.printing.printer.Printer",
    "typing_extensions.Protocol": "typing.Protocol",
}
__REF_TYPE_SUBSTITUTIONS = {
    "None": "obj",
    "ParameterValue": "obj",
    "ampform.dynamics.builder.BuilderReturnType": "obj",
    "ampform.kinematics.FourMomenta": "obj",
    "ampform.kinematics.FourMomentumSymbol": "obj",
    "ampform.sympy.DecoratedClass": "obj",
    "symplot.RangeDefinition": "obj",
    "symplot.Slider": "obj",
}


try:  # Sphinx >=4.4.0
    # https://github.com/sphinx-doc/sphinx/blob/v4.4.0/sphinx/domains/python.py#L110-L133
    from sphinx.addnodes import pending_xref_condition
    from sphinx.domains.python import parse_reftarget

    def _new_type_to_xref(
        target: str,
        env: BuildEnvironment = None,
        suppress_prefix: bool = False,
    ) -> pending_xref:
        reftype, target, title, refspecific = parse_reftarget(
            target, suppress_prefix
        )
        target = __TARGET_SUBSTITUTIONS.get(target, target)
        reftype = __REF_TYPE_SUBSTITUTIONS.get(target, reftype)
        assert env is not None
        return pending_xref(
            "",
            *__create_nodes(env, title),
            refdomain="py",
            reftype=reftype,
            reftarget=target,
            refspecific=refspecific,
            **__get_env_kwargs(env),
        )

except ImportError:  # Sphinx <4.4.0
    # https://github.com/sphinx-doc/sphinx/blob/v4.3.2/sphinx/domains/python.py#L83-L107
    def _new_type_to_xref(
        target: str,
        env: BuildEnvironment = None,
        suppress_prefix: bool = False,
    ) -> pending_xref:
        # pylint: disable=unused-argument
        target = __TARGET_SUBSTITUTIONS.get(target, target)
        reftype = __REF_TYPE_SUBSTITUTIONS.get(target, "class")
        assert env is not None
        return pending_xref(
            "",
            *__create_nodes(env, target),
            refdomain="py",
            reftype=reftype,
            reftarget=target,
            **__get_env_kwargs(env),
        )


def __get_env_kwargs(env: BuildEnvironment) -> dict:
    if env:
        return {
            "py:module": env.ref_context.get("py:module"),
            "py:class": env.ref_context.get("py:class"),
        }
    return {}


def __create_nodes(env: BuildEnvironment, title: str) -> List[nodes.Node]:
    short_name = title.split(".")[-1]
    if env.config.python_use_unqualified_type_names:
        return [
            pending_xref_condition("", short_name, condition="resolved"),
            pending_xref_condition("", title, condition="*"),
        ]
    return [nodes.Text(short_name)]


def relink_references() -> None:
    sphinx.domains.python.type_to_xref = _new_type_to_xref
