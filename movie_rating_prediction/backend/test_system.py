import unittest
from fastapi.testclient import TestClient
from app import app

class TestMovieRatingAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "API is running"})

    def test_predict_endpoint(self):
        payload = {
            "genres": ["Drama", "Thriller"],
            "director": "Christopher Nolan",
            "actors": ["Leonardo DiCaprio", "Tom Hardy"],
            "runtime": 148,
            "release_year": 2024,
            "vote_count": 50000
        }
        response = self.client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("predicted_rating", response.json())
        self.assertIn("confidence_range", response.json())
        self.assertIn("top_influencing_features", response.json())

    def test_upload_dataset(self):
        with open("../data/processed_dataset.csv", "rb") as file:
            response = self.client.post("/upload-dataset", files={"file": file})
            self.assertEqual(response.status_code, 200)
            self.assertIn("detail", response.json())

if __name__ == "__main__":
    unittest.main()