import os
import torch
from minigpt4.models import MiniGPT4


# Step 1: Load the MiniGPT-4 model
def load_model():
    try:
        # Use GPU if available, otherwise fallback to CPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the MiniGPT-4 model using checkpoint and config paths
        model = MiniGPT4.load_from_checkpoint(
            checkpoint_path="/Users/makalliwa/Documents/MiniGPT-4/Checkpoints/pretrained_minigpt4_7b.pth",
            config_path="/Users/makalliwa/Documents/MiniGPT-4/Weights/config.json"
        )
        # Set model to evaluation mode
        model.to(device)
        model.eval()
        return model, device
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

# Step 2: Get a list of photos in the directory
def get_photos(directory):
    # Only look for files with these extensions
    supported_formats = ('.jpg', '.jpeg', '.png')
    # Return a list of full paths to files with supported formats
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith(supported_formats)]

# Step 3: Ask ODD questions for a single photo
def process_photo(model, photo_path, questions, device):
    responses = []  # To store "Yes" or "No" answers
    for question in questions:
        # Prepare a prompt that includes the photo path and question
        prompt = f"Given this photo: {photo_path}, {question} Respond with only 'Yes' or 'No'."
        try:
            # Create input for the model
            inputs = {"text": prompt}

            # Generate a response from the model
            with torch.no_grad():
                response = model.generate_text(inputs)

            # Process the response to ensure it's either "Yes" or "No"
            response = response.strip().lower()
            if "yes" in response:
                responses.append("Yes")
            elif "no" in response:
                responses.append("No")
            else:
                responses.append("No")  # Default to "No" if unclear
        except Exception as e:
            print(f"Error processing photo {photo_path}: {e}")
            responses.append("No")  # Default to "No" for errors
    return responses

# Step 4: Check compliance for each photo
def check_compliance(photo_responses):
    compliance = {}  # To store compliance status for each photo
    for photo, answers in photo_responses.items():
        # If all answers are "Yes," mark as compliant; otherwise, non-compliant
        if all(answer == "Yes" for answer in answers):
            compliance[os.path.basename(photo)] = "compliant"
        else:
            compliance[os.path.basename(photo)] = "non-compliant"
    return compliance

# Step 5: Process all photos in the directory
def process_photos_in_directory(model, photo_directory, questions, device):
    photo_responses = {}  # To store yes/no responses for each photo
    photos = get_photos(photo_directory)  # Get all photos from the directory
    if not photos:
        print(f"No photos found in directory: {photo_directory}")
        return photo_responses

    # Process each photo
    for photo in photos:
        print(f"Processing photo: {photo}")
        photo_responses[photo] = process_photo(model, photo, questions, device)
    return photo_responses

# Main logic
if __name__ == "__main__":
    # List of ODD questions
    odd_questions = [
        "1. Does this image have poor visibility (e.g., heavy rain, snow, fog)?",
        "2. Is the camera obstructed (e.g., by mud, ice, snow)?",
        "3. Is the road in this image a sharp curve?",
        "4. Is the road in this image an on-off ramp?",
        "5. Is the road in this image an intersection?",
        "6. Does the road in this image have restricted lanes?",
        "7. Does the road in this image have construction zones?",
        "8. Is the road in this image highly banked?",
        "9. Is the image affected by bright light (e.g., headlights, sunlight)?",
        "10. Is the road in this image narrow or winding?",
        "11. Is the road in this image on a hill?"
    ]

    # Path to the directory containing photos
    photo_directory = "/Users/makalliwa/Documents/OM_ODD_diLLMma/3_TestData"

    # Step 1: Load the model
    model, device = load_model()
    if model is None:
        print("Failed to load the model. Exiting.")
    else:
        # Step 2: Process photos and get yes/no responses
        photo_responses = process_photos_in_directory(model, photo_directory, odd_questions, device)

        # Step 3: Check compliance for each photo
        compliance_report = check_compliance(photo_responses)

        # Step 4: Print the compliance report
        print("\nCompliance Report:")
        for photo, status in compliance_report.items():
            print(f"{photo}: {status}")

        # Step 5: Save the report to a file
        import json

        with open("compliance_report.json", "w") as file:
            json.dump(compliance_report, file, indent=4)
        print("\nCompliance report saved to 'compliance_report.json'")
