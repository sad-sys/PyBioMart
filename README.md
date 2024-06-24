## README for BioMart Python Module

### Overview
This Python module provides functionality to interact with the BioMart service, specifically focusing on Ensembl marts. It allows users to list available marts, check the validity of Mart objects, and make HTTP requests to the BioMart web service.

### Installation
To use this module, you need to have the following Python packages installed:
- `requests`
- `lxml`

You can install these packages using pip:
```bash
pip install requests lxml
```

### Usage

#### Mart Class
The `Mart` class is a custom class to store relevant information about a BioMart dataset.
