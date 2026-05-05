""" Somewhat nicer wrapper around ot_api.runs for lh related things """

from typing import Optional, Tuple

from ot_api.decorators import command, request_with_run_id
import ot_api.requestor as requestor
import ot_api.runs

def load_pipette(pipette_name, mount, run_id: Optional[str] = None) -> dict:
  assert mount in ["left", "right"]

  @command
  def _load_pipette(run_id=None):
    data = {
      "pipetteName": pipette_name,
      "mount": mount,
    }
    return ot_api.runs.enqueue_command("loadPipette", params=data, intent="setup", run_id=run_id)

  resp = _load_pipette(run_id=run_id)
  return resp["data"]["result"]

@request_with_run_id
def add_mounted_pipettes(run_id=None) -> Tuple[Optional[dict], Optional[dict]]:
  mounted_pipettes = requestor.get("/pipettes")

  left_pipette = mounted_pipettes["left"]
  if left_pipette["name"] is not None:
    left = load_pipette(left_pipette["name"], "left", run_id=run_id)
    left["name"] = left_pipette["name"]
  else:
    left = None

  right_pipette = mounted_pipettes["right"]
  if right_pipette["name"] is not None:
    right = load_pipette(right_pipette["name"], "right", run_id=run_id)
    right["name"] = right_pipette["name"]
  else:
    right = None

  return left, right

@command
def pick_up_tip(
  labware_id: str,
  well_name: str,
  pipette_id: str,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
  run_id: Optional[str]=None
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      }
    },
    "pipetteId": pipette_id
  }
  return ot_api.runs.enqueue_command("pickUpTip", params, intent="setup", run_id=run_id)

@command
def drop_tip(
  labware_id: str,
  well_name: str,
  pipette_id: str,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
  run_id: Optional[str]=None
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      }
    },
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("dropTip", params, intent="setup", run_id=run_id)

@command
def aspirate(
  labware_id: str,
  well_name: str,
  volume: float,
  flow_rate: float,
  pipette_id,
  run_id: Optional[str]=None,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      },
    },
    "flowRate": flow_rate,
    "volume": volume,
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("aspirate", params, intent="setup", run_id=run_id)

@command
def dispense(
  labware_id: str,
  well_name: str,
  volume: float,
  flow_rate: float,
  push_out: float,
  pipette_id,
  run_id: Optional[str]=None,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      },
    },
    "flowRate": flow_rate,
    "volume": volume,
    "pipetteId": pipette_id,
    "pushOut": push_out,
  }

  return ot_api.runs.enqueue_command("dispense", params, intent="setup", run_id=run_id)

@command
def blowout(
  labware_id: str,
  well_name: str,
  flow_rate: float,
  pipette_id,
  run_id: Optional[str]=None,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      },
    },
    "flowRate": flow_rate,
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("blowout", params, intent="setup", run_id=run_id)

@command
def move_arm(
  pipette_id: str,
  location_x: float,
  location_y: float,
  location_z: float,
  minimum_z_height: Optional[float],
  speed: Optional[float],
  force_direct: bool = False,
  run_id: Optional[str]=None
):
  params = {
    "pipetteId": pipette_id,
    "coordinates": {
      "x": location_x,
      "y": location_y,
      "z": location_z
    },
    "forceDirect": force_direct
  }

  if minimum_z_height is not None:
    params["minimumZHeight"] = minimum_z_height

  if speed is not None:
    params["speed"] = speed

  return ot_api.runs.enqueue_command("moveToCoordinates", params, intent="setup", run_id=run_id)

@command
def move_to_addressable_area_for_drop_tip(
  pipette_id: str,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
  run_id: Optional[str]=None,
):
  params = {
    "pipetteId": pipette_id,
    "addressableAreaName": "movableTrashA1",
    "wellName": "A1",
    "wellLocation": {
      "origin": "default",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      }
    },
    "alternateDropLocation": False
  }

  return ot_api.runs.enqueue_command("moveToAddressableAreaForDropTip", params,
                                     intent="setup", run_id=run_id)

@command
def blowout_in_place(
  flow_rate: float,
  pipette_id,
  run_id: Optional[str]=None,
):
  params = {
    "flowRate": flow_rate,
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("blowOutInPlace", params, intent="setup", run_id=run_id)

@command
def prepare_to_aspirate(
  pipette_id,
  run_id: Optional[str]=None,
):
  params = {
    "pipetteId": pipette_id
  }
  return ot_api.runs.enqueue_command("prepareToAspirate", params, intent="setup", run_id=run_id)

@command
def drop_tip_in_place(pipette_id: str, run_id: Optional[str]=None):
  params = {
    "pipetteId": pipette_id
  }
  return ot_api.runs.enqueue_command("dropTipInPlace", params, intent="setup", run_id=run_id)

@command
def move_relative(
  axis: str,
  pipette_id,
  run_id: Optional[str]=None,
  distance: float = 0,
):
  params = {
    "axis": axis,
    "distance": distance,
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("moveRelative", params, intent="setup", run_id=run_id)



@command
def move_to_well(
  labware_id: str,
  well_name: str,
  pipette_id,
  run_id: Optional[str]=None,
  offset_x: float = 0,
  offset_y: float = 0,
  offset_z: float = 0,
):
  params = {
    "labwareId": labware_id,
    "wellName": well_name,
    "wellLocation": {
      "origin": "top",
      "offset": {
        "x": offset_x,
        "y": offset_y,
        "z": offset_z
      },
    },
    "pipetteId": pipette_id
  }

  return ot_api.runs.enqueue_command("moveToWell", params, intent="setup", run_id=run_id)


@command
def move_to_coords(
    x: float,
    y: float,
    z: float,
    pipette_id: str,
    minimum_z_height: float = 500.0,
    run_id: Optional[str] = None,
    force_direct: bool = True,
):
    params = {
        "coordinates": {
            "x": x,
            "y": y,
            "z": z,
        },
        "minimumZHeight": minimum_z_height,
        "forceDirect": force_direct,
        "pipetteId": pipette_id,
    }
    return ot_api.runs.enqueue_command(
        "moveToCoordinates", params, intent="setup", run_id=run_id
    )


@command
def aspirate_in_place(
    volume: float,
    flow_rate: float,
    pipette_id: str,
    run_id: Optional[str] = None,
):
    assert flow_rate > 0
    params = {
        "volume": volume,
        "flowRate": flow_rate,
        "pipetteId": pipette_id,
        "run_id": run_id,
    }
    return ot_api.runs.enqueue_command(
        "aspirateInPlace", params=params, intent="setup", run_id=run_id
    )


@command
def dispense_in_place(
    volume: float,
    flow_rate: float,
    pipette_id: str,
    # push_out:Optional[int]=1, # this is not required...
    run_id: Optional[str] = None,
):
    assert flow_rate > 0
    params = {
        "volume": volume,
        "flowRate": flow_rate,
        "pipetteId": pipette_id,
        #'push_out': push_out,
        "run_id": run_id,
    }
    return ot_api.runs.enqueue_command(
        "dispenseInPlace", params=params, intent="setup", run_id=run_id
    )


@command
def retract_pipette_z_axis(
  pipette_mount: str, # left or right
  run_id: Optional[str] = None, 
) -> None: 
   params = {'axis': f'{pipette_mount}Z'}
   return ot_api.runs.enqueue_command(
     'retractAxis', params=params, intent='setup', run_id=run_id,
   )

@command
def home_pipette_plunger(
  pipette_mount: str,  # "left" or "right"
  run_id: Optional[str] = None,
) -> None:
  """Home the plunger (and Z) of one pipette via a Protocol Engine run command.

  Preferred over the direct /robot/home endpoint when a run is active: this
  enqueues a ``home`` command inside the PE session, so the engine's internal
  axis-state bookkeeping stays consistent after clearing a stall fault latch.

  Axes homed:
    ``{mount}Plunger`` — clears the ejector / plunger stall fault latch.
    ``{mount}Z``       — re-establishes the Z home position after retraction.
  """
  params = {'axes': [f'{pipette_mount}Plunger', f'{pipette_mount}Z']}
  return ot_api.runs.enqueue_command(
    'home', params=params, intent='setup', run_id=run_id,
  )

@command 
def home_extension_jaw(
  run_id: Optional[str] = None, 
) -> None: 
  params = {'axes': 'extensionJaw'}
  return ot_api.runs.enqueue_command(
      'home', params=params, intent='setup', run_id=run_id,
  )

@command
def home_extension_z_axis(
   run_id: Optional[str] = None,
) -> None:
  params = {'axes': 'extensionZ'}
  return ot_api.runs.enqueue_command(
        'home', params=params, intent='setup', run_id=run_id,
    ) 

  


@command
def home_gripper(
   run_id: Optional[str] = None,  
): 
  params = {'axes': ['extensionJaw']}
  return ot_api.runs.enqueue_command(
      'home', params=params, intent='setup', run_id=run_id,
  )


@command 
def safe_move_gantry(
    run_id: Optional[str] = None,
  ) -> None:

    params = {
      "mount": "left",
      "destination": {  
        "x": 200, 
        "y": 200,
        "z": 100, 
    }
    }
    return ot_api.runs.enqueue_command(
      "robot/moveTo", params=params, intent="setup", run_id=run_id
    )


@command 
def move_labware(
   labware_id: str, 
   new_location: dict[str, str], # Enum --> see opentrons HTTP spec
   strategy: str='usingGripper', # Enum --> "usingGripper", "manualMoveWithPause", "manualMoveWithoutPause"
   pickup_offset_x: float=0.,
   pickup_offset_y: float=0.,
   pickup_offset_z: float=0.,
   drop_offset_x: float=0.,
   drop_offset_y: float=0.,
   drop_offset_z: float=0.,
   run_id: Optional[str] = None,
):
   pickup_offset = {
      'x': pickup_offset_x,
      'y': pickup_offset_y,
      'z': pickup_offset_z,
   }

   drop_offset = {
      'x': drop_offset_x,
      'y': drop_offset_y,
      'z': drop_offset_z,
   }
   

   params = {
      'labwareId': labware_id,
      'newLocation': new_location,
      'strategy': strategy,
      'pickUpOffset': pickup_offset,
      'dropOffset': drop_offset,
   }
   return ot_api.runs.enqueue_command(
      'moveLabware', params=params, intent='setup', run_id=run_id,
   )


def transfer_to_loc(
    source_labware_id: str,
    source_well_name: str,
    dest_init_coords: dict[str, float],  # initially over labware
    dest_disp_z_diff: float,  # z coord diff between initial and dispensing height
    volume: float,
    pipette_id: str,
    run_id: Optional[str] = None,
    blowout: bool = True,
    blowout_flow_rate: Optional[float] = 300.0,
    asp_flow_rate: Optional[float] = 300.0,
    asp_offset_x: Optional[float] = 0.0,
    asp_offset_y: Optional[float] = 0.0,
    asp_offset_z: Optional[float] = 0.0,
    disp_flow_rate: Optional[float] = 300.0,
    disp_offset_x: Optional[float] = 0.0,
    disp_offset_y: Optional[float] = 0.0,
    disp_offset_z: Optional[float] = 0.0,
    minimum_z_height: float = 10.0,
    well_location={
        "origin": "top",
        "offset": {
            "x": 0.0,
            "y": 0.0,
            "z": 10.0,
        },
    },
    force_direct: bool = False,
    pipette_mount_map=None,
) -> None:
    """Transfer to location on the deck of the OT-2
    Performs the following steps:
      i) aspirate from defined well
      ii) move to specified coordinates
      iii) dispense
      iv) blowout
    """
    # aspirate from the source well
    r_asp = aspirate(
        labware_id=source_labware_id,
        well_name=source_well_name,
        volume=volume,
        pipette_id=pipette_id,
        flow_rate=asp_flow_rate,
        run_id=run_id,
        offset_x=asp_offset_x,
        offset_y=asp_offset_y,
        offset_z=asp_offset_z,
        minimum_z_height=minimum_z_height,
        well_location=well_location,
        force_direct=force_direct,
    )

    # TODO: might need to move to safe z-location

    # move to initial coordinates above the destination well
    r_move_init = move_to_coords(
        x=dest_init_coords["x"],
        y=dest_init_coords["y"],
        z=dest_init_coords["z"],
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # move to final dispensing heing in z-axis
    r_move_z = move_to_coords(
        x=dest_init_coords["x"],
        y=dest_init_coords["y"],
        z=dest_init_coords["z"] - dest_disp_z_diff,
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # dispense in place
    r_disp = dispense_in_place(
        volume=volume,
        flow_rate=disp_flow_rate,
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # blowout in place
    if blowout:
        r_blowout = blowout_in_place(
            flow_rate=blowout_flow_rate,
            pipette_id=pipette_id,
            run_id=run_id,
        )
    else:
        r_blowout = None

    # raise back up to initial height in z-axis
    r_move_final = move_to_coords(
        x=dest_init_coords["x"],
        y=dest_init_coords["y"],
        z=dest_init_coords["z"],
        pipette_id=pipette_id,
        run_id=run_id,
    )

    return None



def transfer_from_loc(
    source_init_coords: dict[str, float],  # initially over labware
    source_asp_z_diff: float,  # z coord diff between initial and dispensing height
    dest_labware_id: str,
    dest_well_name: str,
    volume: float,
    pipette_id: str,
    run_id: Optional[str] = None,
    blowout: bool = True,
    blowout_flow_rate: Optional[float] = 300.0,
    asp_flow_rate: Optional[float] = 300.0,
    asp_offset_x: Optional[float] = 0.0,
    asp_offset_y: Optional[float] = 0.0,
    asp_offset_z: Optional[float] = 0.0,
    disp_flow_rate: Optional[float] = 300.0,
    disp_offset_x: Optional[float] = 0.0,
    disp_offset_y: Optional[float] = 0.0,
    disp_offset_z: Optional[float] = 0.0,
    minimum_z_height: float = 10.0,
    well_location={
        "origin": "top",
        "offset": {
            "x": 0.0,
            "y": 0.0,
            "z": 10.0,
        },
    },
    force_direct: bool = False,
    pipette_mount_map=None,
):
    """Aspirates in place from a specified location,
    then dispenses in a known well
    """
    # move to initial coordinates above the source well
    r_move_init = move_to_coords(
        x=source_init_coords["x"],
        y=source_init_coords["y"],
        z=source_init_coords["z"],
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # move to final dispensing height in z-axis
    r_move_z = move_to_coords(
        x=source_init_coords["x"],
        y=source_init_coords["y"],
        z=source_init_coords["z"] - source_asp_z_diff,
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # aspirate in place
    r_asp = aspirate_in_place(
        volume=volume,
        flow_rate=asp_flow_rate,
        pipette_id=pipette_id,
        run_id=run_id,
    )

    # TODO: might need to move to a safe z location

    # dispense at target well
    r_disp = dispense(
        labware_id=dest_labware_id,
        well_name=dest_well_name,
        volume=volume,
        flow_rate=disp_flow_rate,
        pipette_id=pipette_id,
        run_id=run_id,
        offset_x=disp_offset_x,
        offset_y=disp_offset_y,
        offset_z=disp_offset_z,
        minimum_z_height=minimum_z_height,
        well_location=well_location,
        force_direct=force_direct,
    )

    return None
