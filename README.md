# Amazon Home Products Customer Reviews API

If you sell consumer home products and you are looking for an API to support your web site, business dashboard, or research, this API is for you!

Here's a link to the dataset data dictionary that also includes the S3 links for all the customer review datasets.

[Data Dictionary](https://s3.amazonaws.com/amazon-reviews-pds/tsv/index.txt)

## Requirements
* Git
* Docker
* Docker-compose

## Installation
1. Open your terminal
2. Clone the repo `git clone git:shumakriss/dataset-to-api.git`
3. Change directories `cd dataset-to-api`
4. Launch the Docker containers `docker-compose up --build`
5. Open your browser
6. Hit the test URL: [http://localhost:8081/health](http://localhost:8081/health)
7. You should get a message `"Server is running"`
8. Try the rest of the API!

## API
See below for the list of endpoints in this API. All responses formatted as JSON.

### List Products
Method: `GET` <br>
Returns: A paged list of products as lists \[product_id, product_parent, product_title, product_category\]<br>
Endpoint: `/products`<br>
Example: `http://localhost:8081/products?keyword=Roomba`<br>
Example: `http://localhost:8081/products?page=0&page-size=100`<br>
Query Parameters:
* keyword: Wildcard match on titles
* page-size: Limits the size of the list, capped at 100
* page: The page index to retrieve

### Reviews by Product
Method: `GET` <br>
Returns: A list of all the reviews for a specific product ID<br>
Endpoint: `/reviews/<product_id>`<br>
Example: `http://localhost:8081/reviews/B00EE62UAE`<br>

### Health
Method: `GET` <br>
Returns: 200 when server is available<br>
Endpoint: `/health`<br>
Example: `http://localhost:8081/health`<br>

## Internal Details

This project was built with the purpose of serving a useful API based on customer review data.

Some notable technical decisions:
* Use of Docker and Docker-compose for reproducibility
* Use of Python for rapid application development
* Use of batch-style processing given a static dataset rather than a live source

Notable Python libraries include:
* Boto3 - For Amazon S3
* psycopg2 - For Postgres
* Flask - For web services

### Considerations

#### Maintainability
The project is structured with a docker-compose.yml and two subprojects, processor and web each with its own Dockerfile.
Usage of infrastructure as code serves to improve reproducibility and to make deployment less dependent on environment.
 
#### User Experience
Processing is done as expediently as possible to limit user waiting while application loads. Reviews are committed 
periodically so that they may be queried while the data is loading. The API should be well-documented and intuitive.

#### Security (API key management)
Secrets may be provided via docker-compose and are not hardcoded (except certain defaults which should not be used in
production). This could vary greatly depending on your organization, as you may have Docker secrets management or some
other secrets management approach. Another major point of variation is authentication for the API which depends on your
API token management system and user directories.

#### Documentation (End user and internal)
This guide should provide both API documentation and architectural insights.

#### Error handling
The code is generally organized to fail quickly. For example, a database health is done prior to major data operations
to prevent wasting user time.

#### Testability
Some tests are included along with instructions to manually execute the scripts outside of Docker as well as to attach 
a database tool if necessary. Health check endpoints and API usage also serve as manual test points.

#### Processing approach (streaming, batch processing, etc.)
Batch-style processing is used due to the static nature of the dataset. A live, continuous data source would be better
suited to a streaming approach.

### Development

Additional Requirements
* Python 3 & pip

#### Instructions
1. Open your terminal
2. Clone the repo `git clone git:shumakriss/dataset-to-api.git`
3. Change directories to 'processor' folder `cd dataset-to-api/processor`
4. Install dependencies `pip3 install --no-cache-dir -r requirements.txt`
5. Change directories to 'web' folder `cd ../web`
6. Install dependencies `pip3 install --no-cache-dir -r requirements.txt`
7. Change to parent directory `cd ..`
8. Launch the containers

You may also run the processor.py ad web.py scripts in each corresponding folder to debug outside of Docker.

#### Data Model
The data model in Postgres is based on the [Data Dictionary](https://s3.amazonaws.com/amazon-reviews-pds/tsv/index.txt).

>marketplace       - 2 letter country code of the marketplace where the review was written.<br>
>customer_id       - Random identifier that can be used to aggregate reviews written by a single author.<br>
>review_id         - The unique ID of the review.<br>
>product_id        - The unique Product ID the review pertains to. In the multilingual dataset the reviews
                    for the same product in different countries can be grouped by the same product_id.<br>
>product_parent    - Random identifier that can be used to aggregate reviews for the same product.<br>
>product_title     - Title of the product.<br>
>product_category  - Broad product category that can be used to group reviews 
                    (also used to group the dataset into coherent parts).<br>
>star_rating       - The 1-5 star rating of the review.<br>
>helpful_votes     - Number of helpful votes.<br>
>total_votes       - Number of total votes the review received.<br>
>vine              - Review was written as part of the Vine program.<br>
>verified_purchase - The review is on a verified purchase.<br>
>review_headline   - The title of the review.<br>
>review_body       - The review text.<br>
>review_date       - The date the review was written.<br>

#### Working with the database
If you want to work directly with the database, you can run pgAdmin. Be careful
 not to expose your database or credentials in production. For development purposes, add a pgAdmin container to your 
 docker-compose.yml like so:

```db-browser:
image: dpage/pgadmin4
environment:
  - PGADMIN_DEFAULT_EMAIL=user@domain.com
  - PGADMIN_DEFAULT_PASSWORD=SuperSecret
ports:
  - "80:80"
```

### Possible Improvements & Features
* Integrate a more complete stack (API Gateway, user management, secrets management, etc.)
* Supplement data (average star rating, rating histograms, top customers, etc.)
* Further automated testing
* Performance profiling & tuning
* Additional product category datasets