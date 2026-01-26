// Mind Map Visualization Logic

let simulation;
let isPaused = false;
let mindmapData = null;  // Store loaded data
let svg, g, tooltip;

async function loadMindMap() {
    if (mindmapData) {
        // If already loaded, just ensure simulation is running (or restart if needed for layout fix)
        // console.log("Mind map already loaded");
        if (simulation) simulation.alpha(0.1).restart();
        return;
    }

    const container = document.getElementById('mindmap-container');
    container.innerHTML = '<div class="loading-spinner">🧠 Generating Graph...</div>';

    try {
        const response = await fetch('/api/graph/mindmap');
        const data = await response.json();

        if (data.error) throw new Error(data.error);
        if (!data.nodes || data.nodes.length === 0) throw new Error("No video data found. Index some playlists first!");

        mindmapData = data;
        renderMindMap(data);

    } catch (error) {
        console.error("Mind Map Error:", error);
        container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">❌</div>
                <p>Failed to load Mind Map</p>
                <p class="error-detail">${error.message}</p>
            </div>
        `;
    }
}

function renderMindMap(data) {
    const container = document.getElementById('mindmap-container');
    container.innerHTML = '';

    // Create UI controls
    const controls = document.createElement('div');
    controls.className = 'mindmap-controls';
    controls.innerHTML = `
        <div class="control-group">
            <label>Connection Type:</label>
            <select id="connectionType" onchange="updateGraphFilter()">
                <option value="tags">By Tags (Topic Clusters)</option>
                <option value="channel">By Channel</option>
                <option value="all">All Connections</option>
            </select>
        </div>
        <div class="control-actions">
            <button onclick="resetSimulation()" class="control-btn">🔄 Reset</button>
            <button onclick="toggleSimulation()" class="control-btn" id="pauseBtn">⏸️ Pause</button>
            <button onclick="centerGraph()" class="control-btn">⊙ Center</button>
        </div>
    `;
    container.appendChild(controls);

    // Create SVG
    const width = container.clientWidth;
    const height = 800;

    // Create Stats
    const stats = document.createElement('div');
    stats.className = 'graph-stats';
    stats.innerHTML = `
        <h3>📊 Graph Stats</h3>
        <div class="stat-item">Nodes: <span class="stat-value">${data.meta.nodeCount}</span></div>
        <div class="stat-item">Edges: <span class="stat-value">${data.meta.edgeCount}</span></div>
        <div class="stat-item">Communities: <span class="stat-value">${data.meta.communityCount}</span></div>
    `;
    container.appendChild(stats);

    // Create Tooltip
    tooltip = d3.select("body").append("div")
        .attr("class", "graph-tooltip")
        .style("opacity", 0);

    // D3 Setup
    svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("class", "mindmap-svg");

    g = svg.append("g");

    // Zoom
    const zoom = d3.zoom()
        .scaleExtent([0.1, 8])
        .on("zoom", (event) => g.attr("transform", event.transform));

    svg.call(zoom);

    // Color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Expose control functions globally FIRST
    window.resetSimulation = () => {
        if (simulation) simulation.alpha(1).restart();
        svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    };

    window.toggleSimulation = () => {
        const btn = document.getElementById('pauseBtn');
        if (isPaused) {
            simulation.restart();
            btn.textContent = '⏸️ Pause';
            isPaused = false;
        } else {
            simulation.stop();
            btn.textContent = '▶️ Resume';
            isPaused = true;
        }
    };

    window.centerGraph = () => {
        svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
    };

    // Define update function
    const updateGraphFilter = (type) => {
        const selectedType = type || document.getElementById('connectionType').value;
        createForceGraph(data, selectedType, width, height, color);
    };
    // Expose it globally for the select onchange event
    window.updateGraphFilter = updateGraphFilter;

    // Initialize simulation with Tag data by default
    updateGraphFilter('tags');
}

function createForceGraph(data, type, width, height, color) {
    // Stop previous simulation
    if (simulation) simulation.stop();
    g.selectAll("*").remove();

    // Filter links based on type
    const links = data.links.filter(l => type === 'all' || l.type === type).map(d => Object.create(d));
    const nodes = data.nodes.map(d => Object.create(d));

    // Simulation
    simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).strength(0.5).distance(d => 100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(20));

    // Draw Links
    const link = g.append("g")
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", d => Math.sqrt(d.value));

    // Draw Nodes
    const node = g.append("g")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    node.append("circle")
        .attr("r", 8)
        .attr("fill", d => color(d.group))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5);

    // Labels
    node.append("text")
        .text(d => d.label.length > 20 ? d.label.substring(0, 18) + '...' : d.label)
        .attr("x", 12)
        .attr("y", 4)
        .style("font-size", "10px")
        .style("fill", "#333")
        .style("pointer-events", "none");

    // Interactivity
    node.on("mouseover", (event, d) => {
        // Highlight
        link.style("stroke", l => (l.source === d || l.target === d) ? "#667eea" : "#999")
            .style("stroke-opacity", l => (l.source === d || l.target === d) ? 1 : 0.1);

        // Tooltip
        tooltip.transition().duration(200).style("opacity", .9);
        tooltip.html(`
            <div class="tooltip-title">${d.label}</div>
            <div class="tooltip-meta">📺 ${d.channel}</div>
            <div class="tooltip-tags">${d.tags.join(', ')}</div>
        `)
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 28) + "px");
    })
        .on("mouseout", () => {
            link.style("stroke", "#999").style("stroke-opacity", 0.6);
            tooltip.transition().duration(500).style("opacity", 0);
        })
        .on("click", (event, d) => {
            if (d.url) window.open(d.url, '_blank');
        });

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
}
