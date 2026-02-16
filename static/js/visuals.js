// Trends Chart
window.initTrendChart = function () {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    // Destroy existing chart if any
    if (window.myTrendChart) window.myTrendChart.destroy();

    window.myTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: 'Citations',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: '#0ea5e9',
                backgroundColor: 'rgba(14, 165, 233, 0.2)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Keyword: "Attention"',
                data: [2, 10, 25, 45, 60, 80],
                borderColor: '#f472b6',
                borderDash: [5, 5],
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });
};

// Network Graph
window.initNetworkGraph = function () {
    const container = document.getElementById('network-container');
    if (!container) return;

    // Data provided by the backend (mocked here)
    const data = {
        nodes: [
            { id: 1, label: 'Transformer', color: '#0ea5e9', shape: 'dot', size: 30 },
            { id: 2, label: 'BERT', color: '#8b5cf6', shape: 'dot', size: 25 },
            { id: 3, label: 'GPT-3', color: '#f472b6', shape: 'dot', size: 25 },
            { id: 4, label: 'Attention', color: '#ffffff', shape: 'dot', size: 20 },
            { id: 5, label: 'NLP', color: '#ffffff', shape: 'dot', size: 20 }
        ],
        edges: [
            { from: 1, to: 2 },
            { from: 1, to: 3 },
            { from: 4, to: 1 },
            { from: 5, to: 2 },
            { from: 5, to: 3 }
        ]
    };

    const options = {
        nodes: {
            font: { color: '#ffffff' },
            borderWidth: 2
        },
        edges: {
            color: 'rgba(255,255,255,0.3)',
            smooth: true
        },
        physics: {
            stabilization: false,
            barnesHut: {
                gravitationalConstant: -2000
            }
        },
        interaction: { hover: true }
    };

    new vis.Network(container, data, options);
};
