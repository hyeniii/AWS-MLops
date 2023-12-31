# Property Price Predictor & Description Generator
 Web application to estimate rental prices based on property descriptions. Optimizes your listings with AI-generated summaries tailored for platforms like Zillow. We utilize scalable, event-driven architecture to train, infer, retrain our ML model using AWS serverless compute services.

## Pipeline diagram:
![MLops_flow](deliverables/Rental_price_predictor.png)

## Data Source:
https://archive.ics.uci.edu/dataset/555/apartment+for+rent+classified

## Lambda:

1. create deployment package with dependencies
```bash
cd .venv/lib/python{version}/site-packages
zip -r9 ${OLDPWD}/my-deployment-package.zip .
```
2. add lambda handler and other files to zip
```
zip -g my-deployment-package.zip my_lambda_function.py
```

## Contributors:
Hye Won Hwang (hyeniii)
Sharika Mahadevan (sharika95m)
Alejandra Lelo De Larrea Ibarra (AlejandraLLI)
