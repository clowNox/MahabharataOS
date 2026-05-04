"use client";

import { useCallback, useEffect } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Handle,
  Position,
  type Node as ReactFlowNode,
  type Edge as ReactFlowEdge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DelegationNodeData } from "@/components/ExecutionStepper";

export interface AgentNodeData extends Record<string, unknown> {
  department: string;
  title: string;
  subtitle: string;
  badgeVariant: "default" | "secondary" | "outline" | "destructive";
  badgeClassName: string;
  model_choice: string;
  estimated_time_minutes: number;
}

// Custom Node Component
const AgentNode = ({ data }: { data: AgentNodeData }) => {
  return (
    <div className="bg-card border border-border shadow-md rounded-xl text-foreground min-w-[250px] p-4 max-w-[300px]">
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-primary border-2 border-background" />
      <div className="flex flex-col gap-2">
        <Badge variant={data.badgeVariant || "default"} className={data.badgeClassName + " w-fit"}>
          {data.department}
        </Badge>
        <span className="font-semibold text-sm leading-tight">{data.title}</span>
        <span className="text-xs text-muted-foreground leading-relaxed">{data.subtitle}</span>
        <div className="mt-2 pt-2 border-t border-border/50 flex justify-between items-center text-[10px] font-mono text-muted-foreground">
          <span>{data.model_choice || "Auto"}</span>
          <span>{data.estimated_time_minutes}m</span>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-primary border-2 border-background" />
    </div>
  );
};

const nodeTypes = {
  agent: AgentNode,
};

const defaultInitialNodes: ReactFlowNode<AgentNodeData>[] = [
  {
    id: "empty",
    type: "agent",
    position: { x: 250, y: 150 },
    data: { 
      department: "System Standby",
      title: "Awaiting Objective",
      subtitle: "Enter a prompt above to orchestrate a delegation graph.",
      badgeVariant: "outline",
      badgeClassName: "text-muted-foreground border-dashed",
      model_choice: "N/A",
      estimated_time_minutes: 0
    },
  }
];

export default function DelegationBoard({ dataNodes = [] }: { dataNodes?: DelegationNodeData[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultInitialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<ReactFlowEdge>([]);

  useEffect(() => {
    if (!dataNodes || dataNodes.length === 0) return;

    const newNodes: ReactFlowNode<AgentNodeData>[] = [];
    const newEdges: ReactFlowEdge[] = [];
    
    // Parse backend schema to React Flow schema
    dataNodes.forEach((node, index) => {
      // Create a nice staggered layout for now
      const x = 250;
      const y = 50 + index * 200;

      newNodes.push({
        id: node.id,
        type: "agent",
        position: { x, y },
        data: { 
          department: node.receiver || node.department || "CEO Office",
          title: node.message || node.objective || "Objective Execution",
          subtitle: node.reason || "System-defined delegation path.",
          badgeVariant: index === 0 ? "default" : "secondary",
          badgeClassName: index === 0 ? "bg-primary text-primary-foreground" : "bg-blue-500/10 text-blue-500",
          model_choice: node.model_choice || "Auto",
          estimated_time_minutes: node.estimated_time_minutes || 0
        },
      });

      // Handle Dependencies
      if (node.dependency_ids && node.dependency_ids.length > 0) {
        node.dependency_ids.forEach((depId: string) => {
          newEdges.push({
            id: `e-${depId}-${node.id}`,
            source: depId,
            target: node.id,
            animated: true,
            style: { stroke: '#64748b', strokeWidth: 2 }
          });
        });
      } else if (index > 0) {
        // Fallback: Link to the previous node if no dependencies provided (sequential)
        newEdges.push({
          id: `e-${dataNodes[index-1].id}-${node.id}`,
          source: dataNodes[index-1].id,
          target: node.id,
          animated: true,
          style: { stroke: '#64748b', strokeWidth: 2 }
        });
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [dataNodes, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <Card className="w-full h-[600px] border-border/50 bg-card/50 backdrop-blur-xl overflow-hidden shadow-2xl relative">
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <h2 className="text-xl font-semibold flex items-center gap-2 text-foreground">
          Delegation Graph
        </h2>
        <p className="text-sm text-muted-foreground">Live visualization of execution path</p>
      </div>
      
      <CardContent className="p-0 h-full w-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          colorMode="dark"
          className="bg-transparent"
        >
          <Controls 
            className="bg-card border-border fill-foreground shadow-lg rounded-md overflow-hidden" 
            showInteractive={false}
          />
          <MiniMap 
            className="bg-card border border-border shadow-lg rounded-md" 
            maskColor="rgba(0,0,0,0.5)" 
            nodeColor="#334155"
          />
          <Background gap={16} size={1} color="#334155" className="opacity-40" />
        </ReactFlow>
      </CardContent>
    </Card>
  );
}
