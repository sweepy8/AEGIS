# LLM Pilot class for rover. Provides high-level autopilot functions and holds

# AEGIS Senior Design, Created 10/22/2025

import os
import openai

import json
import time
import random


class Autopilot:

    memory_depth = 10  # Number of past interactions to remember
    model_name = "gpt-5"  # LLM model to use


    def __init__(self):
        pass

    def decide_action(self, telemetry: list[int]) -> dict:
        """
        Decide on the next action based on telemetry input.
        Returns a dict with action details.
        """
        pass

    def update_memory(self, role: str, content: str):
        """
        Update the internal memory with a new message.
        """
        pass

    def get_memory(self) -> list[dict]:
        """
        Retrieve the current memory as a list of messages.
        """
        pass

    


# Connect API account to client
client = openai.OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

system_context = """
You are controlling a rover. Follow these rules:
- Always prioritize safety of the motors and sensors.
- Decisions must be based on incoming telemetry.
- Telemetry is provided as an array with the following mapping:
    [uptime, remaining storage in GB, scan resolution, camera connected, 
     camera recording, 
     front left mot. amps, mid left mot. amps, rear left mot. amps, 
     front right mot. amps, mid right mot. amps, rear right mot. amps, 
     front left ultrasonic dist (cm), front center US. dist, front right US. 
     dist, lidar US. dist, rear US. dist, IMU yaw (deg)]
- Respond only using tools. If unsafe or unclear, call `no_op` with a safe 
  fallback and a short reason.
- Rings per scan is inversely proportional to angular resolution. Better resolution
  occurs with higher ring scans. Use only multiples of 200 rings when configuring
  rings per scan.
- Target 400 ring scans unless you believe a higher resolution scan is warranted
  and take a scan once for every 5 times you move. Ring count will latch.
"""
context_msg = {"role": "system", "content": system_context}


cam_recording = False
num_rings = 400

def build_new_input(recording, rings, last_tel_idx : int) -> tuple[list[int], int]:
    """
    [uptime, remaining storage in GB, scan resolution, camera connected, 
     camera recording, 
     front left mot. amps, mid left mot. amps, rear left mot. amps, 
     front right mot. amps, mid right mot. amps, rear right mot. amps, 
     front left ultrasonic dist (cm), front center US. dist, front right US. 
     dist, lidar US. dist, rear US. dist, IMU yaw (deg)]
    """

    lf_us = random.randint(10, 300)
    cf_us = random.randint(10, 300)
    rf_us = random.randint(10, 300)
    li_us = random.randint(10, 300)
    rr_us = random.randint(10, 300)
    
    telemetry = [
        12, 101.2, rings, True, recording, 
        0.8, 0.84, 0.88, 0.81, 0.8, 0.8,
        lf_us, cf_us, rf_us, li_us, rr_us, 0.0]
    curr_tel_idx = 1

    return telemetry, curr_tel_idx

# Define available tools for the rover autopilot
aegis_tools = [
    {
        "type": "function",
        "function": {
            "name": "scan",
            "description": (
                "Captures a high-res LiDAR scan of the rover's surroundings."
                "Use this to gather detailed environmental data whenever"
                "telemetry suggests anything worth scanning, or if it has been"
                "a while since the last scan."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "order_movement",
            "description": (
                "Issues movement commands to the rover."
                "Use this to move or turn the rover."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "enum": ["TURN", "MOVE"],
                        "description": (
                            "Type of movement."
                            "Either TURN (rotational) or MOVE (linear)."
                        )
                    },
                    "spd": {
                        "type": "number",
                        "description": (
                            "Speed factor in range [-1, 1]."
                            "Required for MOVE and TURN."
                            "Positive only for TURN."
                        )
                    },
                    "turn_dir": {
                        "type": "string",
                        "enum": ["LEFT", "RIGHT"],
                        "description": (
                            "Turn direction. Only used when op is TURN."
                        )
                    }
                },
                "required": ["op", "spd"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "no_op",
            "description": (
                "Signal that no safe/clear action can be taken now."
            ),
            "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type":"string", "description":"Why action is deferred."},
                "confidence": {
                "type":"number", "minimum":0, "maximum":1,
                "description":"Model confidence that doing nothing is correct."
                },
                "needs": {
                "type":"array",
                "items":{"type":"string"},
                "description":"Specific data/information needed to proceed."
                }
            },
            "required": ["reason"]
            }
        }
    }
]

# Ring buffer with system context, will hold last N prompts (N = memory depth)
history = [context_msg]
mem_depth = 10

last_telemetry_idx = 0

while True:

    # Get most recent telemetry slice and track last slice index
    new_tel, last_telemetry_idx = build_new_input(cam_recording, num_rings, last_telemetry_idx)


    # Circular buffer with system context and last N iteration commands
    history = [ {"role": "system", "content": system_context} ]
    history.append(
        {"role": "user", "content": json.dumps(new_tel)}
    )

    start_time = time.perf_counter()
    # Prompt the model with tools and telemetry
    response = client.chat.completions.create(
        model="gpt-5",
        store=True,
        messages=history,                   # type: ignore
        tools=aegis_tools,                  # type: ignore
        tool_choice="auto",         # auto, none, required
        temperature=1     # Token probability differential (creativity) [0,2]
    )

    print("\n\n")
    print(f"Took {round(time.perf_counter() - start_time, 3)} seconds.")

    print(f"INPUT: {new_tel}") 

    print(f"HISTORY: {history}")

    msg = response.choices[0].message
    #history.append({"role": "assistant", "content": msg.content or ""})

    print(f"MESSAGE: {msg.content}")

    for toolcall in (msg.tool_calls or []):
        name = toolcall.function.name                           # type: ignore
        args = json.loads(toolcall.function.arguments or "{}")  # type: ignore
        match name:


            case _: # Default
                print(f"Called {name} with args {args}.")


    # Wait
    time.sleep(2)