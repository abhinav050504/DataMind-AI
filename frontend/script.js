// ============================================================
// DATA MIND AI - FRONTEND
// ============================================================

const API_URL = "http://127.0.0.1:8000";

let selectedFile = null;


// ============================================================
// HTML ELEMENTS
// ============================================================

const fileInput =
    document.getElementById("fileInput");

const uploadButton =
    document.getElementById("uploadButton");

const fileName =
    document.getElementById("fileName");

const questionInput =
    document.getElementById("questionInput");

const askButton =
    document.getElementById("askButton");

const resultContainer =
    document.getElementById("resultContainer");

const answerContainer =
    document.getElementById("answerContainer");

const chartContainer =
    document.getElementById("chartContainer");

const dashboard =
    document.getElementById("dashboard");

const totalRecords =
    document.getElementById("totalRecords");

const totalColumns =
    document.getElementById("totalColumns");

const totalSales =
    document.getElementById("totalSales");

const averageSales =
    document.getElementById("averageSales");

const bestProduct =
    document.getElementById("bestProduct");

const lowestSales =
    document.getElementById("lowestSales");

const dashboardBars =
    document.getElementById("dashboardBars");


// ============================================================
// FRONTEND LOADED
// ============================================================

console.log("DataMind AI frontend loaded.");


// ============================================================
// FILE SELECTION
// ============================================================

if (fileInput) {

    fileInput.addEventListener(
        "change",
        function () {

            if (fileInput.files.length === 0) {

                selectedFile = null;

                fileName.textContent =
                    "No file selected";

                return;
            }


            selectedFile =
                fileInput.files[0];


            if (
                !selectedFile.name
                    .toLowerCase()
                    .endsWith(".csv")
            ) {

                alert(
                    "Please select a CSV file."
                );

                selectedFile = null;

                fileInput.value = "";

                fileName.textContent =
                    "No file selected";

                return;
            }


            fileName.textContent =
                selectedFile.name;


            console.log(
                "Selected file:",
                selectedFile.name
            );


            // Automatically analyze dataset
            loadDashboard();

        }
    );
}


// ============================================================
// UPLOAD BUTTON
// ============================================================

if (uploadButton) {

    uploadButton.addEventListener(
        "click",
        function () {

            fileInput.click();

        }
    );
}


// ============================================================
// ASK BUTTON
// ============================================================

if (askButton) {

    askButton.addEventListener(
        "click",
        askQuestion
    );
}


// ============================================================
// ENTER KEY
// ============================================================

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                askQuestion();
            }

        }
    );
}


// ============================================================
// LOAD AUTOMATIC DASHBOARD
// ============================================================

async function loadDashboard() {

    if (!selectedFile) {

        return;
    }


    dashboard.style.display =
        "block";


    totalRecords.textContent =
        "...";

    totalColumns.textContent =
        "...";

    totalSales.textContent =
        "...";

    averageSales.textContent =
        "...";

    bestProduct.textContent =
        "...";

    lowestSales.textContent =
        "...";

    dashboardBars.innerHTML =
        "<p>Analyzing dataset...</p>";


    try {

        const formData =
            new FormData();

        formData.append(
            "file",
            selectedFile
        );


        // ----------------------------------------------------
        // GET DATASET INFORMATION
        // ----------------------------------------------------

        const infoResponse =
            await fetch(
                `${API_URL}/dataset-info`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!infoResponse.ok) {

            throw new Error(
                `Server returned ${infoResponse.status}`
            );
        }


        const info =
            await infoResponse.json();


        console.log(
            "Dataset information:",
            info
        );


        if (!info.success) {

            throw new Error(
                info.error ||
                "Could not analyze dataset."
            );
        }


        totalRecords.textContent =
            info.rows;


        totalColumns.textContent =
            info.columns;


        // ----------------------------------------------------
        // GET BEST PRODUCT / SALES DATA
        // ----------------------------------------------------

        const questionData =
            new FormData();

        questionData.append(
            "file",
            selectedFile
        );

        questionData.append(
            "question",
            "Which product sells the most?"
        );


        const askResponse =
            await fetch(
                `${API_URL}/ask`,
                {
                    method: "POST",
                    body: questionData
                }
            );


        if (!askResponse.ok) {

            throw new Error(
                `Server returned ${askResponse.status}`
            );
        }


        const analysis =
            await askResponse.json();


        console.log(
            "Automatic analysis:",
            analysis
        );


        if (
            analysis.success &&
            analysis.ranking
        ) {

            const values =
                Object.values(
                    analysis.ranking
                );


            const salesTotal =
                values.reduce(
                    (sum, value) =>
                        sum + Number(value),
                    0
                );


            const average =
                values.length > 0
                    ? salesTotal / values.length
                    : 0;


            totalSales.textContent =
                formatNumber(salesTotal);


            averageSales.textContent =
                formatNumber(average);


            const rankingEntries =
                Object.entries(
                    analysis.ranking
                );


            if (
                rankingEntries.length > 0
            ) {

                bestProduct.textContent =
                    rankingEntries[0][0];


                const lowest =
                    rankingEntries[
                        rankingEntries.length - 1
                    ];


                lowestSales.textContent =
                    formatNumber(
                        lowest[1]
                    );
            }


            displayDashboardChart(
                analysis.ranking
            );

        } else {

            dashboardBars.innerHTML =
                `
                <p>
                    Sales information could not
                    be detected automatically.
                </p>
                `;
        }


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        dashboardBars.innerHTML =
            `
            <p class="error-text">
                Could not load dashboard.
                Make sure the FastAPI backend
                is running.
            </p>
            `;
    }
}


// ============================================================
// DISPLAY DASHBOARD CHART
// ============================================================

function displayDashboardChart(
    ranking
) {

    const entries =
        Object.entries(ranking);


    if (entries.length === 0) {

        dashboardBars.innerHTML =
            "<p>No sales data available.</p>";

        return;
    }


    const values =
        entries.map(
            ([, value]) =>
                Number(value)
        );


    const maxValue =
        Math.max(...values);


    let html =
        `<div class="bar-chart">`;


    entries.forEach(
        function ([product, value]) {

            const numericValue =
                Number(value);


            let percentage =
                0;


            if (maxValue > 0) {

                percentage =
                    (
                        numericValue /
                        maxValue
                    ) * 100;
            }


            html +=
                `
                <div class="bar-row">

                    <div class="bar-label">
                        ${escapeHTML(product)}
                    </div>

                    <div class="bar-wrapper">

                        <div
                            class="bar"
                            style="width: ${percentage}%"
                        ></div>

                    </div>

                    <div class="bar-value">
                        ${formatNumber(numericValue)}
                    </div>

                </div>
                `;
        }
    );


    html +=
        `</div>`;


    dashboardBars.innerHTML =
        html;
}


// ============================================================
// ASK QUESTION
// ============================================================

async function askQuestion() {

    if (!selectedFile) {

        showError(
            "Please upload a CSV file first."
        );

        return;
    }


    const question =
        questionInput.value.trim();


    if (!question) {

        showError(
            "Please enter a question."
        );

        return;
    }


    showLoading();


    const formData =
        new FormData();


    formData.append(
        "file",
        selectedFile
    );


    formData.append(
        "question",
        question
    );


    try {

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
                `Server returned ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Backend response:",
            data
        );


        displayResult(data);


    } catch (error) {

        console.error(
            "Question error:",
            error
        );


        showError(
            "Could not connect to the backend. " +
            "Make sure FastAPI is running."
        );
    }
}


// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(data) {

    resultContainer.style.display =
        "block";


    if (data.success === false) {

        const message =
            data.answer ||
            data.error ||
            "Something went wrong.";


        showError(message);

        return;
    }


    answerContainer.innerHTML =
        `
        <div class="answer-box">

            <div class="answer-label">
                AI Answer
            </div>

            <div class="answer-text">
                ${escapeHTML(
                    data.answer ||
                    "No answer available."
                )}
            </div>

        </div>
        `;


    if (
        data.ranking &&
        typeof data.ranking === "object"
    ) {

        displayRanking(
            data.ranking
        );
    }


    if (data.chart) {

        displayChart(
            data.chart
        );

    } else {

        clearChart();
    }
}


// ============================================================
// DISPLAY RANKING
// ============================================================

function displayRanking(
    ranking
) {

    let rankingHTML =
        `
        <div class="ranking-box">

            <h3>
                🏆 Product Ranking
            </h3>

            <div class="ranking-list">
        `;


    const entries =
        Object.entries(ranking);


    entries.forEach(
        function (
            [product, value],
            index
        ) {

            rankingHTML +=
                `
                <div class="ranking-item">

                    <span class="rank">
                        #${index + 1}
                    </span>

                    <span class="product-name">
                        ${escapeHTML(product)}
                    </span>

                    <span class="product-value">
                        ${formatNumber(value)}
                    </span>

                </div>
                `;
        }
    );


    rankingHTML +=
        `
            </div>

        </div>
        `;


    answerContainer.innerHTML +=
        rankingHTML;
}


// ============================================================
// DISPLAY QUESTION CHART
// ============================================================

function displayChart(chart) {

    chartContainer.style.display =
        "block";


    const data =
        chart.data || [];


    if (data.length === 0) {

        chartContainer.innerHTML =
            `
            <div class="chart-box">
                No chart data available.
            </div>
            `;

        return;
    }


    const values =
        data.map(
            item =>
                Number(item.value)
        );


    const maxValue =
        Math.max(...values);


    let html =
        `
        <div class="chart-box">

            <h3>
                📊 ${escapeHTML(
                    chart.title ||
                    "Data Chart"
                )}
            </h3>

            <div class="bar-chart">
        `;


    data.forEach(
        function (item) {

            const value =
                Number(item.value);


            let percentage =
                0;


            if (maxValue > 0) {

                percentage =
                    (value / maxValue) *
                    100;
            }


            html +=
                `
                <div class="bar-row">

                    <div class="bar-label">
                        ${escapeHTML(
                            item.category
                        )}
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
        }
    );


    html +=
        `
            </div>

        </div>
        `;


    chartContainer.innerHTML =
        html;
}


// ============================================================
// CLEAR CHART
// ============================================================

function clearChart() {

    chartContainer.innerHTML =
        "";

    chartContainer.style.display =
        "none";
}


// ============================================================
// LOADING
// ============================================================

function showLoading() {

    resultContainer.style.display =
        "block";


    answerContainer.innerHTML =
        `
        <div class="loading-box">

            <div class="loader"></div>

            <p>
                Analyzing your data...
            </p>

        </div>
        `;


    clearChart();
}


// ============================================================
// ERROR
// ============================================================

function showError(
    message
) {

    resultContainer.style.display =
        "block";


    answerContainer.innerHTML =
        `
        <div class="error-box">

            <strong>
                Error
            </strong>

            <p>
                ${escapeHTML(message)}
            </p>

        </div>
        `;


    clearChart();
}


// ============================================================
// FORMAT NUMBER
// ============================================================

function formatNumber(
    value
) {

    const number =
        Number(value);


    if (Number.isNaN(number)) {

        return "0";
    }


    return number.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(
    value
) {

    const div =
        document.createElement("div");


    div.textContent =
        String(value);


    return div.innerHTML;
}