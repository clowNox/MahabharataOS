import uuid
from typing import List, Dict, Any
from app.models.domain import DelegationNode

def create_delegation_chain(delegation_plan: List[Dict[str, Any]], task_id: str) -> List[DelegationNode]:
    """
    Transforms the abstract CEO execution plan into explicit delegation nodes.
    Each node represents a distinct handoff in the system.
    """
    delegations = []
    
    for i, step in enumerate(delegation_plan):
        # The sender is the CEO Office for the first node, 
        # otherwise it's the department from the previous step.
        sender = "CEO Office" if i == 0 else steps[i-1]["department"]
        receiver = step["department"]
        
        node = DelegationNode(
            id=str(uuid.uuid4()),
            task_id=task_id,
            sender=sender,
            receiver=receiver,
            message=step["objective"],
            reason=step["reason"],
            expected_output=step["expected_output"],
            status="pending",
            editable=True
        )
        delegations.append(node)
        
    return delegations

def update_delegation_chain(task_id: str, current_nodes: List[DelegationNode], updated_nodes_data: List[Dict[str, Any]]) -> List[DelegationNode]:
    """
    Handles user edits to the delegation chain (e.g., from the React Flow board).
    In a real app, this would also handle database versioning.
    """
    # For MVP, we simply overwrite the chain with the new node definitions provided by the UI.
    new_chain = []
    
    for node_data in updated_nodes_data:
        # Reconstruct node or create new if it was added
        node = DelegationNode(
            id=node_data.get("id", str(uuid.uuid4())),
            task_id=task_id,
            sender=node_data.get("sender", "Unknown"),
            receiver=node_data.get("receiver", "Unknown"),
            message=node_data.get("message", "User added custom objective"),
            reason=node_data.get("reason", "User modified chain"),
            expected_output=node_data.get("expected_output", "N/A"),
            status=node_data.get("status", "pending"),
            editable=node_data.get("editable", True)
        )
        new_chain.append(node)
        
    return new_chain

def validate_chain(nodes: List[DelegationNode]) -> bool:
    """
    Validates that a delegation chain isn't broken (e.g., missing receivers, loops).
    """
    if not nodes:
        return False
        
    for i in range(len(nodes) - 1):
        # Basic validation: current receiver should be next sender (unless it's a parallel task, which we handle later)
        if nodes[i].receiver != nodes[i+1].sender:
            # Not strictly broken if we allow disjoint graphs, but for simple MVP chains:
            return False
            
    return True
