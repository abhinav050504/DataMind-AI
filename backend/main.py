# ============================================================
# DATA MIND AI - BACKEND
# AI-Powered Data Analysis & Insight Platform
# ============================================================

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io
import re


# ============================================================
# CREATE APP
# ============================================================

app = FastAPI(
    title="DataMind AI",
    description="AI-Powered Data Analysis & Insight Platform",
    version="1.0.0"
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
        "message": "DataMind AI backend is running!",
        "version": "1.0.0"
    }


# ============================================================
# READ CSV
# ============================================================

async def read_csv(file: UploadFile):

    contents = await file.read()

    df = pd.read_csv(
        io.BytesIO(contents)
    )

    return df


# ============================================================
# FIND SALES COLUMN
# ============================================================

def find_sales_column(df):

    possible_columns = [
        "Sales",
        "sales",
        "Sale",
        "sale",
        "Revenue",
        "revenue",
        "Amount",
        "amount",
        "Value",
        "value",
        "Total Sales",
        "total_sales"
    ]

    for column in possible_columns:

        if column in df.columns:

            if pd.api.types.is_numeric_dtype(df[column]):
                return column

    # Backup: find first numeric column
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:
        return numeric_columns[0]

    return None


# ============================================================
# FIND PRODUCT COLUMN
# ============================================================

def find_product_column(df):

    possible_columns = [
        "Product",
        "product",
        "Product Name",
        "product_name",
        "ProductName",
        "Item",
        "item",
        "Category",
        "category"
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    # Backup: find a text column
    text_columns = df.select_dtypes(
        include="object"
    ).columns

    if len(text_columns) > 0:
        return text_columns[0]

    return None


# ============================================================
# CREATE PRODUCT CHART
# ============================================================

def create_product_chart(
    df,
    product_column,
    sales_column
):

    grouped = (
        df.groupby(product_column)[sales_column]
        .sum()
        .sort_values(ascending=False)
    )

    chart_data = []

    for product, value in grouped.items():

        chart_data.append({
            "category": str(product),
            "value": round(float(value), 2)
        })

    return chart_data


# ============================================================
# ASK DATA
# ============================================================

@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):

    question_original = question.strip()

    if not file.filename.lower().endswith(".csv"):

        return {
            "success": False,
            "question": question_original,
            "answer": "Please upload a CSV file."
        }

    try:

        # ----------------------------------------------------
        # READ CSV
        # ----------------------------------------------------

        df = await read_csv(file)

        # ----------------------------------------------------
        # NORMALIZE QUESTION
        # ----------------------------------------------------

        q = question_original.lower()

        q = re.sub(
            r"[?!.,]",
            "",
            q
        )

        q = re.sub(
            r"\s+",
            " ",
            q
        ).strip()

        # ----------------------------------------------------
        # FIND COLUMNS
        # ----------------------------------------------------

        sales_column = find_sales_column(df)

        product_column = find_product_column(df)

        # ====================================================
        # 1. BEST SELLING PRODUCT
        # ====================================================

        best_selling_keywords = [
            "sells most",
            "sell most",
            "best selling",
            "best-selling",
            "best seller",
            "best product",
            "top product",
            "highest selling",
            "most popular",
            "which product sells the most",
            "which product is best",
            "what product sells the most"
        ]

        if any(
            keyword in q
            for keyword in best_selling_keywords
        ):

            if not product_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a product "
                        "column in your dataset."
                    )
                }

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            ranking = (
                df.groupby(product_column)[sales_column]
                .sum()
                .sort_values(ascending=False)
            )

            if ranking.empty:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": "No product data found."
                }

            best_product = ranking.index[0]

            best_value = ranking.iloc[0]

            ranking_data = {
                str(product): round(float(value), 2)
                for product, value in ranking.items()
            }

            chart_data = create_product_chart(
                df,
                product_column,
                sales_column
            )

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"{best_product} is the "
                    f"best-selling product with "
                    f"{best_value:.2f} "
                    f"{sales_column}."
                ),

                "product_column": product_column,

                "sales_column": sales_column,

                "ranking": ranking_data,

                "chart": {
                    "chart_type": "bar",
                    "title": (
                        f"{sales_column} by "
                        f"{product_column}"
                    ),
                    "x_axis": product_column,
                    "y_axis": sales_column,
                    "data": chart_data
                }
            }

        # ====================================================
        # 2. TOTAL SALES
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "total sales",
                "total sale",
                "sum of sales",
                "sales total",
                "how much sales",
                "total revenue",
                "total amount"
            ]
        ):

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            total = df[sales_column].sum()

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The total "
                    f"{sales_column.lower()} is "
                    f"{total:.2f}."
                ),

                "sales_column": sales_column,

                "total": round(float(total), 2)
            }

        # ====================================================
        # 3. AVERAGE SALES
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "average sales",
                "average sale",
                "mean sales",
                "average revenue",
                "average amount"
            ]
        ):

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            average = df[sales_column].mean()

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The average "
                    f"{sales_column.lower()} is "
                    f"{average:.2f}."
                ),

                "sales_column": sales_column,

                "average": round(float(average), 2)
            }

        # ====================================================
        # 4. MAXIMUM SALES
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "maximum sales",
                "max sales",
                "highest sales",
                "highest sale",
                "maximum sale",
                "largest sale",
                "largest sales"
            ]
        ):

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            maximum = df[sales_column].max()

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The highest "
                    f"{sales_column.lower()} is "
                    f"{maximum:.2f}."
                ),

                "sales_column": sales_column,

                "maximum": round(float(maximum), 2)
            }

        # ====================================================
        # 5. MINIMUM SALES
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "minimum sales",
                "min sales",
                "lowest sales",
                "lowest sale",
                "minimum sale",
                "smallest sale",
                "smallest sales"
            ]
        ):

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            minimum = df[sales_column].min()

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The lowest "
                    f"{sales_column.lower()} is "
                    f"{minimum:.2f}."
                ),

                "sales_column": sales_column,

                "minimum": round(float(minimum), 2)
            }

        # ====================================================
        # 6. NUMBER OF RECORDS
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "number of records",
                "number of rows",
                "how many records",
                "how many rows",
                "count records",
                "record count",
                "row count"
            ]
        ):

            count = len(df)

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"Your dataset contains "
                    f"{count} records."
                ),

                "records": count
            }

        # ====================================================
        # 7. TOP 3 PRODUCTS
        # ====================================================

        if any(
            keyword in q
            for keyword in [
                "top 3 products",
                "top three products",
                "best 3 products",
                "best three products",
                "top three product",
                "top 3 product"
            ]
        ):

            if not product_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a product "
                        "column."
                    )
                }

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            ranking = (
                df.groupby(product_column)[sales_column]
                .sum()
                .sort_values(ascending=False)
                .head(3)
            )

            top_products = {
                str(product): round(float(value), 2)
                for product, value in ranking.items()
            }

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    "Here are the top 3 "
                    "best-selling products."
                ),

                "ranking": top_products,

                "chart": {
                    "chart_type": "bar",
                    "title": "Top 3 Products",
                    "x_axis": product_column,
                    "y_axis": sales_column,
                    "data": [
                        {
                            "category": str(product),
                            "value": round(float(value), 2)
                        }
                        for product, value
                        in ranking.items()
                    ]
                }
            }

        # ====================================================
        # 8. SALES BY PRODUCT
        # ====================================================

        if (
            "sales by product" in q
            or "show sales by product" in q
            or "sales per product" in q
            or "product sales" in q
            or "sales for each product" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a product "
                        "column."
                    )
                }

            if not sales_column:

                return {
                    "success": False,
                    "question": question_original,
                    "answer": (
                        "I could not find a numeric "
                        "sales column."
                    )
                }

            chart_data = create_product_chart(
                df,
                product_column,
                sales_column
            )

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"Here is the "
                    f"{sales_column.lower()} "
                    f"breakdown by "
                    f"{product_column.lower()}."
                ),

                "chart": {
                    "chart_type": "bar",
                    "title": (
                        f"{sales_column} by "
                        f"{product_column}"
                    ),
                    "x_axis": product_column,
                    "y_axis": sales_column,
                    "data": chart_data
                }
            }

        # ====================================================
        # 9. DATASET SUMMARY
        # ====================================================

        if (
            "dataset summary" in q
            or "data summary" in q
            or "summarize the data" in q
            or "summary of data" in q
            or q == "summary"
            or "give me a summary" in q
        ):

            numeric_columns = [
                str(column)
                for column
                in df.select_dtypes(
                    include="number"
                ).columns
            ]

            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"Your dataset has "
                    f"{len(df)} rows and "
                    f"{len(df.columns)} columns."
                ),

                "rows": len(df),

                "columns": len(df.columns),

                "column_names": [
                    str(column)
                    for column in df.columns
                ],

                "numeric_columns": numeric_columns
            }

        # ====================================================
        # UNKNOWN QUESTION
        # ====================================================

        return {

            "success": False,

            "question": question_original,

            "answer": (
                "I don't understand this question yet. "
                "Try asking a question such as "
                "'Which product sells the most?', "
                "'What is the total sales?', "
                "'What is the average sales?', "
                "'What are the maximum sales?', "
                "'What are the minimum sales?', "
                "'How many records are there?', "
                "'Show me the top 3 products', "
                "'Show me sales by product', "
                "or 'Give me a dataset summary'."
            )
        }

    except Exception as e:

        return {

            "success": False,

            "question": question_original,

            "answer": (
                "An error occurred while "
                "analyzing your dataset."
            ),

            "error": str(e)
        }


# ============================================================
# GENERATE CHART DATA
# ============================================================

@app.post("/chart")
async def generate_chart(
    file: UploadFile = File(...),
    column: str = Form(...),
    value_column: str = Form(...)
):

    if not file.filename.lower().endswith(".csv"):

        return {
            "success": False,
            "error": "Please upload a CSV file."
        }

    try:

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )

        if column not in df.columns:

            return {
                "success": False,
                "error": (
                    f"Column '{column}' "
                    f"was not found."
                )
            }

        if value_column not in df.columns:

            return {
                "success": False,
                "error": (
                    f"Column '{value_column}' "
                    f"was not found."
                )
            }

        if not pd.api.types.is_numeric_dtype(
            df[value_column]
        ):

            return {
                "success": False,
                "error": (
                    f"'{value_column}' must be "
                    f"a numeric column."
                )
            }

        grouped = (
            df.groupby(column)[value_column]
            .sum()
            .sort_values(ascending=False)
        )

        chart_data = [
            {
                "category": str(category),
                "value": round(float(value), 2)
            }
            for category, value
            in grouped.items()
        ]

        return {

            "success": True,

            "chart_type": "bar",

            "title": (
                f"{value_column} by {column}"
            ),

            "x_axis": column,

            "y_axis": value_column,

            "data": chart_data
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# DATASET INFORMATION
# ============================================================

@app.post("/dataset-info")
async def dataset_info(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".csv"):

        return {

            "success": False,

            "error": "Please upload a CSV file."
        }

    try:

        df = await read_csv(file)

        return {

            "success": True,

            "rows": len(df),

            "columns": len(df.columns),

            "column_names": [
                str(column)
                for column in df.columns
            ],

            "data_types": {
                str(column): str(df[column].dtype)
                for column in df.columns
            },

            "missing_values": {
                str(column):
                    int(df[column].isna().sum())
                for column in df.columns
            }
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# END
# ============================================================