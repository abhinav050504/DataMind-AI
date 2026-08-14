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
        "value",
        "Total Sales",
        "total_sales"
    ]

    for column in possible_columns:

        if column in df.columns:

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):

                return column

    # Automatic fallback:
    # Find the first numeric column if no common
    # sales column name exists.

    numeric_columns = list(
        df.select_dtypes(
            include="number"
        ).columns
    )

    if numeric_columns:

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
        "Item",
        "item",
        "Category",
        "category",
        "ProductName",
        "productname"
    ]

    for column in possible_columns:

        if column in df.columns:

            return column

    # Automatic fallback:
    # Find a text column with relatively few unique values.

    object_columns = list(
        df.select_dtypes(
            include=["object", "string"]
        ).columns
    )

    for column in object_columns:

        if df[column].nunique() <= max(
            50,
            len(df) * 0.5
        ):

            return column

    return None


# ============================================================
# CLEAN NUMERIC SALES DATA
# ============================================================

def clean_sales_column(df, sales_column):

    if not sales_column:
        return df

    df[sales_column] = pd.to_numeric(
        df[sales_column],
        errors="coerce"
    )

    return df


# ============================================================
# CREATE PRODUCT ANALYSIS
# ============================================================

def create_product_analysis(df, product_column, sales_column):

    if not product_column or not sales_column:

        return {
            "ranking": {},
            "chart": [],
            "best_product": None,
            "best_value": None,
            "worst_product": None,
            "worst_value": None,
            "best_percentage": 0
        }

    valid_df = df[
        df[product_column].notna()
        & df[sales_column].notna()
    ].copy()

    if valid_df.empty:

        return {
            "ranking": {},
            "chart": [],
            "best_product": None,
            "best_value": None,
            "worst_product": None,
            "worst_value": None,
            "best_percentage": 0
        }

    ranking = (
        valid_df
        .groupby(product_column)[sales_column]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    ranking_data = {}

    chart_data = []

    for product, value in ranking.items():

        product_name = str(product)
        numeric_value = float(value)

        ranking_data[product_name] = round(
            numeric_value,
            2
        )

        chart_data.append(
            {
                "category": product_name,
                "value": round(
                    numeric_value,
                    2
                )
            }
        )

    best_product = str(
        ranking.index[0]
    )

    best_value = float(
        ranking.iloc[0]
    )

    worst_product = str(
        ranking.index[-1]
    )

    worst_value = float(
        ranking.iloc[-1]
    )

    total_sales = float(
        ranking.sum()
    )

    if total_sales != 0:

        best_percentage = (
            best_value /
            total_sales
        ) * 100

    else:

        best_percentage = 0

    return {

        "ranking": ranking_data,

        "chart": chart_data,

        "best_product": best_product,

        "best_value": round(
            best_value,
            2
        ),

        "worst_product": worst_product,

        "worst_value": round(
            worst_value,
            2
        ),

        "best_percentage": round(
            best_percentage,
            2
        )
    }


# ============================================================
# DASHBOARD ANALYSIS
# ============================================================

def analyze_dataset(df):

    # --------------------------------------------------------
    # BASIC INFORMATION
    # --------------------------------------------------------

    rows = len(df)

    columns = len(df.columns)

    column_names = [
        str(column)
        for column in df.columns
    ]


    # --------------------------------------------------------
    # FIND SALES + PRODUCT
    # --------------------------------------------------------

    sales_column = find_sales_column(df)

    product_column = find_product_column(df)


    # --------------------------------------------------------
    # CLEAN SALES
    # --------------------------------------------------------

    df = clean_sales_column(
        df,
        sales_column
    )


    # --------------------------------------------------------
    # SALES KPI
    # --------------------------------------------------------

    total_sales = 0

    average_sales = 0

    maximum_sales = 0

    minimum_sales = 0

    valid_sales_count = 0


    if sales_column:

        sales_data = df[
            sales_column
        ].dropna()

        valid_sales_count = len(
            sales_data
        )

        if not sales_data.empty:

            total_sales = float(
                sales_data.sum()
            )

            average_sales = float(
                sales_data.mean()
            )

            maximum_sales = float(
                sales_data.max()
            )

            minimum_sales = float(
                sales_data.min()
            )


    # --------------------------------------------------------
    # PRODUCT ANALYSIS
    # --------------------------------------------------------

    product_analysis = (
        create_product_analysis(
            df,
            product_column,
            sales_column
        )
    )


    # --------------------------------------------------------
    # DATA TYPES
    # --------------------------------------------------------

    data_types = {

        str(column):
            str(df[column].dtype)

        for column in df.columns

    }


    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    missing_values = {

        str(column):
            int(
                df[column].isna().sum()
            )

        for column in df.columns

    }


    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )


    # --------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------

    preview_df = df.head(10).copy()

    preview_df = preview_df.fillna("")

    preview = []

    for _, row in preview_df.iterrows():

        row_data = {}

        for column in df.columns:

            value = row[column]

            if hasattr(value, "item"):

                try:
                    value = value.item()
                except Exception:
                    pass

            row_data[str(column)] = str(
                value
            )

        preview.append(
            row_data
        )


    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [

        str(column)

        for column in
        df.select_dtypes(
            include="number"
        ).columns

    ]


    # --------------------------------------------------------
    # SMART INSIGHTS
    # --------------------------------------------------------

    insights = []


    if product_analysis["best_product"]:

        insights.append(
            f"Best-selling product: "
            f"{product_analysis['best_product']} "
            f"with {product_analysis['best_value']:.2f} "
            f"{sales_column}."
        )


    if product_analysis["worst_product"]:

        insights.append(
            f"Worst-performing product: "
            f"{product_analysis['worst_product']} "
            f"with {product_analysis['worst_value']:.2f} "
            f"{sales_column}."
        )


    if product_analysis["best_product"]:

        insights.append(
            f"The best-selling product contributes "
            f"{product_analysis['best_percentage']:.2f}% "
            f"of total product sales."
        )


    if duplicate_rows > 0:

        insights.append(
            f"The dataset contains "
            f"{duplicate_rows} duplicate rows."
        )

    else:

        insights.append(
            "No duplicate rows were detected."
        )


    missing_count = sum(
        missing_values.values()
    )


    if missing_count > 0:

        insights.append(
            f"The dataset contains "
            f"{missing_count} missing values."
        )

    else:

        insights.append(
            "No missing values were detected."
        )


    # --------------------------------------------------------
    # RETURN COMPLETE DASHBOARD
    # --------------------------------------------------------

    return {

        "success": True,

        "rows": rows,

        "columns": columns,

        "column_names": column_names,

        "sales_column": sales_column,

        "product_column": product_column,

        "total_sales": round(
            total_sales,
            2
        ),

        "average_sales": round(
            average_sales,
            2
        ),

        "maximum_sales": round(
            maximum_sales,
            2
        ),

        "minimum_sales": round(
            minimum_sales,
            2
        ),

        "valid_sales_records":
            valid_sales_count,

        "best_product":
            product_analysis[
                "best_product"
            ],

        "best_product_sales":
            product_analysis[
                "best_value"
            ],

        "worst_product":
            product_analysis[
                "worst_product"
            ],

        "worst_product_sales":
            product_analysis[
                "worst_value"
            ],

        "best_product_percentage":
            product_analysis[
                "best_percentage"
            ],

        "ranking":
            product_analysis[
                "ranking"
            ],

        "chart": {

            "chart_type": "bar",

            "title": (
                f"{sales_column} by "
                f"{product_column}"
                if sales_column
                and product_column
                else "Sales by Product"
            ),

            "x_axis":
                product_column,

            "y_axis":
                sales_column,

            "data":
                product_analysis[
                    "chart"
                ]
        },

        "preview": preview,

        "data_types": data_types,

        "missing_values":
            missing_values,

        "duplicate_rows":
            duplicate_rows,

        "numeric_columns":
            numeric_columns,

        "insights":
            insights
    }


# ============================================================
# DASHBOARD ENDPOINT
# ============================================================

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".csv"):

        return {

            "success": False,

            "answer":
                "Please upload a CSV file."

        }


    try:

        df = await read_csv(file)

        return analyze_dataset(df)


    except Exception as e:

        return {

            "success": False,

            "answer":
                "An error occurred while "
                "analyzing your dataset.",

            "error":
                str(e)

        }


# ============================================================
# ASK DATA
# ============================================================

@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):

    if not file.filename.lower().endswith(".csv"):

        return {

            "success": False,

            "answer":
                "Please upload a CSV file."

        }


    try:

        df = await read_csv(file)

        question_original = (
            question.strip()
        )

        q = question_original.lower()

        sales_column = find_sales_column(df)

        product_column = find_product_column(df)

        df = clean_sales_column(
            df,
            sales_column
        )


        # ====================================================
        # BEST PRODUCT
        # ====================================================

        if (
            "sells most" in q
            or "sell most" in q
            or "best selling" in q
            or "best-selling" in q
            or "top product" in q
            or "highest selling" in q
            or "most popular" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a product "
                        "column in your dataset."
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            analysis = create_product_analysis(
                df,
                product_column,
                sales_column
            )


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"{analysis['best_product']} "
                    f"is the best-selling product "
                    f"with "
                    f"{analysis['best_value']:.2f} "
                    f"{sales_column}."
                ),

                "product_column":
                    product_column,

                "sales_column":
                    sales_column,

                "ranking":
                    analysis["ranking"],

                "chart": {

                    "chart_type": "bar",

                    "title":
                        f"{sales_column} by "
                        f"{product_column}",

                    "x_axis":
                        product_column,

                    "y_axis":
                        sales_column,

                    "data":
                        analysis["chart"]

                }

            }


        # ====================================================
        # TOTAL SALES
        # ====================================================

        if (
            "total sales" in q
            or "total sale" in q
            or "sum of sales" in q
            or "sales total" in q
            or "how much sales" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            total = df[
                sales_column
            ].sum()


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"The total "
                    f"{sales_column.lower()} "
                    f"is {total:.2f}."
                ),

                "sales_column":
                    sales_column,

                "total":
                    round(
                        float(total),
                        2
                    )

            }


        # ====================================================
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
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            average = df[
                sales_column
            ].mean()


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"The average "
                    f"{sales_column.lower()} "
                    f"is {average:.2f}."
                ),

                "sales_column":
                    sales_column,

                "average":
                    round(
                        float(average),
                        2
                    )

            }


        # ====================================================
        # MAXIMUM SALES
        # ====================================================

        if (
            "maximum sales" in q
            or "max sales" in q
            or "highest sales" in q
            or "highest sale" in q
            or "maximum sale" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            maximum = df[
                sales_column
            ].max()


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"The highest "
                    f"{sales_column.lower()} "
                    f"is {maximum:.2f}."
                ),

                "sales_column":
                    sales_column,

                "maximum":
                    round(
                        float(maximum),
                        2
                    )

            }


        # ====================================================
        # MINIMUM SALES
        # ====================================================

        if (
            "minimum sales" in q
            or "min sales" in q
            or "lowest sales" in q
            or "lowest sale" in q
            or "minimum sale" in q
        ):

            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            minimum = df[
                sales_column
            ].min()


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"The lowest "
                    f"{sales_column.lower()} "
                    f"is {minimum:.2f}."
                ),

                "sales_column":
                    sales_column,

                "minimum":
                    round(
                        float(minimum),
                        2
                    )

            }


        # ====================================================
        # NUMBER OF RECORDS
        # ====================================================

        if (
            "number of records" in q
            or "number of rows" in q
            or "how many records" in q
            or "how many rows" in q
            or "count records" in q
        ):

            count = len(df)


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"Your dataset contains "
                    f"{count} records."
                ),

                "records":
                    count

            }


        # ====================================================
        # TOP 3 PRODUCTS
        # ====================================================

        if (
            "top 3 products" in q
            or "top three products" in q
            or "best 3 products" in q
            or "best three products" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a product "
                        "column."
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            ranking = (
                df.groupby(
                    product_column
                )[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(3)
            )


            top_products = {}

            for product, value in ranking.items():

                top_products[
                    str(product)
                ] = round(
                    float(value),
                    2
                )


            return {

                "success": True,

                "question":
                    question_original,

                "answer":
                    "Here are the top 3 "
                    "best-selling products.",

                "ranking":
                    top_products

            }


        # ====================================================
        # SALES BY PRODUCT
        # ====================================================

        if (
            "sales by product" in q
            or "show sales by product" in q
            or "sales per product" in q
            or "product sales" in q
        ):

            if not product_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a product "
                        "column."
                }


            if not sales_column:

                return {
                    "success": False,
                    "answer":
                        "I could not find a numeric "
                        "sales column."
                }


            analysis = create_product_analysis(
                df,
                product_column,
                sales_column
            )


            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"Here is the "
                    f"{sales_column.lower()} "
                    f"breakdown by "
                    f"{product_column.lower()}."
                ),

                "chart": {

                    "chart_type":
                        "bar",

                    "title":
                        f"{sales_column} by "
                        f"{product_column}",

                    "x_axis":
                        product_column,

                    "y_axis":
                        sales_column,

                    "data":
                        analysis["chart"]

                }

            }


        # ====================================================
        # DATASET SUMMARY
        # ====================================================

        if (
            "dataset summary" in q
            or "data summary" in q
            or "summarize the data" in q
            or "summary of data" in q
            or q == "summary"
        ):

            return {

                "success": True,

                "question":
                    question_original,

                "answer": (
                    f"Your dataset has "
                    f"{len(df)} rows and "
                    f"{len(df.columns)} columns."
                ),

                "rows":
                    len(df),

                "columns":
                    len(df.columns),

                "column_names": [
                    str(column)
                    for column in df.columns
                ]

            }


        # ====================================================
        # UNKNOWN QUESTION
        # ====================================================

        return {

            "success": False,

            "question":
                question_original,

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
                "or 'Give me a dataset summary'."
            )

        }


    except Exception as e:

        return {

            "success": False,

            "question":
                question_original,

            "answer":
                "An error occurred while analyzing "
                "your dataset.",

            "error":
                str(e)

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

            "error":
                "Please upload a CSV file."

        }


    try:

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )


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

                "error":
                    f"'{value_column}' must be "
                    f"a numeric column."

            }


        grouped = (
            df.groupby(column)[value_column]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        chart_data = []

        for category, value in grouped.items():

            chart_data.append(
                {

                    "category":
                        str(category),

                    "value":
                        round(
                            float(value),
                            2
                        )

                }
            )


        return {

            "success": True,

            "chart_type":
                "bar",

            "title":
                f"{value_column} by {column}",

            "x_axis":
                column,

            "y_axis":
                value_column,

            "data":
                chart_data

        }


    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)

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

            "error":
                "Please upload a CSV file."

        }


    try:

        df = await read_csv(file)

        return {

            "success": True,

            "rows":
                len(df),

            "columns":
                len(df.columns),

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
                    int(
                        df[column].isna().sum()
                    )

                for column in df.columns

            }

        }


    except Exception as e:

        return {

            "success": False,

            "error":
                str(e)

        }