import six
import re

from craftai.errors import *
from craftai.operators import _OPERATORS
from craftai.time import Time

class Interpreter(object):

  @staticmethod
  def decide(tree, args):
    bare_tree, configuration, version = Interpreter._parse_tree(tree)
    if configuration != {}:
        context = Interpreter._rebuild_context(configuration, args)
    else:
        context = Interpreter.join_decide_args(args)
    # self._check_context(configuration, context, version)
    raw_decision = Interpreter._decide_recursion(bare_tree, context)

    # If the configuration is not included in the tree object (f.i. version 0.0.1)
    # we give a default key name to the output
    try:
        output_name = configuration.get("output")[0]
    except TypeError:
        output_name = "value"

    decision = {}
    decision["decision"] = {}
    decision["decision"][output_name] = raw_decision["value"]
    if raw_decision.get("standard_deviation", None) is not None:
        decision["decision"]["standard_deviation"] = raw_decision.get("standard_deviation")
    decision["confidence"] = raw_decision["confidence"]
    decision["predicates"] = raw_decision["predicates"]
    decision["context"] = context

    return decision

  ####################
  # Internal helpers #
  ####################

  @staticmethod
  def _rebuild_context(configuration, args):
      # Model should come from _parse_tree and is assumed to be checked upon
      # already
      mo = configuration["output"]
      mc = configuration["context"]

      # We should not use the output key(s) to compare against
      configuration_ctx = {
          key: mc[key] for (key, value) in mc.items() if (key not in mo)
      }

      context = {}
      for arg in args:
          if not arg:
              continue
          context.update({
              k: Interpreter._context_value(k, v, arg) for k, v in configuration_ctx.items()
          })

      return context

  @staticmethod
  def _context_value(k, v, arg):
    if isinstance(arg, Time):
      time_of_day = arg.to_dict()["time_of_day"]
      day_of_week = arg.to_dict()["day_of_week"]
      day_of_month = arg.to_dict()["day_of_month"]
      month_of_year = arg.to_dict()["month_of_year"]
      timezone = arg.to_dict()["timezone"]
      if (v["type"] == "day_of_week" and
          (v.get("is_generated") is None or v["is_generated"])):
        return day_of_week
      elif (v["type"] == "time_of_day" and
            (v.get("is_generated") is None or v["is_generated"])):
        return time_of_day
      elif (v["type"] == "day_of_month" and
            (v.get("is_generated") is None or v["is_generated"])):
        return day_of_month
      elif (v["type"] == "month_of_year" and
            (v.get("is_generated") is None or v["is_generated"])):
        return month_of_year
      elif v["type"] == "timezone":
        return timezone
      else:
        return None
    else:
      return arg.get(k)

  @staticmethod
  def _decide_recursion(node, context):
    # If we are on a leaf
    if not node.get("predicate_property"):
      return {
        "value": node["value"],
        "confidence": node.get("confidence") or 0,
        "standard_deviation": node.get("standard_deviation", None),
        "predicates": []
      }

    # If we are on a regular node
    prop_name = node["predicate_property"]

    ctx_value = context.get(prop_name)
    if ctx_value is None:
      raise CraftAIDecisionError(
        """Property '{}' is not defined in the given context""".
        format(prop_name)
      )

    # Finding the first element in this node's childrens matching the
    # operator condition with given context
    matching_child = Interpreter._find_matching_child(node, ctx_value, prop_name)

    if not matching_child:
      raise CraftAIDecisionError(
        """Invalid decision tree format, no leaf matching the given"""
        """ context could be found because the tree is malformed."""
      )

    # If a matching child is found, recurse
    result = Interpreter._decide_recursion(matching_child, context)
    new_predicates = [{
      "property": prop_name,
      "op": matching_child["predicate"]["op"],
      "value": matching_child["predicate"]["value"]
    }]
    return {
      "value": result["value"],
      "confidence": result["confidence"],
      "standard_deviation": result.get("standard_deviation", None),
      "predicates": new_predicates + result["predicates"]
    }

  @staticmethod
  def _find_matching_child(node, context, prop_name):
      for child in node["children"]:
          threshold = child["predicate"]["value"]
          operator = child["predicate"]["op"]
          if (not isinstance(operator, six.string_types) or
                  not (operator in _OPERATORS)):
              raise CraftAIDecisionError(
                  """Invalid decision tree format, {} is not a valid"""
                  """decision operator.""".
                  format(operator)
              )

          # To be compared, continuous parameters should not be strings
          if "continuous" in operator:
              context = float(context)
              threshold = float(threshold)

          if _OPERATORS[operator](context, threshold):
              return child
      return {}

  @staticmethod
  def join_decide_args(args):
    joined_args = {}
    for arg in args:
      if isinstance(arg, Time):
        joined_args.update(arg.to_dict())
      try:
        joined_args.update(arg)
      except TypeError:
        raise CraftAIDecisionError(
          """Invalid context args, the given objects aren't dicts"""
          """ or Time instances."""
        )
    return joined_args

  @staticmethod
  def _parse_tree(tree_object):
    # Checking definition of tree_object
    if not (tree_object and isinstance(tree_object, list)):
      raise CraftAIDecisionError(
        """Invalid decision tree format, the given object is not a"""
        """ list or is empty."""
      )

    # Checking version existence
    tree_version = tree_object[0].get("version")
    if not tree_version:
      raise CraftAIDecisionError(
        """Invalid decision tree format, unable to find the version"""
        """ information."""
      )

    # Checking version and tree validity according to version
    if re.compile('\d+.\d+.\d+').match(tree_version) is None:
      raise CraftAIDecisionError(
        """Invalid decision tree format, {} is not a valid version.""".
        format(tree_version)
      )
    elif tree_version == "0.0.1":
      if len(tree_object) < 2:
        raise CraftAIDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object[1]
      configuration = {}
    elif tree_version == "0.0.2":
      if (len(tree_object) < 2 or
          not tree_object[1].get("model")):
        raise CraftAIDecisionError(
          """Invalid decision tree format, no model found"""
        )
      if len(tree_object) < 3:
        raise CraftAIDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object[2]
      configuration = tree_object[1]["model"]
    elif tree_version == "0.0.3":
      if (len(tree_object) < 2 or
            not tree_object[1]):
        raise CraftAIDecisionError(
            """Invalid decision tree format, no configuration found"""
        )
      if len(tree_object) < 3:
        raise CraftAIDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object[2]
      configuration = tree_object[1]
    elif tree_version == "0.0.4":
      if (len(tree_object) < 2 or
            not tree_object[1]):
        raise CraftAIDecisionError(
            """Invalid decision tree format, no configuration found"""
        )
      if len(tree_object) < 3:
        raise CraftAIDecisionError(
          """Invalid decision tree format, no tree found."""
        )
      bare_tree = tree_object[2]
      configuration = tree_object[1]
    else:
      raise CraftAIDecisionError(
        """Invalid decision tree format, {} is not a supported"""
        """ version.""".
        format(tree_version)
      )
    return bare_tree, configuration, tree_version
