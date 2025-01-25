# NoClueAstronomy

**NoClueAstronomy** is a Streamlit-based web application that provides users with insights and educational resources about astronomy. With features like NASA's Astronomy Picture of the Day (APOD) and a glossary of astronomy-related terms, this app aims to make learning about space both engaging and accessible.

---

## Features

1. **APOD Page**
   - Displays the Astronomy Picture of the Day (APOD) using NASA's API.
   - Includes detailed explanations of the image or video of the day.

2. **Glossary Page**
   - Provides definitions and explanations of common astronomy terms.
   - Useful for beginners and enthusiasts alike.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+**
- **Docker** and **Docker Compose** (for containerized deployment)
- **pip** (Python package manager)

---

## Installation and Usage

### Option 1: Using Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/modernn/NoClueAstronomy.git
   cd NoClueAstronomy
   ```

2. **Run the application with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Open your browser and navigate to `http://localhost:8501`.

4. **Stop the application**:
   - Use `Ctrl+C` to stop the application.
   - Run `docker-compose down` to clean up the containers.

### Option 2: Running Streamlit Independently

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/modernn/NoClueAstronomy.git
   cd NoClueAstronomy
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r .\webapp\requirements.txt
   ```

3. **Run the application**:
   ```powershell
   streamlit run .\webapp\app.py
   ```

4. **Access the application**:
   - Open your browser and navigate to the URL displayed in the terminal (e.g., `http://localhost:8501`).

---

## Project Structure

```
NoClueAstronomy/
├── docker-compose.yml      # Defines services for running the app using Docker
├── ReadMe.md               # Project documentation (this file)
└── webapp/
    ├── app.py              # Main application file for Streamlit
    ├── dockerfile          # Dockerfile for containerizing the webapp
    ├── pages/              # Contains additional pages for the app
    │   ├── apod.py         # APOD feature implementation
    │   └── glossary.py     # Glossary feature implementation
    └── requirements.txt    # Python dependencies for the project
```

---

## API Keys

The application may require an API key for certain features (e.g., NASA APOD API). Set your API keys as environment variables or modify the code in `app.py` to include your key:

```python
NASA_API_KEY = "your_api_key_here"
```

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- NASA's Astronomy Picture of the Day (APOD) API
- [Streamlit](https://streamlit.io/) for providing an easy-to-use framework for building data apps.

