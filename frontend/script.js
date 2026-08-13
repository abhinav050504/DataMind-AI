// ============================================================
// AI DATA ANALYST - FRONTEND
// ============================================================

// Backend URL
const API_URL = "http://127.0.0.1:8000";

// Selected CSV file
let selectedFile = null;


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const fileName = document.getElementById("fileName");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

const resultContainer = document.getElementById("resultContainer");
const answerContainer = document.getElementById("answerContainer");

const chartContainer = document.getElementById("chartContainer");


// ============================================================
// FRONTEND LOADED
// ============================================================

console.log("AI Data Analyst frontend loaded.");


// ============================================================
// FILE SELECTION
// ============================================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (fileInput.files.length === 0) {

            selectedFile = null;

            if (fileName) {
                fileName.textContent = "No file selected";
            }

            return;
        }

        selectedFile = fileInput.files[0];

        // Check CSV
        if (!selectedFile.name.toLowerCase().endsWith(".csv")) {

            alert("Please select a CSV file.");

            selectedFile = null;

            fileInput.value = "";

            if (fileName) {
                fileName.textContent = "No file selected";
            }

            return;
        }

        if (fileName) {
            fileName.textContent = selectedFile.name;
        }

        console.log("Selected file:", selectedFile.name);
    });
}


// ============================================================
// UPLOAD BUTTON
// ============================================================

if (uploadButton) {

    uploadButton.addEventListener("click", function () {

        if (fileInput) {
            fileInput.click();
        }

    });
}


// ============================================================
// ASK BUTTON
// ============================================================

if (askButton) {

    askButton.addEventListener("click", askQuestion);

}


// ============================================================
// ENTER KEY
// ============================================================

if (questionInput) {

    questionInput.addEventListener("keydown", function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();
        }

    });

}


// ============================================================
// ASK QUESTION
// ============================================================

async function askQuestion() {

    // --------------------------------------------------------
    // CHECK FILE
    // --------------------------------------------------------

    if (!selectedFile) {

        showError("Please upload a CSV file first.");

        return;
    }


    // --------------------------------------------------------
    // GET QUESTION
    // --------------------------------------------------------

    const question = questionInput.value.trim();


    if (!question) {

        showError("Please enter a question.");

        return;
    }


    // --------------------------------------------------------
    // LOADING
    // --------------------------------------------------------

    showLoading();


    // --------------------------------------------------------
    // FORM DATA
    // --------------------------------------------------------

    const formData = new FormData();

    formData.append("file", selectedFile);

    formData.append("question", question);


    // --------------------------------------------------------
    // SEND REQUEST TO FASTAPI
    // --------------------------------------------------------

    try {

        console.log("Sending question:", question);

        console.log("Sending request to:", `${API_URL}/ask`);


        const response = await fetch(
            `${API_URL}/ask`,
            {
                method: "POST",
                body: formData
            }
        );


        // ----------------------------------------------------
        // CHECK SERVER RESPONSE
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        // ----------------------------------------------------
        // CONVERT RESPONSE TO JSON
        // ----------------------------------------------------

        const data = await response.json();


        console.log("Backend response:", data);


        // ----------------------------------------------------
        // DISPLAY RESULT
        // ----------------------------------------------------

        displayResult(data);


    } catch (error) {

        console.error("Backend error:", error);

        showError(
            "Could not connect to the backend. " +
            "Make sure FastAPI is running on port 8000."
        );

    }

}


// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(data) {

    if (resultContainer) {

        resultContainer.style.display = "block";

    }


    // --------------------------------------------------------
    // BACKEND ERROR
    // --------------------------------------------------------

    if (data.success === false) {

        const message =
            data.answer ||
            data.error ||
            "Something went wrong.";

        showError(message);

        return;
    }


    // --------------------------------------------------------
    // ANSWER
    // --------------------------------------------------------

    if (answerContainer) {

        answerContainer.innerHTML = `

            <div class="answer-box">

                <div class="answer-label">
                    AI Answer
                </div>

                <div class="answer-text">
                    ${escapeHTML(
                        data.answer || "No answer available."
                    )}
                </div>

            </div>

        `;
    }


    // --------------------------------------------------------
    // PRODUCT RANKING
    // --------------------------------------------------------

    if (
        data.ranking &&
        typeof data.ranking === "object"
    ) {

        displayRanking(data.ranking);

    }


    // --------------------------------------------------------
    // CHART
    // --------------------------------------------------------

    if (data.chart) {

        displayChart(data.chart);

    } else {

        clearChart();

    }

}


// ============================================================
// DISPLAY PRODUCT RANKING
// ============================================================

function displayRanking(ranking) {

    const entries = Object.entries(ranking);


    if (entries.length === 0) {
        return;
    }


    let rankingHTML = `

        <div class="ranking-box">

            <h3>Product Ranking</h3>

            <div class="ranking-list">

    `;


    entries.forEach(function ([product, value], index) {

        rankingHTML += `

            <div class="ranking-item">

                <span class="rank">
                    #${index + 1}
                </span>

                <span class="product-name">
                    ${escapeHTML(product)}
                </span>

                <span class="product-value">
                    ${Number(value).toFixed(2)}
                </span>

            </div>

        `;

    });


    rankingHTML += `

            </div>

        </div>

    `;


    if (answerContainer) {

        answerContainer.innerHTML += rankingHTML;

    }

}


// ============================================================
// DISPLAY BAR CHART
// ============================================================

function displayChart(chart) {

    if (!chartContainer) {

        console.warn(
            "chartContainer was not found in index.html."
        );

        return;
    }


    const data = chart.data || [];


    // --------------------------------------------------------
    // NO DATA
    // --------------------------------------------------------

    if (data.length === 0) {

        chartContainer.style.display = "block";

        chartContainer.innerHTML = `

            <div class="no-chart">
                No chart data available.
            </div>

        `;

        return;
    }


    // --------------------------------------------------------
    // FIND MAX VALUE
    // --------------------------------------------------------

    const values = data.map(
        item => Number(item.value)
    );


    const maxValue = Math.max(...values);


    // --------------------------------------------------------
    // CREATE CHART
    // --------------------------------------------------------

    let html = `

        <div class="chart-box">

            <h3>
                ${escapeHTML(
                    chart.title || "Data Chart"
                )}
            </h3>

            <div class="bar-chart">

    `;


    data.forEach(function (item) {

        const value = Number(item.value);

        let percentage = 0;


        if (maxValue > 0) {

            percentage =
                (value / maxValue) * 100;

        }


        html += `

            <div class="bar-row">

                <div class="bar-label">
                    ${escapeHTML(item.category)}
                </div>

                <div class="bar-wrapper">

                    <div
                        class="bar"
                        style="width: ${percentage}%"
                    ></div>

                </div>

                <div class="bar-value">
                    ${value.toFixed(2)}
                </div>

            </div>

        `;

    });


    html += `

            </div>

        </div>

    `;


    chartContainer.innerHTML = html;

    chartContainer.style.display = "block";

}


// ============================================================
// CLEAR CHART
// ============================================================

function clearChart() {

    if (!chartContainer) {
        return;
    }


    chartContainer.innerHTML = "";

    chartContainer.style.display = "none";

}


// ============================================================
// SHOW LOADING
// ============================================================

function showLoading() {

    if (resultContainer) {

        resultContainer.style.display = "block";

    }


    if (answerContainer) {

        answerContainer.innerHTML = `

            <div class="loading-box">

                <div class="loader"></div>

                <p>
                    Analyzing your data...
                </p>

            </div>

        `;

    }


    clearChart();

}


// ============================================================
// SHOW ERROR
// ============================================================

function showError(message) {

    if (resultContainer) {

        resultContainer.style.display = "block";

    }


    if (answerContainer) {

        answerContainer.innerHTML = `

            <div class="error-box">

                <strong>
                    Error
                </strong>

                <p>
                    ${escapeHTML(message)}
                </p>

            </div>

        `;

    }


    clearChart();

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");


    div.textContent =
        String(value);


    return div.innerHTML;

}