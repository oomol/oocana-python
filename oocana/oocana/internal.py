from .mainframe import Mainframe
from .data import JobDict
import random
import string
import math

class InternalAPI:

    def __init__(self, client: Mainframe, job_id: JobDict) -> None:
        self._client = client
        self._job_id = job_id

    # keep this method async for future use
    async def update_node_weight(self, node_id: str, weight: int | float) -> None:
        """
        Update the weight of a node.
        :param node_id: The ID of the node to update.
        :param weight: The new weight for the node.
        """
        if not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight < 0:
            raise ValueError("Weight must be a non-negative finite number.")

        self._client.send(self._job_id, {
            "type": "BlockRequest",
            "action": "UpdateNodeWeight",
            "node_id": node_id,
            "weight": weight,
            "request_id": random_string(16),
        })

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
