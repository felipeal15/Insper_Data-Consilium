const canvas = document.getElementById('mapCanvas');
const ctx = canvas.getContext('2d');
const legend = document.getElementById('legend');
const variableSelect = document.getElementById('variableSelect');
const yearSelect = document.getElementById('yearSelect');
const perCapitaToggle = document.getElementById('perCapitaToggle');
const yearGroup = document.getElementById('yearGroup');
const perCapitaGroup = document.getElementById('perCapitaGroup');

const GEOJSON_URL = '../raw/geo/sp_municipios.geojson';
const DATA_URL = '../final/painel_feminicidio_sp.csv';
const YEARS = ['2022', '2023', '2024', '2025'];
const polygons = [];
const dataByMunicipio = new Map();
let selectedCodarea = null;
let currentMin = 0;
let currentMax = 1;

const VARIABLE_CONFIG = {
    feminicidios: {
        label: 'Feminicídios por 100 mil hab',
        unit: 'por 100 mil hab',
    },
    pib: {
        label: 'PIB 2022',
        unit: 'R$',
    },
    taxa_alfabetizacao: {
        label: 'Taxa de alfabetização',
        unit: '%',
        normalize: value => value * 100,
    },
    anos_medios_estudo: {
        label: 'Anos médios de estudo',
        unit: 'anos',
    },
    pct_ensino_medio: {
        label: '% Ensino médio completo',
        unit: '%',
        normalize: value => value * 100,
    },
    pct_ensino_superior: {
        label: '% Ensino superior completo',
        unit: '%',
        normalize: value => value * 100,
    },
    populacao_media_2022_2025: {
        label: 'População média 2022–2025',
        unit: 'hab',
    },
};

function splitCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (inQuotes) {
            if (char === '"') {
                if (line[i + 1] === '"') {
                    current += '"';
                    i += 1;
                } else {
                    inQuotes = false;
                }
            } else {
                current += char;
            }
        } else if (char === '"') {
            inQuotes = true;
        } else if (char === ',') {
            values.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    values.push(current);
    return values;
}

function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/).filter(line => line.trim() !== '');
    const headers = splitCSVLine(lines[0]);
    return lines.slice(1).map(line => {
        const values = splitCSVLine(line);
        const row = {};
        headers.forEach((key, index) => {
            const raw = values[index] ?? '';
            const num = Number(raw);
            row[key] = raw === '' || Number.isNaN(num) ? raw : num;
        });
        return row;
    });
}

function formatValue(value, variableKey) {
    if (value === null || value === undefined || value === '') {
        return 'n/d';
    }
    const config = VARIABLE_CONFIG[variableKey] || {};
    const formatter = config.normalize || (v => v);
    const actual = formatter(Number(value));
    if (Number.isNaN(actual)) {
        return 'n/d';
    }
    if (config.unit === '%') {
        return `${actual.toFixed(1)}%`;
    }
    if (config.unit === 'R$') {
        return `R$ ${actual.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}`;
    }
    if (config.unit === 'anos') {
        return `${actual.toFixed(1)} anos`;
    }
    if (config.unit === 'por 100 mil hab') {
        return `${actual.toFixed(2)} por 100 mil hab`;
    }
    return actual.toLocaleString('pt-BR', { maximumFractionDigits: 1 });
}

function getHeatColor(value, min, max) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return 'rgba(220,220,220,0.4)';
    }
    const normalized = min === max ? 0.5 : Math.max(0, Math.min(1, (value - min) / (max - min)));
    const hue = 240 - normalized * 200; // azul -> roxo/vermelho
    return `hsla(${hue}, 80%, ${45 + normalized * 25}%, 0.9)`;
}

function normalizeCoordinates(features) {
    const allLon = [];
    const allLat = [];

    features.forEach(feature => {
        const geometry = feature.geometry;
        if (!geometry) return;
        const coords = geometry.type === 'Polygon'
            ? geometry.coordinates
            : geometry.type === 'MultiPolygon'
                ? geometry.coordinates.flat(1)
                : [];

        coords.flat(1).forEach(([lon, lat]) => {
            allLon.push(lon);
            allLat.push(lat);
        });
    });

    const minLon = Math.min(...allLon);
    const maxLon = Math.max(...allLon);
    const minLat = Math.min(...allLat);
    const maxLat = Math.max(...allLat);
    const padding = 30;
    const width = canvas.width - padding * 2;
    const height = canvas.height - padding * 2;
    const lonRange = maxLon - minLon;
    const latRange = maxLat - minLat;
    const aspect = width / height;
    const geoAspect = lonRange / latRange;
    let scaleX = width / lonRange;
    let scaleY = height / latRange;
    if (geoAspect > aspect) {
        scaleY = scaleX;
    } else {
        scaleX = scaleY;
    }

    return { minLon, minLat, scaleX, scaleY, padding };
}

function getSelectedVariable() {
    return variableSelect.value;
}

function getSelectedYear() {
    return yearSelect.value;
}

function getSelectedPibMode() {
    return perCapitaToggle.checked;
}

function getValueForRow(row, variableKey, yearKey) {
    if (!row) return null;
    if (variableKey === 'feminicidios') {
        if (yearKey === 'all') {
            return row.feminicidios_per_100k_2022_2025 ?? null;
        }
        return row[`taxa_feminicidio_total_100k_${yearKey}`] ?? row[`taxa_feminicidio_consumado_100k_${yearKey}`] ?? null;
    }
    if (variableKey === 'pib') {
        return getSelectedPibMode() ? row.pib_per_capita_2022 : row.pib_2022;
    }
    return row[variableKey];
}

function getLegendLabel() {
    const variableKey = getSelectedVariable();
    const config = VARIABLE_CONFIG[variableKey] || {};
    if (variableKey === 'pib' && getSelectedPibMode()) {
        return 'PIB per capita 2022';
    }
    return config.label || variableKey;
}

function updateLegendText(min, max) {
    const label = getLegendLabel();
    const minText = formatValue(min, getSelectedVariable());
    const maxText = formatValue(max, getSelectedVariable());
    legend.textContent = `${label} — intervalo de ${minText} até ${maxText}`;
}

function updateControlsVisibility() {
    const variableKey = getSelectedVariable();

    if (variableKey === 'feminicidios') {
        yearGroup.style.display = 'flex';
        yearSelect.disabled = false;
        perCapitaGroup.style.display = 'none';
        perCapitaToggle.disabled = true;
        perCapitaToggle.checked = false;
    } else if (variableKey === 'pib') {
        yearGroup.style.display = 'none';
        yearSelect.disabled = true;
        yearSelect.value = 'all';
        perCapitaGroup.style.display = 'flex';
        perCapitaToggle.disabled = false;
    } else {
        yearGroup.style.display = 'none';
        yearSelect.disabled = true;
        yearSelect.value = 'all';
        perCapitaGroup.style.display = 'none';
        perCapitaToggle.disabled = true;
        perCapitaToggle.checked = false;
    }
}

function drawPolygons() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    polygons.forEach(item => {
        const isSelected = item.codarea === selectedCodarea;
        ctx.beginPath();
        item.regions.forEach(region => {
            region.forEach((point, index) => {
                if (index === 0) {
                    ctx.moveTo(point.x, point.y);
                } else {
                    ctx.lineTo(point.x, point.y);
                }
            });
            ctx.closePath();
        });
        ctx.fillStyle = item.fillColor || 'rgba(220,220,220,0.4)';
        ctx.fill();
        ctx.lineWidth = isSelected ? 1.8 : 0.4;
        ctx.strokeStyle = isSelected ? '#ff9800' : '#555';
        ctx.stroke();
    });
}

function getClickedCodarea(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    for (let i = polygons.length - 1; i >= 0; i--) {
        const item = polygons[i];
        ctx.beginPath();
        item.regions.forEach(region => {
            region.forEach((point, index) => {
                if (index === 0) {
                    ctx.moveTo(point.x, point.y);
                } else {
                    ctx.lineTo(point.x, point.y);
                }
            });
            ctx.closePath();
        });
        if (ctx.isPointInPath(x, y)) {
            return item.codarea;
        }
    }
    return null;
}

function updateOutputText() {
    if (!selectedCodarea) {
        return;
    }
}

function updatePolygonsValues() {
    const variableKey = getSelectedVariable();
    const yearKey = getSelectedYear();
    const values = [];

    polygons.forEach(item => {
        const row = dataByMunicipio.get(String(item.codarea));
        const value = getValueForRow(row, variableKey, yearKey);
        item.value = value;
        if (value !== null && value !== undefined && !Number.isNaN(value)) {
            values.push(Number(value));
        }
    });

    currentMin = values.length ? Math.min(...values) : 0;
    currentMax = values.length ? Math.max(...values) : currentMin;
    polygons.forEach(item => {
        item.fillColor = getHeatColor(item.value, currentMin, currentMax);
    });
    updateLegendText(currentMin, currentMax);
}

function onSelectionChange() {
    updateControlsVisibility();
    updatePolygonsValues();
    drawPolygons();
    updateOutputText();
}

function loadMapData() {
    return Promise.all([
        fetch(GEOJSON_URL).then(resp => {
            if (!resp.ok) throw new Error('Falha ao carregar GeoJSON');
            return resp.json();
        }),
        fetch(DATA_URL).then(resp => {
            if (!resp.ok) throw new Error('Falha ao carregar os dados do mapa');
            return resp.text();
        }),
    ]).then(([geojson, csvText]) => {
        const csvRows = parseCSV(csvText);

        csvRows.forEach(row => {
            const id = String(row.id_municipio);
            const current = dataByMunicipio.get(id) || {
                id_municipio: row.id_municipio,
                municipio: row.municipio,
                n_total_2022: 0,
                n_total_2023: 0,
                n_total_2024: 0,
                n_total_2025: 0,
                taxa_feminicidio_total_100k_2022: 0,
                taxa_feminicidio_total_100k_2023: 0,
                taxa_feminicidio_total_100k_2024: 0,
                taxa_feminicidio_total_100k_2025: 0,
                taxa_feminicidio_consumado_100k_2022: 0,
                taxa_feminicidio_consumado_100k_2023: 0,
                taxa_feminicidio_consumado_100k_2024: 0,
                taxa_feminicidio_consumado_100k_2025: 0,
            };

            const year = String(row.ano);
            current.municipio = row.municipio || current.municipio;
            current.populacao_2022 = (current.populacao_2022 || 0) + (year === '2022' ? (Number(row.populacao) || 0) : 0);
            current.populacao_2023 = (current.populacao_2023 || 0) + (year === '2023' ? (Number(row.populacao) || 0) : 0);
            current.populacao_2024 = (current.populacao_2024 || 0) + (year === '2024' ? (Number(row.populacao) || 0) : 0);
            current.populacao_2025 = (current.populacao_2025 || 0) + (year === '2025' ? (Number(row.populacao) || 0) : 0);
            current.pib_per_capita_2022 = Number(row.pib_per_capita_2022) || current.pib_per_capita_2022 || 0;
            current.taxa_alfabetizacao = Number(row.taxa_alfabetizacao) || current.taxa_alfabetizacao || 0;
            current.anos_medios_estudo = Number(row.anos_medios_estudo) || current.anos_medios_estudo || 0;
            current.pct_ensino_medio = Number(row.pct_ensino_medio) || current.pct_ensino_medio || 0;
            current.pct_ensino_superior = Number(row.pct_ensino_superior) || current.pct_ensino_superior || 0;
            current.taxa_urbanizacao_pct = Number(row.taxa_urbanizacao_pct) || current.taxa_urbanizacao_pct || 0;
            current.taxa_saneamento_basico_pct = Number(row.taxa_saneamento_basico_pct) || current.taxa_saneamento_basico_pct || 0;
            current.taxa_trafico_drogas_100k = Number(row.taxa_trafico_drogas_100k) || current.taxa_trafico_drogas_100k || 0;

            current[`n_total_${year}`] = (current[`n_total_${year}`] || 0) + (Number(row.n_total) || 0);
            current[`taxa_feminicidio_total_100k_${year}`] = Number(row.taxa_feminicidio_total_100k) || 0;
            current[`taxa_feminicidio_consumado_100k_${year}`] = Number(row.taxa_feminicidio_consumado_100k) || 0;

            dataByMunicipio.set(id, current);
        });

        dataByMunicipio.forEach(row => {
            const years = ['2022', '2023', '2024', '2025'];
            const totalRate = years.reduce((sum, year) => sum + (Number(row[`taxa_feminicidio_total_100k_${year}`]) || 0), 0);
            row.feminicidios_per_100k_2022_2025 = totalRate / years.length;
            row.populacao_media_2022_2025 = years.reduce((sum, year) => sum + (Number(row[`populacao_${year}`]) || 0), 0) / years.length;
            row.pib_2022 = (Number(row.pib_per_capita_2022) || 0) * (Number(row.populacao_2022) || 0);
        });

        const features = geojson.features || [];
        if (!features.length) throw new Error('GeoJSON sem features');
        const meta = normalizeCoordinates(features);

        features.forEach(feature => {
            const geometry = feature.geometry;
            const codarea = feature.properties?.codarea;
            if (!geometry || !codarea) return;
            const rawPolygons = geometry.type === 'Polygon'
                ? [geometry.coordinates]
                : geometry.type === 'MultiPolygon'
                    ? geometry.coordinates
                    : [];
            const regions = rawPolygons.map(polygon => {
                return polygon[0].map(([lon, lat]) => ({
                    x: meta.padding + (lon - meta.minLon) * meta.scaleX,
                    y: canvas.height - meta.padding - (lat - meta.minLat) * meta.scaleY,
                }));
            }).filter(region => region.length);
            if (regions.length) {
                polygons.push({ codarea, regions, value: null, fillColor: 'rgba(220,220,220,0.4)' });
            }
        });

        updateControlsVisibility();
        updatePolygonsValues();
        drawPolygons();
    });
}

const tooltip = document.getElementById('tooltip');

function showTooltip(event, codarea) {
    const row = dataByMunicipio.get(String(codarea));
    if (!row) return;
    const label = getLegendLabel();
    const value = formatValue(getValueForRow(row, getSelectedVariable(), getSelectedYear()), getSelectedVariable());
    tooltip.innerHTML = `<strong>${row.municipio || codarea}</strong><br>${label}: ${value}`;
    tooltip.style.left = `${event.clientX + 12}px`;
    tooltip.style.top = `${event.clientY + 12}px`;
    tooltip.style.display = 'block';
}

function hideTooltip() {
    tooltip.style.display = 'none';
}

canvas.addEventListener('mousemove', event => {
    const codarea = getClickedCodarea(event);
    if (codarea) {
        showTooltip(event, codarea);
    } else {
        hideTooltip();
    }
});

canvas.addEventListener('mouseleave', hideTooltip);

canvas.addEventListener('click', event => {
    const codarea = getClickedCodarea(event);
    selectedCodarea = codarea;
    drawPolygons();
    updateOutputText();
});

variableSelect.addEventListener('change', onSelectionChange);
yearSelect.addEventListener('change', onSelectionChange);
perCapitaToggle.addEventListener('change', onSelectionChange);

loadMapData().catch(error => {
    console.error(error);
    legend.textContent = 'Erro: ' + error.message;
});