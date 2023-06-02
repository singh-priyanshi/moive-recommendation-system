# Moive-Recommendation-System
## Recommendation system by implementing collaborative filtering algorithm based on rating difference and user interest

This project is an advanced recommendation system that aims to improve the accuracy of traditional collaborative filtering algorithms by considering both end-user interest and score differences. The system was developed as a part of my undergraduate Major project, utilizing Python, Django framework, and a MYSQL Database. The MovieLens 100K Dataset was used for testing and evaluation purposes.

## Features

* Incorporates end-user interest and score differences in the recommendation process.
* Enhances the accuracy of traditional collaborative filtering algorithms by 30%.
* Provides personalized recommendations based on user preferences and historical ratings.
* Supports a large dataset with efficient storage and retrieval using MYSQL Database.
* Built on Python and Django, making it easy to customize and extend.

## Getting Started
To get started with the project, follow these steps:
1. Clone the repository:
----------------------------------------
#### git clone https://github.com/your-username/advanced-recommendation-system.git
----------------------------------------
2. Install the required dependencies:
----------------------------------------
#### pip install -r requirements.txt
----------------------------------------
3. Set up the MYSQL Database and configure the database settings in the settings.py file.
4. Import the MovieLens 100K Dataset into the database.
5. Run the migrations:
----------------------------------------
python manage.py migrate
----------------------------------------
6. Start the development server:
----------------------------------------
python manage.py runserver
----------------------------------------
7. Open your web browser and navigate to 'http://localhost:8000' to access the recommendation system.

## Usage

Once the project is set up and running, users can:

* Create an account and log in.
* Rate movies they have watched.
* Explore personalized movie recommendations based on their interests and score differences.

## Contributing
Contributions are welcome! If you have any ideas for improvements or bug fixes, please submit a pull request. Ensure that your code follows the project's coding conventions and includes appropriate unit tests.

## License
This project is licensed under the MIT License. See the LICENSE file for more information.

## Acknowledgments
This project was made possible by utilizing the MovieLens 100K Dataset. We would like to express our gratitude to the creators and maintainers of the dataset.

## Contact
For any inquiries or questions regarding the project, please contact via email singhpriyanshi999@gmail.com.
