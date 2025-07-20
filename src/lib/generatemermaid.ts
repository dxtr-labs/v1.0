export function generateMermaidDiagram(nodes: any[], connections: any): string {
  if (!nodes?.length) return 'graph TD\n  Empty[No nodes found]';

  const ids: Record<string, string> = {};
  const lines: string[] = ['graph TD'];

  nodes.forEach((node: any, idx: number) => {
    const nodeId = `n${idx}`;
    const label = node.name + '\\n(' + node.type.replace('n8n-nodes-base.', '') + ')';
    lines.push(`${nodeId}["${label}"]`);
    ids[node.name] = nodeId;
  });

  Object.entries(connections).forEach(([sourceName, conns]) => {
    const sourceId = ids[sourceName];
    if (!sourceId) return;

    const outputs = (conns as any).main || [];
    outputs.forEach((connList: any[]) => {
      connList?.forEach((conn) => {
        const targetId = ids[conn.node];
        if (targetId) lines.push(`${sourceId} --> ${targetId}`);
      });
    });
  });

  return lines.join('\n');
}
