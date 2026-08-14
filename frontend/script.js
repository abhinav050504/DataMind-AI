// ============================================================
// DATAMIND AI - FRONTEND JAVASCRIPT
// ============================================================

const API_URL = "http://127.0.0.1:8000";

// ============================================================
// ELEMENTS
// ============================================================

const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const fileName = document.getElementById("fileName");

const dashboard = document.getElementById("dashboard");

const totalRecords = document.getElementById("totalRecords");
const totalColumns = document.getElementById("totalColumns");
const totalSales = document.getElementById("totalSales");
const averageSales = document.getElementById("averageSales");
const bestProduct = document.getElementById("bestProduct");
const lowestSales = document.getElementById("lowestSales");

const dashboardBars = document.getElementById("dashboardBars");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

const resultContainer = document.getElementById("resultContainer");
const answerContainer = document.getElementById("answerContainer");
const chartContainer = document.getElementById("chartContainer");

// ============================================================
// CURRENT FILE
// ============================================================

let selectedFile = null;

// ============================================================
// CHOOSE FILE
// ============================================================

uploadButton.addEventListener("click", function () {
    fileInput.click();
});

// ============================================================
// FILE SELECTED
// ============================================================

fileInput.addEventListener("change", async function () {

    const file = fileInput.files[0];

    if (!file) {
        return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {

        fileName.textContent = "Please select a CSV file.";

        return;
    }

    selectedFile = file;

    fileName.textContent = `Selected: ${file.name}`;

    await loadDashboard(file);
});

// ============================================================
// LOAD DASHBOARD
// ============================================================

async function loadDashboard(file) {

    dashboard.style.display = "block";

    totalRecords.textContent = "...";
    totalColumns.textContent = "...";
    totalSales.textContent = "...";
    averageSales.textContent = "...";
    bestProduct.textContent = "...";
    lowestSales.textContent = "...";

    dashboardBars.innerHTML = `
        <div class="loading-box">
            <div class="loader"></div>
            <p>Analyzing your dataset...</p>
        </div>
    `;

    try {

        // ----------------------------------------------------
        // READ CSV IN BROWSER
        // ----------------------------------------------------

        const text = await file.text();

        const rows = parseCSV(text);

        if (rows.length < 2) {
            throw new Error("The CSV file does not contain enough data.");
        }

        const headers = rows[0];

        const data = rows
            .slice(1)
            .filter(row => row.some(value => value.trim() !== ""));

        // ----------------------------------------------------
        // FIND SALES COLUMN
        // ----------------------------------------------------

        const salesColumn = findColumn(
            headers,
            [
                "Sales",
                "sales",
                "Sale",
                "sale",
                "Revenue",
                "revenue",
                "Amount",
                "amount",
                "Price",
                "price",
                "Value",
                "value"
            ]
        );

        // ----------------------------------------------------
        // FIND PRODUCT COLUMN
        // ----------------------------------------------------

        const productColumn = findColumn(
            headers,
            [
                "Product",
                "product",
                "Product Name",
                "product_name",
                "Item",
                "item",
                "Category",
                "category"
            ]
        );

        // ----------------------------------------------------
        // BASIC DATA
        // ----------------------------------------------------

        totalRecords.textContent = data.length;
        totalColumns.textContent = headers.length;

        // ----------------------------------------------------
        // SALES DATA
        // ----------------------------------------------------

        if (salesColumn !== null) {

            const salesIndex = headers.indexOf(salesColumn);

            const salesValues = data
                .map(row => parseNumber(row[salesIndex]))
                .filter(value => !isNaN(value));

            if (salesValues.length > 0) {

                const total = salesValues.reduce(
                    (sum, value) => sum + value,
                    0
                );

                const average = total / salesValues.length;

                const maximum = Math.max(...salesValues);

                const minimum = Math.min(...salesValues);

                totalSales.textContent = formatNumber(total);

                averageSales.textContent = formatNumber(average);

                lowestSales.textContent = formatNumber(minimum);

                // ------------------------------------------------
                // PRODUCT ANALYSIS
                // ------------------------------------------------

                if (productColumn !== null) {

                    const productIndex =
                        headers.indexOf(productColumn);

                    const productSales = {};

                    data.forEach(row => {

                        const product =
                            row[productIndex]?.trim();

                        const value =
                            parseNumber(row[salesIndex]);

                        if (
                            product &&
                            !isNaN(value)
                        ) {

                            if (!productSales[product]) {
                                productSales[product] = 0;
                            }

                            productSales[product] += value;
                        }
                    });

                    const ranking =
                        Object.entries(productSales)
                            .sort((a, b) => b[1] - a[1]);

                    if (ranking.length > 0) {

                        bestProduct.textContent =
                            ranking[0][0];

                        renderDashboardChart(ranking);

                        renderInsights(
                            ranking,
                            total
                        );

                    } else {

                        bestProduct.textContent = "N/A";

                        dashboardBars.innerHTML =
                            "<p>No product data found.</p>";
                    }

                } else {

                    bestProduct.textContent = "N/A";

                    dashboardBars.innerHTML =
                        "<p>No product column found.</p>";
                }

            } else {

                totalSales.textContent = "N/A";
                averageSales.textContent = "N/A";
                lowestSales.textContent = "N/A";
                bestProduct.textContent = "N/A";

                dashboardBars.innerHTML =
                    "<p>No numeric sales values found.</p>";
            }

        } else {

            totalSales.textContent = "N/A";
            averageSales.textContent = "N/A";
            lowestSales.textContent = "N/A";
            bestProduct.textContent = "N/A";

            dashboardBars.innerHTML =
                "<p>No sales column found.</p>";
        }

        // ----------------------------------------------------
        // DATASET PREVIEW
        // ----------------------------------------------------

        renderDatasetPreview(
            headers,
            data
        );

    } catch (error) {

        console.error(error);

        dashboardBars.innerHTML = `
            <div class="error-box">
                <strong>Dashboard Error</strong>
                ${escapeHTML(error.message)}
            </div>
        `;
    }
}

// ============================================================
// FIND COLUMN
// ============================================================

function findColumn(headers, possibleNames) {

    for (const name of possibleNames) {

        if (headers.includes(name)) {
            return name;
        }
    }

    return null;
}

// ============================================================
// PARSE NUMBER
// ============================================================

function parseNumber(value) {

    if (value === undefined || value === null) {
        return NaN;
    }

    return Number(
        String(value)
            .replace(/₹/g, "")
            .replace(/,/g, "")
            .trim()
    );
}

// ============================================================
// FORMAT NUMBER
// ============================================================

function formatNumber(value) {

    return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 2
    }).format(value);
}

// ============================================================
// CSV PARSER
// ============================================================

function parseCSV(text) {

    const rows = [];

    let row = [];
    let value = "";
    let insideQuotes = false;

    for (let i = 0; i < text.length; i++) {

        const character = text[i];
        const nextCharacter = text[i + 1];

        if (character === '"' && insideQuotes && nextCharacter === '"') {

            value += '"';

            i++;

        } else if (character === '"') {

            insideQuotes = !insideQuotes;

        } else if (character === "," && !insideQuotes) {

            row.push(value.trim());

            value = "";

        } else if (
            (character === "\n" || character === "\r") &&
            !insideQuotes
        ) {

            if (character === "\r" && nextCharacter === "\n") {
                i++;
            }

            row.push(value.trim());

            if (row.some(item => item !== "")) {
                rows.push(row);
            }

            row = [];
            value = "";

        } else {

            value += character;
        }
    }

    if (value.length > 0 || row.length > 0) {

        row.push(value.trim());

        if (row.some(item => item !== "")) {
            rows.push(row);
        }
    }

    return rows;
}

// ============================================================
// DASHBOARD BAR CHART
// ============================================================

function renderDashboardChart(ranking) {

    if (!dashboardBars) {
        return;
    }

    if (ranking.length === 0) {

        dashboardBars.innerHTML =
            "<p>No product data available.</p>";

        return;
    }

    const maximum =
        Math.max(...ranking.map(item => item[1]));

    const chartHTML = ranking
        .map(([product, value]) => {

            const percentage =
                maximum === 0
                    ? 0
                    : (value / maximum) * 100;

            return `
                <div class="bar-row">

                    <div
                        class="bar-label"
                        title="${escapeHTML(product)}"
                    >
                        ${escapeHTML(product)}
                    </div>

                    <div class="bar-wrapper">

                        <div
                            class="bar"
                            style="width: ${percentage}%"
                        ></div>

                    </div>

                    <div class="bar-value">
                        ${formatNumber(value)}
                    </div>

                </div>
            `;
        })
        .join("");

    dashboardBars.innerHTML = `
        <div class="bar-chart">
            ${chartHTML}
        </div>
    `;
}

// ============================================================
// SMART INSIGHTS
// ============================================================

function renderInsights(ranking, totalSalesValue) {

    const existing =
        document.getElementById("smartInsights");

    if (existing) {
        existing.remove();
    }

    if (!ranking || ranking.length === 0) {
        return;
    }

    const best = ranking[0];

    const worst =
        ranking[ranking.length - 1];

    const contribution =
        totalSalesValue > 0
            ? (best[1] / totalSalesValue) * 100
            : 0;

    const insightsSection =
        document.createElement("section");

    insightsSection.id = "smartInsights";

    insightsSection.className = "insights-box";

    insightsSection.innerHTML = `
        <h3>🧠 Smart Insights</h3>

        <div class="insight-grid">

            <div class="insight-item">

                <div class="insight-title">
                    🏆 Best-Selling Product
                </div>

                <div class="insight-value">
                    ${escapeHTML(best[0])}
                </div>

            </div>


            <div class="insight-item">

                <div class="insight-title">
                    📈 Best Product Sales
                </div>

                <div class="insight-value">
                    ${formatNumber(best[1])}
                </div>

            </div>


            <div class="insight-item">

                <div class="insight-title">
                    📊 Contribution to Total Sales
                </div>

                <div class="insight-value">
                    ${contribution.toFixed(1)}%
                </div>

            </div>


            <div class="insight-item">

                <div class="insight-title">
                    📉 Lowest-Performing Product
                </div>

                <div class="insight-value">
                    ${escapeHTML(worst[0])}
                </div>

            </div>

        </div>
    `;

    dashboard.appendChild(insightsSection);
}

// ============================================================
// DATASET PREVIEW
// ============================================================

function renderDatasetPreview(headers, data) {

    const existing =
        document.getElementById("datasetPreview");

    if (existing) {
        existing.remove();
    }

    const section =
        document.createElement("section");

    section.id = "datasetPreview";

    section.className = "dataset-box";

    const previewRows =
        data.slice(0, 10);

    let tableHTML = `
        <table class="dataset-table">

            <thead>
                <tr>
    `;

    headers.forEach(header => {

        tableHTML += `
            <th>
                ${escapeHTML(header)}
            </th>
        `;
    });

    tableHTML += `
                </tr>
            </thead>

            <tbody>
    `;

    previewRows.forEach(row => {

        tableHTML += "<tr>";

        headers.forEach((_, index) => {

            const value =
                row[index] ?? "";

            tableHTML += `
                <td>
                    ${escapeHTML(value)}
                </td>
            `;
        });

        tableHTML += "</tr>";
    });

    tableHTML += `
            </tbody>

        </table>
    `;

    section.innerHTML = `
        <h3>📋 Dataset Preview</h3>

        <div class="dataset-info">

            <div class="info-tag">
                Rows: ${data.length}
            </div>

            <div class="info-tag">
                Columns: ${headers.length}
            </div>

            <div class="info-tag">
                Showing first ${Math.min(10, data.length)} rows
            </div>

        </div>

        ${tableHTML}
    `;

    dashboard.appendChild(section);
}

// ============================================================
// ASK DATA
// ============================================================

askButton.addEventListener("click", async function () {

    const question =
        questionInput.value.trim();

    if (!selectedFile) {

        showError(
            "Please upload a CSV file first."
        );

        return;
    }

    if (!question) {

        showError(
            "Please enter a question."
        );

        return;
    }

    await askBackend(
        selectedFile,
        question
    );
});

// ============================================================
// ASK BACKEND
// ============================================================

async function askBackend(file, question) {

    resultContainer.style.display = "block";

    answerContainer.innerHTML = `
        <div class="loading-box">

            <div class="loader"></div>

            <p>
                DataMind AI is analyzing your question...
            </p>

        </div>
    `;

    chartContainer.style.display = "none";

    askButton.disabled = true;

    try {

        const formData = new FormData();

        formData.append("file", file);

        formData.append("question", question);

        const response =
            await fetch(
                `${API_URL}/ask`,
                {
                    method: "POST",
                    body: formData
                }
            );

        if (!response.ok) {

            throw new Error(
                `Backend returned HTTP ${response.status}`
            );
        }

        const result =
            await response.json();

        displayAnswer(result);

    } catch (error) {

        console.error(error);

        showError(
            "Could not connect to the DataMind AI backend. " +
            "Make sure FastAPI is running on port 8000."
        );

    } finally {

        askButton.disabled = false;
    }
}

// ============================================================
// DISPLAY ANSWER
// ============================================================

function displayAnswer(result) {

    if (!result.success) {

        answerContainer.innerHTML = `
            <div class="error-box">

                <strong>Unable to Analyze</strong>

                ${escapeHTML(
                    result.answer ||
                    result.error ||
                    "Unknown error."
                )}

            </div>
        `;

        return;
    }

    answerContainer.innerHTML = `
        <div class="answer-box">

            <div class="answer-label">
                DataMind AI
            </div>

            <div class="answer-text">
                ${escapeHTML(result.answer)}
            </div>

        </div>
    `;

    // --------------------------------------------------------
    // RANKING
    // --------------------------------------------------------

    if (result.ranking) {

        renderRanking(
            result.ranking
        );
    }

    // --------------------------------------------------------
    // CHART
    // --------------------------------------------------------

    if (
        result.chart &&
        result.chart.data
    ) {

        renderResultChart(
            result.chart
        );
    }
}

// ============================================================
// RANKING
// ============================================================

function renderRanking(ranking) {

    const entries =
        Object.entries(ranking);

    const rankingBox =
        document.createElement("div");

    rankingBox.className =
        "ranking-box";

    let html = `
        <h3>📊 Product Ranking</h3>

        <div class="ranking-list">
    `;

    entries.forEach(
        ([product, value], index) => {

            html += `
                <div class="ranking-item">

                    <div class="rank">
                        #${index + 1}
                    </div>

                    <div class="product-name">
                        ${escapeHTML(product)}
                    </div>

                    <div class="product-value">
                        ${formatNumber(value)}
                    </div>

                </div>
            `;
        }
    );

    html += `
        </div>
    `;

    rankingBox.innerHTML = html;

    answerContainer.appendChild(
        rankingBox
    );
}

// ============================================================
// RESULT CHART
// ============================================================

function renderResultChart(chart) {

    chartContainer.style.display =
        "block";

    const data =
        chart.data || [];

    if (data.length === 0) {

        chartContainer.innerHTML =
            "<p>No chart data available.</p>";

        return;
    }

    const maximum =
        Math.max(
            ...data.map(item => Number(item.value))
        );

    const rows =
        data.map(item => {

            const value =
                Number(item.value);

            const width =
                maximum === 0
                    ? 0
                    : (value / maximum) * 100;

            return `
                <div class="bar-row">

                    <div
                        class="bar-label"
                        title="${escapeHTML(item.category)}"
                    >
                        ${escapeHTML(item.category)}
                    </div>

                    <div class="bar-wrapper">

                        <div
                            class="bar"
                            style="width: ${width}%"
                        ></div>

                    </div>

                    <div class="bar-value">
                        ${formatNumber(value)}
                    </div>

                </div>
            `;
        }).join("");

    chartContainer.innerHTML = `
        <div class="chart-box">

            <h3>
                📊 ${escapeHTML(chart.title || "Chart")}
            </h3>

            <div class="bar-chart">
                ${rows}
            </div>

        </div>
    `;
}

// ============================================================
// ERROR
// ============================================================

function showError(message) {

    resultContainer.style.display =
        "block";

    chartContainer.style.display =
        "none";

    answerContainer.innerHTML = `
        <div class="error-box">

            <strong>Error</strong>

            ${escapeHTML(message)}

        </div>
    `;
}

// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ============================================================
// ENTER KEY
// ============================================================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askButton.click();
        }
    }
);