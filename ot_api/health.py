""" Somewhat nicer wrapper around ot_api.runs for health related things """

from ot_api.requestor import get as rget, post

def get():
  return rget("/health")

def home():
  return post("/robot/home", data={"target": "robot"})

def home_pipette(mount: str = "left"):
  """Home just one pipette (resets plunger + Z on that mount).

  Useful after a STALL_OR_COLLISION on the pipette axis: the firmware
  latches the fault and refuses further motion on that axis until it
  is homed. Targeting just the pipette avoids moving the gantry -- so
  it's safe to call mid-protocol with a tip attached over a reservoir.
  """
  return post("/robot/home", data={"target": "pipette", "mount": mount})
