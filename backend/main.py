# ============================================================
# DATA MIND AI - BACKEND
# AI-Powered Data Analysis & Insight Platform
# ============================================================

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io


# ============================================================
# CREATE FASTAPI APP
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
        "Price",
        "price",
        "Value",
        "value"
    ]

    for column in possible_columns:

        if column in df.columns:

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                return column

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
        "Item",
        "item",
        "Category",
        "category"
    ]

    for column in possible_columns:

        if column in df.columns:

            return column

    return None


# ============================================================
# FIND NUMERIC COLUMN
# ============================================================

def find_numeric_column(df):

    numeric_columns = list(
        df.select_dtypes(
            include="number"
        ).columns
    )

    if numeric_columns:

        return numeric_columns[0]

    return None


# ============================================================
# CREATE BAR CHART DATA
# ============================================================

def create_chart_data(
    df,
    category_column,
    value_column
):

    grouped = (
        df.groupby(category_column)[value_column]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    chart_data = []

    for category, value in grouped.items():

        chart_data.append(
            {
                "category": str(category),

                "value": round(
                    float(value),
                    2
                )
            }
        )

    return chart_data


# ============================================================
# ASK DATA
# ============================================================

@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file.filename:

        return {
            "success": False,
            "answer": "Please upload a CSV file."
        }


    if not file.filename.lower().endswith(".csv"):

        return {
            "success": False,
            "answer": "Please upload a CSV file."
        }


    try:

        # ----------------------------------------------------
        # READ DATA
        # ----------------------------------------------------

        df = await read_csv(file)


        if df.empty:

            return {
                "success": False,
                "answer": "The uploaded CSV file is empty."
            }


        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        question_original = question.strip()

        q = question_original.lower()


        # ----------------------------------------------------
        # FIND IMPORTANT COLUMNS
        # ----------------------------------------------------

        sales_column = find_sales_column(df)

        product_column = find_product_column(df)


        # ====================================================
        # QUESTION 1
        # WHICH PRODUCT SELLS THE MOST?
        # ====================================================

        if (
            "sells most" in q
            or "sell most" in q
            or "best selling" in q
            or "best-selling" in q
            or "top product" in q
            or "highest selling" in q
            or "most popular" in q
            or "best product" in q
            or "which product sells" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a product column "
                        "in your dataset."
                    )
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column in your dataset."
                    )
                }


            ranking = (
                df.groupby(product_column)[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            if ranking.empty:

                return {
                    "success": False,
                    "answer": "No product sales data was found."
                }


            best_product = ranking.index[0]

            best_value = ranking.iloc[0]


            ranking_data = {}

            for product, value in ranking.items():

                ranking_data[str(product)] = round(
                    float(value),
                    2
                )


            chart_data = create_chart_data(
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
        # QUESTION 2
        # TOTAL SALES
        # ====================================================

        if (
            "total sales" in q
            or "total sale" in q
            or "sum of sales" in q
            or "sales total" in q
            or "how much sales" in q
            or "total revenue" in q
            or "total amount" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column in your dataset."
                    )
                }


            total = df[sales_column].sum()


            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The total "
                    f"{sales_column.lower()} "
                    f"is {total:.2f}."
                ),

                "sales_column": sales_column,

                "total": round(
                    float(total),
                    2
                )
            }


        # ====================================================
        # QUESTION 3
        # AVERAGE SALES
        # ====================================================

        if (
            "average sales" in q
            or "average sale" in q
            or "mean sales" in q
            or "average" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column in your dataset."
                    )
                }


            average = df[sales_column].mean()


            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The average "
                    f"{sales_column.lower()} "
                    f"is {average:.2f}."
                ),

                "sales_column": sales_column,

                "average": round(
                    float(average),
                    2
                )
            }


        # ====================================================
        # QUESTION 4
        # MAXIMUM SALES
        # ====================================================

        if (
            "maximum sales" in q
            or "max sales" in q
            or "highest sales" in q
            or "highest sale" in q
            or "maximum sale" in q
            or "max sale" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column in your dataset."
                    )
                }


            maximum = df[sales_column].max()


            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The highest "
                    f"{sales_column.lower()} "
                    f"is {maximum:.2f}."
                ),

                "sales_column": sales_column,

                "maximum": round(
                    float(maximum),
                    2
                )
            }


        # ====================================================
        # QUESTION 5
        # MINIMUM SALES
        # ====================================================

        if (
            "minimum sales" in q
            or "min sales" in q
            or "lowest sales" in q
            or "lowest sale" in q
            or "minimum sale" in q
            or "min sale" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column in your dataset."
                    )
                }


            minimum = df[sales_column].min()


            return {

                "success": True,

                "question": question_original,

                "answer": (
                    f"The lowest "
                    f"{sales_column.lower()} "
                    f"is {minimum:.2f}."
                ),

                "sales_column": sales_column,

                "minimum": round(
                    float(minimum),
                    2
                )
            }


        # ====================================================
        # QUESTION 6
        # NUMBER OF RECORDS
        # ====================================================

        if (
            "number of records" in q
            or "number of rows" in q
            or "how many records" in q
            or "how many rows" in q
            or "count records" in q
            or "record count" in q
            or "how many entries" in q
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
        # QUESTION 7
        # TOP 3 PRODUCTS
        # ====================================================

        if (
            "top 3 products" in q
            or "top three products" in q
            or "best 3 products" in q
            or "best three products" in q
            or "top three product" in q
            or "top 3 product" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a product column."
                    )
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column."
                    )
                }


            ranking = (
                df.groupby(product_column)[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(3)
            )


            top_products = {}

            for product, value in ranking.items():

                top_products[str(product)] = round(
                    float(value),
                    2
                )


            chart_data = []

            for product, value in ranking.items():

                chart_data.append(
                    {
                        "category": str(product),

                        "value": round(
                            float(value),
                            2
                        )
                    }
                )


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

                    "data": chart_data
                }
            }


        # ====================================================
        # QUESTION 8
        # SALES BY PRODUCT
        # ====================================================

        if (
            "sales by product" in q
            or "show sales by product" in q
            or "sales per product" in q
            or "product sales" in q
            or "sales for each product" in q
            or "sales of each product" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a product column."
                    )
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer": (
                        "I could not find a numeric sales "
                        "column."
                    )
                }


            grouped = (
                df.groupby(product_column)[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            chart_data = []

            for product, value in grouped.items():

                chart_data.append(
                    {
                        "category": str(product),

                        "value": round(
                            float(value),
                            2
                        )
                    }
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
        # QUESTION 9
        # DATASET SUMMARY
        # ====================================================

        if (
            "dataset summary" in q
            or "data summary" in q
            or "summarize the data" in q
            or "summary of data" in q
            or q == "summary"
            or "summarize dataset" in q
            or "give me a dataset summary" in q
        ):

            numeric_columns = list(
                df.select_dtypes(
                    include="number"
                ).columns
            )


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

                "numeric_columns": [
                    str(column)
                    for column in numeric_columns
                ]
            }


        # ====================================================
        # QUESTION 10
        # SHOW ALL DATA
        # ====================================================

        if (
            "show data" in q
            or "show dataset" in q
            or "display data" in q
            or "display dataset" in q
        ):

            preview = df.head(20).fillna("").to_dict(
                orient="records"
            )


            return {

                "success": True,

                "question": question_original,

                "answer": (
                    "Here is a preview of your dataset."
                ),

                "rows": len(df),

                "preview": preview
            }


        # ====================================================
        # UNKNOWN QUESTION
        # ====================================================

        return {

            "success": False,

            "question": question_original,

            "answer": (
                "I don't understand this question yet. "
                "Try asking: "
                "'Which product sells the most?', "
                "'What is the total sales?', "
                "'What is the average sales?', "
                "'What are the maximum sales?', "
                "'What are the minimum sales?', "
                "'How many records are there?', "
                "'Show me the top 3 products', "
                "'Show me sales by product', "
                "'Show me the dataset', "
                "or 'Give me a dataset summary'."
            )
        }


    except Exception as e:

        return {

            "success": False,

            "question": question_original,

            "answer": (
                "An error occurred while analyzing "
                "your dataset."
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


        chart_data = create_chart_data(
            df,
            column,
            value_column
        )


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

                str(column):
                    str(df[column].dtype)

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