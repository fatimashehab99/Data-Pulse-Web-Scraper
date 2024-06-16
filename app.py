from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from google.cloud import storage
import Functions.data_collector_functions as data_collector

app = Flask(__name__)


@app.route('/collect')
def collectData():
    global response
    url = (request.get_json())["url"]
    # throw an exception incase the url not found
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # get post title and post tags
        post_title = (data_collector.getPostTitle(soup))["post_title"]
        post_tags = (data_collector.getPostTitle(soup))["post_tags"]

        # get post type
        post_type = data_collector.getPostType(soup)
        # the post type must be a product
        if post_type != "product":
            return jsonify({'error': 'The post type must be of type product'}), 400

        # get domain
        domain = data_collector.getDomain(soup)

        # get description
        description = data_collector.getPostDescription(soup)

        # get post image
        post_image = data_collector.getPostImage(soup)

        # get post currency
        post_currency = data_collector.getPostCurrency(soup)

        # get post price
        post_price = data_collector.getPostPrice(soup)

        # get post vendor
        post_vendor = data_collector.getPostVendor(soup)

        return {
            "post_title": post_title,
            "post_tags": post_tags,
            "post_url": url,
            "post_type": post_type,
            "domain": domain,
            "description": description,
            "post_image": post_image,
            "post_currency": post_currency,
            "post_price": post_price,
            "post_vendor": post_vendor
        }
    # exception incase the url is wrong or any http errors
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), response.status_code
    except requests.exceptions.ConnectionError as conn_err:
        return jsonify({'error': f'Connection error occurred: {conn_err}'}), 500
    except requests.exceptions.Timeout as timeout_err:
        return jsonify({'error': f'Timeout error occurred: {timeout_err}'}), 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Invalid URL or request error occurred: {req_err}'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
