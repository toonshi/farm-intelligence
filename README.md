# Mshamba Intelligence API

This is the backend API for the Mshamba Intelligence platform. It provides endpoints for managing farms, farmers, crops, and seasons, as well as for getting farm valuations, crop recommendations, and yield predictions.

## Features

- **Farm Management:** Create, read, update, and delete farms and farmers.
- **Crop and Season Management:** Create, read, update, and delete crops and seasons.
- **Farm Valuation:** Get a simple valuation of a farm based on its historical profit, or a more sophisticated valuation using a Discounted Cash Flow (DCF) model.
- **Crop Recommendations:** Get simple crop recommendations based on the most profitable crop in a farm's history, or advanced recommendations based on the risk-adjusted return (Sharpe Ratio) of each crop.
- **Yield Prediction:** Predict the yield of a crop given a set of inputs, using a machine learning model.

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**

    - Make sure you have PostgreSQL installed and running.
    - Create a new PostgreSQL database.
    - Create a `.env` file in the root of the project and add the following line, replacing the placeholders with your database credentials:

      ```
      DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
      ```

5.  **Run the database migrations and load the initial data:**

    ```bash
    python -m scripts.load_data
    ```

### Running the Application

To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Crops

-   `GET /crops/`: Get a list of all crops.
-   `POST /crops/predict_yield`: Predict the yield of a crop.

### Farms

-   `POST /farms/`: Create a new farm.
-   `GET /farms/{farm_id}/valuation`: Get a simple valuation of a farm.
-   `GET /farms/{farm_id}/dcf_valuation`: Get a DCF valuation of a farm.
-   `GET /farms/{farm_id}/recommendations`: Get simple crop recommendations for a farm.
-   `GET /farms/{farm_id}/advanced_recommendations`: Get advanced crop recommendations for a farm.

### Farmers

-   `POST /farmers/`: Create a new farmer.

### Seasons

-   `POST /seasons/`: Create a new season.
