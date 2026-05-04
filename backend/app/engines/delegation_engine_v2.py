from typing import List, Dict, Any
from app.models.orchestration import (
    DelegationNode,
    ExecutionStep,
    ContextPacket,
    new_id,
)


def create_delegation_chain(
    delegation_plan: List[ExecutionStep],
    task_id: str,
    context_packet: ContextPacket
) -> List[DelegationNode]:
    nodes: List[DelegationNode] = []

    for step in delegation_plan:
        if not step.depends_on:
            sender = "CEO Office"
        else:
            parent_step = next(
                (s for s in delegation_plan if s.id == step.depends_on[0]),
                None
            )
            sender = parent_step.department if parent_step else "CEO Office"

        node = DelegationNode(
            id=step.id,
            task_id=task_id,
            context_packet_id=context_packet.id,
            sender=sender,
            receiver=step.department,
            message=step.objective,
            reason=step.reason,
            expected_input=step.expected_input,
            expected_output=step.expected_output,
            output_schema=step.output_schema,
            dependency_ids=step.depends_on,
            status="pending",
            editable=True,
            estimated_time_minutes=step.estimated_time_minutes,
            model_choice=step.model_choice,
            confidence_score=step.confidence_score
        )

        nodes.append(node)

    return nodes


def validate_delegation_chain(nodes: List[DelegationNode]) -> Dict[str, Any]:
    errors = []

    node_ids = {node.id for node in nodes}

    for node in nodes:
        for dep in node.dependency_ids:
            if dep not in node_ids:
                errors.append(
                    f"Node {node.id} depends on missing dependency {dep}."
                )

        if not node.receiver:
            errors.append(f"Node {node.id} has no receiver.")

        if not node.expected_output:
            errors.append(f"Node {node.id} has no expected output.")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def update_delegation_chain(
    existing_nodes: List[DelegationNode],
    updates: List[Dict[str, Any]]
) -> List[DelegationNode]:
    """
    Allows user to edit delegation flow.

    Supported updates:
    - change receiver
    - change priority indirectly through estimated time
    - add dependency
    - remove dependency
    - mark node skipped
    - update expected output
    """

    node_map = {node.id: node for node in existing_nodes}

    for update in updates:
        node_id = update.get("node_id")

        if node_id not in node_map:
            continue

        node = node_map[node_id]

        if not node.editable:
            continue

        if "receiver" in update:
            node.receiver = update["receiver"]

        if "message" in update:
            node.message = update["message"]

        if "expected_output" in update:
            node.expected_output = update["expected_output"]

        if "dependency_ids" in update:
            node.dependency_ids = update["dependency_ids"]

        if "status" in update:
            node.status = update["status"]

    return list(node_map.values())
