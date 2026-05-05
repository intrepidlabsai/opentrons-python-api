""" Decorators for the ot_api functions """

import datetime
import functools

import opentrons.protocol_engine.errors as ot_errors
from opentrons_shared_data.errors.exceptions import EnumeratedError

import ot_api


def request_with_run_id(f):
  """ get run_id from param, if given, otherwise __init__, if given, otherwise raise error """

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    if "run_id" not in kwargs:
      run_id = ot_api.run_id
      if run_id is None:
        raise TypeError("No run_id given. Please pass run_id as a parameter or use ot_api.set_run_id()")
      kwargs["run_id"] = run_id

    try:
      return f(*args, **kwargs)
    except TypeError as e:
      if "run_id" in str(e):
        raise TypeError("Error calling function. Did you not pass run_id as a kwarg?")
      raise e

  return wrapper


def command(f, timeout=30):
  """ Decorator for commands. Uses request_with_run_id. Waits for success or failure, potentially raising an error. """

  def get_ot_error(name):
    # Fall back to ProtocolEngineError when the installed `opentrons` package
    # doesn't export a class with this name (e.g. firmware-side error types
    # like StallOrCollisionDetectedError on older opentrons). This preserves
    # the real `detail` string from the robot instead of masking it with an
    # AttributeError in the decoder itself.
    return getattr(ot_errors, name, ot_errors.ProtocolEngineError)

  def format_error_message(error_data) -> str:
    # Build a diagnostic message from an Opentrons command error payload.
    # Includes errorType, errorCode (if present), detail, and the detail of
    # any wrappedErrors so nested hardware errors (axis, motor) are not lost.
    parts = [error_data.get("errorType", "UnknownError")]
    error_code = error_data.get("errorCode")
    if error_code:
      parts.append(f"[{error_code}]")
    detail = error_data.get("detail")
    if detail:
      parts.append(detail)
    for w in error_data.get("wrappedErrors") or []:
      w_type = w.get("errorType", "UnknownError")
      w_detail = w.get("detail", "")
      parts.append(f"| wrapped: {w_type}: {w_detail}")
    return " ".join(parts)

  @request_with_run_id
  def wrapper(*args, **kwargs):
    command_id = f(*args, **kwargs)

    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < end:
      result = ot_api.runs.get_command(command_id, run_id=kwargs["run_id"])

      if result["data"]["status"] == "failed":
        error_data = result["data"]["error"]
        error_type = error_data["errorType"]
        if error_type == "PythonException":
          error_class = RuntimeError
        else:
          error_class = get_ot_error(error_type)

        message = format_error_message(error_data)

        # EnumeratedError subclasses (incl. ProtocolEngineError) take the
        # message via the `message=` kwarg. Passing positionally lands the
        # string in `code=`, which later breaks __str__ with `<exception
        # str() failed>` because __str__ dereferences `self.code.value.code`.
        if isinstance(error_class, type) and issubclass(error_class, EnumeratedError):
          raise error_class(message=message)
        raise error_class(message)
      elif result["data"]["status"] in ["queued", "running"]:
        continue

      return result

    raise RuntimeError("Command timed out")

  return wrapper
