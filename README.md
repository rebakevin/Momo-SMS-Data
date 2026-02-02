# MoMo SMS Data

This is a simple MoMo simulation app built in pure Python

## Documentation
- The API endpoints are documented in `docs/api_docs.md`
- Screenshots for testing the endpoints are in `screenshots` directory

## Other documents 
- [Database_Design_Document_Cohort1_Team2](docs/Database_Design_Document_Cohort1_Team2.pdf)
- [PDF Report](docs/Building-and-Securing-a-REST_API_Group3-Cohort1_Report.pdf)
- [Team participation sheet](https://docs.google.com/spreadsheets/d/1NCB-1ds53lkJXSDRUqGpbYZV42F7CvnEn9rMcusWH8g/edit?usp=sharing)

## Features
- Basic CRUD endpoints
  - Create transactions
  - Get all transactions
  - Get transaction by id
  - Delete transaction
  - Update transasction
- Basic auth
- A python script to transform `xml` data to `JSON`
- OpenAPI / Swagger documentation

## How to run the app
- Clone the app `https://github.com/rebakevin/Momo-SMS-Data.git`
- Install the dependencies `pip install -r requirements.txt`
- Run `python main.py` to start the server at `http://localhost:8000`
- The documentation will be at `http://localhost:8000/api-docs`

