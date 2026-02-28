import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { GlassCard } from './GlassUI';

const MindMap: React.FC = () => {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!svgRef.current || !containerRef.current) return;

        const width = containerRef.current.clientWidth;
        const height = 600;

        // Clear previous
        d3.select(svgRef.current).selectAll("*").remove();

        const svg = d3.select(svgRef.current)
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height]);

        // Mock Graph Data
        const nodes = [
            { id: "Root", group: 1, r: 40 },
            { id: "React", group: 2, r: 30 },
            { id: "Web Dev", group: 2, r: 35 },
            { id: "Music", group: 3, r: 30 },
            { id: "Nature", group: 4, r: 25 },
            { id: "Hooks", group: 2, r: 20 },
            { id: "Components", group: 2, r: 20 },
            { id: "CSS", group: 2, r: 20 },
            { id: "Jazz", group: 3, r: 20 },
            { id: "Ocean", group: 4, r: 20 },
        ];

        const links = [
            { source: "Root", target: "React" },
            { source: "Root", target: "Web Dev" },
            { source: "Root", target: "Music" },
            { source: "Root", target: "Nature" },
            { source: "React", target: "Hooks" },
            { source: "React", target: "Components" },
            { source: "Web Dev", target: "CSS" },
            { source: "Music", target: "Jazz" },
            { source: "Nature", target: "Ocean" },
        ];

        const simulation = d3.forceSimulation(nodes as any)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .attr("stroke", "rgba(255,255,255,0.2)")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", 2);

        const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("g")
            .data(nodes)
            .join("g")
            .call(d3.drag<any, any>()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Glass bubble look for nodes
        node.append("circle")
            .attr("r", (d: any) => d.r)
            .attr("fill", (d: any) => {
                const colors = ["#8b5cf6", "#06b6d4", "#ec4899", "#10b981"];
                return colors[(d.group - 1) % colors.length];
            })
            .attr("fill-opacity", 0.6)
            .attr("stroke", "rgba(255,255,255,0.5)");
            
        // Inner shine
        node.append("circle")
             .attr("r", (d: any) => d.r * 0.7)
             .attr("fill", "url(#grad1)")
             .attr("fill-opacity", 0.3)
             .style("filter", "blur(2px)");

        node.append("text")
            .text((d: any) => d.id)
            .attr("text-anchor", "middle")
            .attr("dy", ".35em")
            .attr("fill", "white")
            .style("font-size", "10px")
            .style("font-weight", "bold")
            .style("pointer-events", "none")
            .attr("stroke", "none");

        // Define gradients
        const defs = svg.append("defs");
        const gradient = defs.append("radialGradient")
            .attr("id", "grad1")
            .attr("cx", "30%")
            .attr("cy", "30%")
            .attr("r", "50%");
        gradient.append("stop").attr("offset", "0%").style("stop-color", "white").style("stop-opacity", 0.8);
        gradient.append("stop").attr("offset", "100%").style("stop-color", "white").style("stop-opacity", 0);

        simulation.on("tick", () => {
            link
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            node
                .attr("transform", (d: any) => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event: any, d: any) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Clean up
        return () => {
            simulation.stop();
        };

    }, []);

    return (
        <GlassCard className="h-full w-full p-0 overflow-hidden" title="Knowledge Graph">
            <div ref={containerRef} className="w-full h-[600px] bg-black/20 rounded-b-3xl">
                <svg ref={svgRef} className="w-full h-full cursor-move"></svg>
            </div>
        </GlassCard>
    );
};

export default MindMap;
