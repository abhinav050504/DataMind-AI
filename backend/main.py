from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io
import re


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Data Analyst",
    description="AI-powered CSV Data Analysis Backend",
    version="2.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "AI Data Analyst Backend is running!"
    }


# ============================================================
# READ CSV
# ============================================================

async def read_csv_file(file: UploadFile):

    contents = await file.read()

    df = pd.read_csv(
        io.BytesIO(contents)
    )

    return df


# ============================================================
# FIND PRODUCT COLUMN
# ============================================================

def find_product_column(df):

    possible_names = [
        "product",
        "products",
        "item",
        "items",
        "product_name",
        "product name",
        "productname",
        "name"
    ]

    # First: exact matches
    for column in df.columns:

        column_lower = (
            str(column)
            .strip()
            .lower()
        )

        if column_lower in possible_names:

            return column

    # Second: partial matches
    for column in df.columns:

        column_lower = (
            str(column)
            .strip()
            .lower()
        )

        if (
            "product" in column_lower
            or "item" in column_lower
        ):

            return column

    return None


# ============================================================
# FIND SALES COLUMN
# ============================================================

def find_sales_column(df):

    possible_names = [
        "sales",
        "sale",
        "revenue",
        "amount",
        "total_sales",
        "total sales",
        "quantity",
        "units",
        "units_sold",
        "units sold"
    ]

    # First: exact matches
    for column in df.columns:

        column_lower = (
            str(column)
            .strip()
            .lower()
        )

        if column_lower in possible_names:

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                return column

    # Second: partial matches
    for column in df.columns:

        column_lower = (
            str(column)
            .strip()
            .lower()
        )

        if (
            "sales" in column_lower
            or "revenue" in column_lower
            or "amount" in column_lower
            or "quantity" in column_lower
        ):

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                return column

    # Third: find a numeric column
    # if there is only one numeric column

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) == 1:

        return numeric_columns[0]

    return None


# ============================================================
# CREATE BAR CHART DATA
# ============================================================

def create_bar_chart(
    df,
    category_column,
    value_column
):

    # Make a copy
    data = df.copy()

    # Remove rows with missing category/value
    data = data.dropna(
        subset=[
            category_column,
            value_column
        ]
    )

    # Group data
    grouped = (
        data.groupby(
            category_column
        )[value_column]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    chart_data = []

    for category, value in grouped.items():

        chart_data.append({

            "category": str(category),

            "value": round(
                float(value),
                2
            )

        })

    return {

        "chart_type": "bar",

        "title": (
            f"{value_column} by "
            f"{category_column}"
        ),

        "x_axis": str(category_column),

        "y_axis": str(value_column),

        "data": chart_data

    }


# ============================================================
# ANALYZE DATASET
# ============================================================

@app.post("/analyze")
async def analyze_dataset(
    file: UploadFile = File(...)
):

    if not file.filename:

        return {
            "success": False,
            "error": "No file selected."
        }

    if not file.filename.lower().endswith(".csv"):

        return {
            "success": False,
            "error": "Please upload a CSV file."
        }

    try:

        df = await read_csv_file(file)

        rows = len(df)

        columns = len(df.columns)

        column_names = [
            str(column)
            for column in df.columns
        ]

        total_missing_values = int(
            df.isnull().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        numeric_columns = [
            str(column)
            for column in df.select_dtypes(
                include="number"
            ).columns
        ]

        text_columns = [
            str(column)
            for column in df.select_dtypes(
                exclude="number"
            ).columns
        ]

        product_column = find_product_column(df)

        sales_column = find_sales_column(df)

        insights = []

        insights.append(
            f"Dataset contains {rows} rows "
            f"and {columns} columns."
        )

        if total_missing_values == 0:

            insights.append(
                "There are no missing values "
                "in the dataset."
            )

        else:

            insights.append(
                f"Dataset contains "
                f"{total_missing_values} "
                f"missing values."
            )

        if duplicate_rows == 0:

            insights.append(
                "There are no duplicate rows."
            )

        else:

            insights.append(
                f"Dataset contains "
                f"{duplicate_rows} "
                f"duplicate rows."
            )

        if numeric_columns:

            insights.append(
                "Numeric columns: "
                + ", ".join(
                    numeric_columns
                )
            )

        if text_columns:

            insights.append(
                "Text/category columns: "
                + ", ".join(
                    text_columns
                )
            )

        return {

            "success": True,

            "dataset": {

                "rows": rows,

                "columns": columns,

                "column_names": column_names,

                "numeric_columns": numeric_columns,

                "text_columns": text_columns

            },

            "data_quality": {

                "total_missing_values":
                    total_missing_values,

                "duplicate_rows":
                    duplicate_rows

            },

            "detected_columns": {

                "product_column":
                    str(product_column)
                    if product_column
                    else None,

                "sales_column":
                    str(sales_column)
                    if sales_column
                    else None

            },

            "insights": insights

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):

    if not file.filename:

        return {

            "success": False,

            "answer": "No CSV file selected."

        }

    if not file.filename.lower().endswith(".csv"):

        return {

            "success": False,

            "answer": "Please upload a CSV file."

        }

    try:

        # ----------------------------------------------------
        # READ CSV
        # ----------------------------------------------------

        df = await read_csv_file(file)

        # ----------------------------------------------------
        # CLEAN QUESTION
        # ----------------------------------------------------

        q = (
            question
            .lower()
            .strip()
        )

        # Remove punctuation
        q_clean = re.sub(
            r"[^\w\s]",
            " ",
            q
        )

        # Remove extra spaces
        q_clean = re.sub(
            r"\s+",
            " ",
            q_clean
        ).strip()

        # ----------------------------------------------------
        # FIND COLUMNS
        # ----------------------------------------------------

        product_column = find_product_column(df)

        sales_column = find_sales_column(df)


        # ====================================================
        # BEST SELLING PRODUCT
        # ====================================================

        best_selling_keywords = [

            "sells most",
            "sell most",
            "sold most",
            "sells the most",
            "sell the most",
            "best selling",
            "best-selling",
            "best seller",
            "top product",
            "top selling",
            "top-selling",
            "highest selling",
            "highest-selling",
            "most popular",
            "most sold",
            "maximum sales",
            "highest sales",
            "product sells",
            "product sell"

        ]

        is_best_selling_question = any(
            keyword in q_clean
            for keyword in best_selling_keywords
        )

        # Also detect questions such as:
        # "Which product has highest sales?"
        if (
            "which product" in q_clean
            and (
                "highest" in q_clean
                or "maximum" in q_clean
                or "most" in q_clean
                or "best" in q_clean
            )
        ):

            is_best_selling_question = True


        if is_best_selling_question:

            if product_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a Product column."

                }

            if sales_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a numeric Sales column."

                }

            # Remove missing values
            data = df.dropna(
                subset=[
                    product_column,
                    sales_column
                ]
            )

            # Group sales by product
            ranking = (
                data.groupby(
                    product_column
                )[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            if ranking.empty:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "There is no valid product sales data."

                }

            # Best product
            best_product = ranking.index[0]

            best_value = float(
                ranking.iloc[0]
            )

            # Ranking
            ranking_data = {}

            for product, value in ranking.items():

                ranking_data[
                    str(product)
                ] = round(
                    float(value),
                    2
                )

            # Chart
            chart = create_bar_chart(
                data,
                product_column,
                sales_column
            )

            return {

                "success": True,

                "question": question,

                "answer": (
                    f"{best_product} is the "
                    f"best-selling product with "
                    f"{best_value:.2f} "
                    f"{sales_column}."
                ),

                "product_column":
                    str(product_column),

                "sales_column":
                    str(sales_column),

                "ranking":
                    ranking_data,

                "chart":
                    chart

            }


        # ====================================================
        # TOTAL SALES
        # ====================================================

        total_keywords = [

            "total sales",
            "total sale",
            "sum of sales",
            "overall sales",
            "sales total",
            "how much sales",
            "how many sales",
            "total revenue",
            "overall revenue"

        ]

        is_total_question = any(
            keyword in q_clean
            for keyword in total_keywords
        )

        if is_total_question:

            if sales_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a numeric Sales column."

                }

            total_sales = float(
                df[sales_column].sum()
            )

            return {

                "success": True,

                "question": question,

                "answer": (
                    f"The total {sales_column} "
                    f"is {total_sales:.2f}."
                ),

                "sales_column":
                    str(sales_column),

                "total":
                    round(
                        total_sales,
                        2
                    )

            }


        # ====================================================
        # AVERAGE SALES
        # ====================================================

        average_keywords = [

            "average sales",
            "average sale",
            "mean sales",
            "average revenue",
            "mean revenue",
            "average amount"

        ]

        is_average_question = any(
            keyword in q_clean
            for keyword in average_keywords
        )

        if is_average_question:

            if sales_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a numeric Sales column."

                }

            average_sales = float(
                df[sales_column].mean()
            )

            return {

                "success": True,

                "question": question,

                "answer": (
                    f"The average {sales_column} "
                    f"is {average_sales:.2f}."
                ),

                "sales_column":
                    str(sales_column),

                "average":
                    round(
                        average_sales,
                        2
                    )

            }


        # ====================================================
        # SALES BY PRODUCT
        # ====================================================

        sales_by_product_keywords = [

            "sales by product",
            "product sales",
            "show sales",
            "sales for each product",
            "sales of each product",
            "breakdown by product",
            "product breakdown",
            "products and sales",
            "sales per product"

        ]

        is_sales_by_product_question = any(
            keyword in q_clean
            for keyword in sales_by_product_keywords
        )

        if is_sales_by_product_question:

            if product_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a Product column."

                }

            if sales_column is None:

                return {

                    "success": False,

                    "question": question,

                    "answer":
                        "I could not find a numeric Sales column."

                }

            chart = create_bar_chart(
                df,
                product_column,
                sales_column
            )

            return {

                "success": True,

                "question": question,

                "answer": (
                    f"Here is the {sales_column} "
                    f"breakdown by {product_column}."
                ),

                "product_column":
                    str(product_column),

                "sales_column":
                    str(sales_column),

                "chart":
                    chart

            }


        # ====================================================
        # SHOW DATASET INFORMATION
        # ====================================================

        dataset_keywords = [

            "dataset",
            "data information",
            "data info",
            "columns",
            "how many rows",
            "how many columns",
            "rows and columns"

        ]

        is_dataset_question = any(
            keyword in q_clean
            for keyword in dataset_keywords
        )

        if is_dataset_question:

            return {

                "success": True,

                "question": question,

                "answer": (
                    f"Your dataset has "
                    f"{len(df)} rows and "
                    f"{len(df.columns)} columns."
                ),

                "columns": [
                    str(column)
                    for column in df.columns
                ],

                "rows":
                    len(df),

                "column_count":
                    len(df.columns)

            }


        # ====================================================
        # UNKNOWN QUESTION
        # ====================================================

        return {

            "success": False,

            "question": question,

            "answer": (
                "I don't understand this question yet. "
                "Try asking questions like: "
                "'Which product sells the most?', "
                "'What is the total sales?', "
                "'What is the average sales?', "
                "'Show me sales by product', "
                "or 'Which product has the highest sales?'"
            )

        }

    except Exception as e:

        return {

            "success": False,

            "question": question,

            "error": str(e),

            "answer":
                "Something went wrong while "
                "analyzing the data."

        }


# ============================================================
# DIRECT CHART ENDPOINT
# ============================================================

@app.post("/chart")
async def generate_chart(

    file: UploadFile = File(...),

    column: str = Form(...),

    value_column: str = Form(...)

):

    if not file.filename:

        return {

            "success": False,

            "error": "No CSV file selected."

        }

    if not file.filename.lower().endswith(".csv"):

        return {

            "success": False,

            "error": "Please upload a CSV file."

        }

    try:

        df = await read_csv_file(file)

        if column not in df.columns:

            return {

                "success": False,

                "error":
                    f"Column '{column}' "
                    f"was not found."

            }

        if value_column not in df.columns:

            return {

                "success": False,

                "error":
                    f"Column '{value_column}' "
                    f"was not found."

            }

        if not pd.api.types.is_numeric_dtype(
            df[value_column]
        ):

            return {

                "success": False,

                "error": (
                    f"'{value_column}' "
                    f"must be a numeric column."
                )

            }

        chart = create_bar_chart(
            df,
            column,
            value_column
        )

        return {

            "success": True,

            **chart

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }