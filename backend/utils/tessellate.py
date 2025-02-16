from ocp_tessellate.convert import to_assembly
from ocp_tessellate import OCP_PartGroup
from ocp_tessellate.convert import (
    tessellate_group,
    to_assembly,
)

def tessellate(
    *cad_objs, names=None, colors=None, alphas=None, progress=None, **kwargs
):
    global FIRST_CALL
    print("calling to assembly")  
    part_group, instances = to_assembly(
        *cad_objs,
        names=names,
        colors=colors,
        alphas=alphas,
        progress=progress,
    )
    print("after to assembly")

    if len(part_group.objects) == 1 and isinstance(
        part_group.objects[0], OCP_PartGroup
    ):
        part_group = part_group.objects[0]

    print("Calling to tesellate")
    instances, shapes, states  = tessellate_group(part_group, instances)
    print("After to tesellate")

    return shapes, states
