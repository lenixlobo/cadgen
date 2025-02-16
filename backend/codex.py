import importlib
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

from openai.types.chat import ChatCompletion
from openai.types.chat import ChatCompletionMessage
from openai.types import CompletionUsage
from openai.types.chat.chat_completion import Choice

load_dotenv()
openai.api_key = "ollama"

import re
def somecleanup(s):
    match = re.search((r'\`\`\`python(.*?)\`\`\`'),s,re.DOTALL)
    return match.group(1) if match else None

def generate_cq_obj(user_msg: str):
    # Define the system message
    system_msg = """
    You are a strict assistant, translating natural language to the python code.
    Please do not explain, just write code. VERY IMPORTANT to name the output variable obj and do not use show_object or any show functions.
    here is the Cadquery API as a helpful resource:
    
    wp.center(x, y) : Shift local coordinates to the specified location.
    wp.lineTo(x, y[, forConstruction]) : Make a line from the current point to the provided point
    wp.line(xDist, yDist[, forConstruction]) : Make a line from the current point to the provided point, using dimensions relative to the current point
    wp.vLine(distance[, forConstruction]) : Make a vertical line from the current point the provided distance
    wp.vLineTo(yCoord[, forConstruction]) : Make a vertical line from the current point to the provided y coordinate.
    wp.hLine(distance[, forConstruction]) : Make a horizontal line from the current point the provided distance
    wp.hLineTo(xCoord[, forConstruction]): Make a horizontal line from the current point to the provided x coordinate.
    wp.polarLine(distance, angle[, ...])- Make a line of the given length, at the given angle from the current point
    wp.polarLineTo(distance, angle[, ...]) : Make a line from the current point to the given polar coordinates
    wp.moveTo([x, y]) : Move to the specified point, without drawing.
    wp.move([xDist, yDist]) : Move the specified distance from the current point, without drawing.
    wp.spline(listOfXYTuple[, tangents, ...]) : Create a spline interpolated through the provided points (2D or 3D).
    wp.parametricCurve(func[, N, start, ...]) : Create a spline curve approximating the provided function.
    wp.parametricSurface(func[, N, ...]) : Create a spline surface approximating the provided function.
    wp.threePointArc(point1, point2[, ...]) : Draw an arc from the current point, through point1, and ending at point2
    wp.sagittaArc(endPoint, sag[, ...]) : Draw an arc from the current point to endPoint with an arc defined by the sag (sagitta).
    wp.radiusArc(endPoint, radius[, ...]) : Draw an arc from the current point to endPoint with an arc defined by the radius.
    wp.tangentArcPoint(endpoint[, ...]) : Draw an arc as a tangent from the end of the current edge to endpoint.
    wp.mirrorY() : Mirror entities around the y axis of the workplane plane.
    wp.mirrorX() : Mirror entities around the x axis of the workplane plane.
    wp.wire([forConstruction]) : Returns a CQ object with all pending edges connected into a wire.
    wp.rect(xLen, yLen[, centered, ...]) : Make a rectangle for each item on the stack.
    wp.circle(radius[, forConstruction]) : Make a circle for each item on the stack.
    wp.ellipse(x_radius, y_radius[, ...]) : Make an ellipse for each item on the stack.
    wp.ellipseArc(x_radius, y_radius[, ...]) : Draw an elliptical arc with x and y radiuses either with start point at current point or or current point being the center of the arc
    wp.polyline(listOfXYTuple[, ...]) : Create a polyline from a list of points
    wp.close() : End construction, and attempt to build a closed wire.
    wp.rarray(xSpacing, ySpacing, xCount, ...) : Creates an array of points and pushes them onto the stack.
    wp.polarArray(radius, startAngle, ...) : Creates a polar array of points and pushes them onto the stack.
    wp.slot2D(length, diameter[, angle]) : Creates a rounded slot for each point on the stack.
    wp.offset2D(d[, kind, forConstruction]) : Creates a 2D offset wire.
    wp.placeSketch(*sketches) : Place the provided sketch(es) based on the current items on the stack.
    wp.gear(gear: BevelGear|CrossedHelicalGear|RackGear|RingGear|Worm) : Create a gear from the provided gear class.
    wp("XY").box(length, width, thickness) : Create a box of particular length, width and thickness

    Here are also some gear classes from the library, use this as input argument to wp.gear

    Bevel Gear : cq_gears.BevelGear(module, teeth_number, cone_angle, face_width, pressure_angle=20.0, helix_angle=0.0, clearance=0.0, backlash=0.0, bore_d)
    CrossedHelicalGear : cq_gears.CrossedHelicalGear(module, teeth_number, width, pressure_angle=20.0, helix_angle=0.0, clearance=0.0, backlash=0.0, bore_d)
    RackGear : cq_gears.RackGear(module, length, width, height, pressure_angle=20.0, helix_angle=0.0, clearance=0.0, backlash=0.0, bore_d)
    RingGear : cq_gears.RingGear(module, teeth_number, width, rim_width, pressure_angle=20.0, helix_angle=0.0, clearance=0.0, backlash=0.0, bore_d)
    Worm : cq_gears.Worm(module, lead_angle, n_threads, length, pressure_angle=20.0, clearance=0.0, backlash=0.0, bore_d)
    SpurGear : cq_gears.SpurGear(self, module, teeth_number, width, pressure_angle=20.0, helix_angle=0.0, clearance=0.0, backlash=0.0, bore_d)
    
    Here is a way to generate airfoils with the coordinates being fed into wp.polyline followed by a wp.polyline.close

    For NACA airfoils use get_coords() for the following classes

    parafoil.CamberThicknessAirfoil(inlet_angle, outlet_angle, chord_length, angle_units="rad"|"deg")
    parafoil.NACAAirfoil(naca_string, chord_length)
    
    Please use the following structure:

    ```python
    #define necessary variables
    #call the necessary function, with the defined variables are arguments

    ```
    """
    client = openai.OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
    )

    response = client.chat.completions.create(
        messages=[
            {
                'role':'system', 
                'content':system_msg
            },
            {
                'role':'user',
                'content':user_msg    
            }
        ],
        model="mistral"
    )

    id = datetime.now().isoformat().replace(":","-")

    # create directory "generated" if does not exist
    if not os.path.exists("generated"):
        os.makedirs("generated")

    print("This is the response")
    print (response)
    finalmessage = response.choices[0].message.content
    cleanupmessage = somecleanup(finalmessage)
    cleanupmessage = "obj = cq.Workplane(\"XY\").box(3, 3, 0.5).edges(\"|Z\").fillet(0.125)"
    print("This is after cleanup")
    print(cleanupmessage)
    file_name = f"generated/{id}.py"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(
            f'import cadquery as cq\nimport cq_gears\nimport parafoil\nfrom cadquery import Workplane as wp\n{cleanupmessage}'
        )

    spec = importlib.util.spec_from_file_location("obj_module", file_name)
    obj_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj_module)
    return id, obj_module.obj